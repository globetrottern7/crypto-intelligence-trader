from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_live_execution_disabled():
    payload = client.get("/api/v1/system/status").json()
    assert payload["trading_mode"] == "paper_only"
    assert payload["live_execution_enabled"] is False
