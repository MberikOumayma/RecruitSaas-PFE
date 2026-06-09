import os

os.environ.setdefault("GROQ_API_KEY", "test-key-for-ci")

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
