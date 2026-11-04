from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import MarketCandle
from app.main import app
from app.api.routes import market_data


def _session_factory():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)


def test_market_data_status_does_not_claim_live_data():
    response = TestClient(app).get("/api/v1/market-data/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "adapter_ready_provider_credentials_pending"
    assert body["live_ingestion_running"] is False
    assert body["live_prices_available"] is False


def test_diagnostics_reports_empty_database(monkeypatch):
    engine, factory = _session_factory()
    monkeypatch.setattr(market_data, "SessionLocal", factory)
    try:
        response = TestClient(app).get("/api/v1/market-data/diagnostics")
        assert response.status_code == 200
        assert response.json()["data_available"] is False
        assert response.json()["coverage"] == []
    finally:
        engine.dispose()


def test_diagnostics_reports_fresh_and_stale_groups(monkeypatch):
    engine, factory = _session_factory()
    monkeypatch.setattr(market_data, "SessionLocal", factory)
    now = datetime.now(UTC)
    with factory() as session:
        for symbol, close_time in (
            ("BTC/INR", now - timedelta(minutes=1)),
            ("ETH/INR", now - timedelta(hours=1)),
        ):
            session.add(MarketCandle(
                venue="coinswitch", symbol=symbol, interval="1m",
                open_time=close_time - timedelta(minutes=1), close_time=close_time,
                open=Decimal("100"), high=Decimal("101"), low=Decimal("99"),
                close=Decimal("100"), volume=Decimal("1"), is_closed=True,
            ))
        session.commit()
    try:
        response = TestClient(app).get("/api/v1/market-data/diagnostics")
        assert response.status_code == 200
        body = response.json()
        assert body["coverage_groups"] == 2
        assert body["fresh_groups"] == 1
        assert body["stale_groups"] == 1
        assert body["worker_health"] == "not_observable_from_candle_rows"
        assert body["live_prices_available"] is False
    finally:
        engine.dispose()
