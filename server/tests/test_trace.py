"""Tests for the X-Ray trace header."""

import json


def test_trace_header_shows_the_request_lifecycle(client):
    client.post(
        "/api/auth/signup", json={"username": "alice", "password": "password123"}
    )

    response = client.get("/api/posts")

    trace = json.loads(response.headers["X-Glassbox-Trace"])
    assert trace["method"] == "GET"
    assert trace["path"] == "/api/posts"
    assert trace["status"] == 200
    assert trace["durationMs"] >= 0
    # The auth dependency left its breadcrumb…
    assert any("@alice" in step for step in trace["steps"])
    # …and the SQL that produced the feed is in there with timings.
    queries = [entry["query"] for entry in trace["sql"]]
    assert any(q.startswith("SELECT p.id") for q in queries)
    assert all(entry["ms"] >= 0 for entry in trace["sql"])


def test_trace_covers_writes_too(client):
    client.post(
        "/api/auth/signup", json={"username": "alice", "password": "password123"}
    )

    response = client.post("/api/posts", json={"body": "traced!"})

    trace = json.loads(response.headers["X-Glassbox-Trace"])
    assert trace["status"] == 201
    assert any("INSERT INTO posts" in entry["query"] for entry in trace["sql"])


def test_trace_can_be_turned_off(client, monkeypatch):
    monkeypatch.setenv("GLASSBOX_TRACE", "0")

    response = client.get("/api/posts")

    assert "X-Glassbox-Trace" not in response.headers


def test_non_api_paths_are_not_traced(client):
    response = client.get("/docs")

    assert "X-Glassbox-Trace" not in response.headers
