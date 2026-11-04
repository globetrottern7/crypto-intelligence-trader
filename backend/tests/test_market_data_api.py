from fastapi.testclient import TestClient

from app.main import app


def test_market_data_status_does_not_claim_live_data():
    response = TestClient(app).get("/api/v1/market-data/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "provider_pending"
    assert body["ingestion_enabled"] is False
    assert body["live_prices_available"] is False
