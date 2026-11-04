from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import MarketCandle
from app.market_data.repository import store_candles
from app.market_data.schemas import CandleInterval, OHLCVCandle


def test_store_candles_is_idempotent_by_venue_pair_interval_and_open_time():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    start = datetime(2026, 1, 1, tzinfo=UTC)
    candle = OHLCVCandle(
        venue="coinswitchx", symbol="BTC/INR", interval=CandleInterval.M1,
        open_time=start, close_time=start + timedelta(minutes=1),
        open=Decimal(100), high=Decimal(105), low=Decimal(99), close=Decimal(103),
        volume=Decimal("2.5"), is_closed=True,
    )
    with Session(engine) as session:
        assert store_candles(session, [candle]) == 1
        session.commit()
        revised = candle.model_copy(update={"close": Decimal(104)})
        assert store_candles(session, [revised]) == 1
        session.commit()
        count = session.scalar(select(func.count()).select_from(MarketCandle))
        stored = session.scalar(select(MarketCandle))
        assert count == 1
        assert stored.close == Decimal(104)
