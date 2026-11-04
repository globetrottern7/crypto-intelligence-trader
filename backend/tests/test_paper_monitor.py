from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import MarketCandle, PaperAccount, PaperTrade
from app.paper import monitor


def test_monitor_triggers_stop_when_candle_low_crosses_stop(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(monitor, "SessionLocal", factory)
    now = datetime.now(UTC)
    with factory() as session:
        session.add(PaperAccount(
            id="primary", initial_cash=Decimal(1000), cash=Decimal(899),
            realised_pnl=Decimal(0),
        ))
        session.add(PaperTrade(
            account_id="primary", symbol="BTC/INR", quantity=Decimal(1),
            entry_price=Decimal(100), entry_fee=Decimal(1),
            stop_loss=Decimal(95), status="open",
        ))
        session.add(MarketCandle(
            venue="test", symbol="BTC/INR", interval="1m",
            open_time=now - timedelta(minutes=1), close_time=now,
            open=Decimal(96), high=Decimal(97), low=Decimal(94), close=Decimal(96),
            volume=Decimal(2), is_closed=True,
        ))
        session.commit()
    try:
        assert monitor.run_once() == 1
        with factory() as session:
            trade = session.get(PaperTrade, 1)
            account = session.get(PaperAccount, "primary")
            assert trade.status == "closed"
            assert trade.exit_price < Decimal(95)
            assert account.realised_pnl < Decimal(0)
    finally:
        engine.dispose()


def test_monitor_ignores_stale_candles(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(monitor, "SessionLocal", factory)
    old = datetime.now(UTC) - timedelta(hours=1)
    with factory() as session:
        session.add(PaperAccount(
            id="primary", initial_cash=Decimal(1000), cash=Decimal(899),
            realised_pnl=Decimal(0),
        ))
        session.add(PaperTrade(
            account_id="primary", symbol="BTC/INR", quantity=Decimal(1),
            entry_price=Decimal(100), entry_fee=Decimal(1),
            stop_loss=Decimal(95), status="open",
        ))
        session.add(MarketCandle(
            venue="test", symbol="BTC/INR", interval="1m",
            open_time=old - timedelta(minutes=1), close_time=old,
            open=Decimal(96), high=Decimal(97), low=Decimal(94), close=Decimal(94),
            volume=Decimal(2), is_closed=True,
        ))
        session.commit()
    try:
        assert monitor.run_once() == 0
        with factory() as session:
            assert session.get(PaperTrade, 1).status == "open"
    finally:
        engine.dispose()
