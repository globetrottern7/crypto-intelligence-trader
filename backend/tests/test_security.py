from fastapi.testclient import TestClient

from app import main


def test_production_api_requires_bearer_token(monkeypatch):
    monkeypatch.setattr(main.settings, "app_env", "production")
    monkeypatch.setattr(main.settings, "api_access_token", "test-secret-token")
    client = TestClient(main.app)
    denied = client.get("/api/v1/system/status")
    allowed = client.get("/api/v1/system/status", headers={
        "Authorization": "Bearer test-secret-token"
    })
    health = client.get("/health")
    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert health.status_code == 200
    monkeypatch.setattr(main.settings, "app_env", "development")
    monkeypatch.setattr(main.settings, "api_access_token", "")
