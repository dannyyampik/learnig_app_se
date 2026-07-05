"""API tests — exercise the backend the way a real client would.

``TestClient`` makes genuine HTTP-shaped requests against the app without
starting a network server, so these tests check the full stack: routing,
validation, handlers, and JSON serialization.
"""


def test_health_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "glassbox-api"
    # The timestamp just has to be present; its value changes per request.
    assert "time" in body


def test_unknown_route_is_404(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
