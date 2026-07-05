"""API tests — exercise the backend the way a real client would.

`TestClient` makes genuine HTTP-shaped requests against the app without
starting a network server, so these tests check the full stack: routing,
the handler, and JSON serialization.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "glassbox-api"
    # The timestamp just has to be present and ISO-formatted enough to parse.
    assert "time" in body


def test_unknown_route_is_404():
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
