from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import MarketCandle
from app.market_data.schemas import CandleInterval, OHLCVCandle
from app.market_data.service import MarketDataIngestionService


def test_ingestion_service_persists_minutes_and_completed_aggregate():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    service = MarketDataIngestionService(factory)
    start = datetime(2026, 1, 1, tzinfo=UTC)

    for index in range(5):
        minute_start = start + timedelta(minutes=index)
        candle = OHLCVCandle(
            venue="coinswitchx", symbol="BTC/INR", interval=CandleInterval.M1,
            open_time=minute_start, close_time=minute_start + timedelta(minutes=1),
            open=Decimal(100 + index), high=Decimal(110 + index),
            low=Decimal(90 + index), close=Decimal(105 + index),
            volume=Decimal("0.5"), is_closed=True,
        )
        assert service.handle(candle, now=candle.close_time + timedelta(seconds=30))

    with factory() as session:
        rows = session.scalars(select(MarketCandle).order_by(MarketCandle.interval)).all()
        assert len(rows) == 6
        aggregate = next(row for row in rows if row.interval == "5m")
        assert aggregate.open == Decimal(100)
        assert aggregate.close == Decimal(109)
        assert aggregate.volume == Decimal("2.5")


def test_ingestion_service_drops_duplicate_and_stale_candles():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    service = MarketDataIngestionService(factory)
    start = datetime(2026, 1, 1, tzinfo=UTC)
    candle = OHLCVCandle(
        venue="coinswitchx", symbol="BTC/INR", interval=CandleInterval.M1,
        open_time=start, close_time=start + timedelta(minutes=1),
        open=Decimal(100), high=Decimal(105), low=Decimal(99), close=Decimal(103),
        volume=Decimal("0.5"), is_closed=True,
    )
    assert service.handle(candle, now=candle.close_time + timedelta(seconds=30))
    assert not service.handle(candle, now=candle.close_time + timedelta(seconds=30))
    assert not service.handle(
        candle, now=candle.close_time + timedelta(minutes=5)
    )
    assert service.stats["duplicates"] == 1
    assert service.stats["stale"] == 1
