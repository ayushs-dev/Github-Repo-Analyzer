# A "smoke test": the cheapest test that proves the app can start and answer.
# If someone breaks an import or the app setup, this fails in CI within seconds.
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
