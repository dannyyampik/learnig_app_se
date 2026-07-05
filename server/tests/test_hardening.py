"""Tests for the unhappiest paths: unexpected crashes and the request log.

Good systems are defined by how they fail. These tests deliberately break
things and check that the failure is boring: the standard envelope for the
client, the full story in the log, nothing leaked.
"""

import logging

import pytest
from fastapi.testclient import TestClient

from app.main import app


# A route that exists only in tests: the simplest possible "bug in our
# code". Registering it here keeps the production app free of test props.
@app.get("/api/boom")
def boom():
    raise RuntimeError("kaboom: secret internal detail")


@pytest.fixture
def crashing_client(tmp_path, monkeypatch):
    monkeypatch.setenv("GLASSBOX_DB", str(tmp_path / "test.db"))
    # By default TestClient re-raises server exceptions into the test —
    # handy normally, but here the *response* is what we're testing.
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_unexpected_errors_wear_the_standard_envelope(crashing_client):
    response = crashing_client.get("/api/boom")

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "INTERNAL"
    # The client must NOT see internals — no exception text, no traceback.
    assert "kaboom" not in response.text
    assert "RuntimeError" not in response.text


def test_crash_details_do_go_to_the_log(crashing_client, caplog):
    with caplog.at_level(logging.ERROR, logger="glassbox"):
        crashing_client.get("/api/boom")

    # Same failure, other audience: we get everything the client doesn't.
    assert "unhandled error on GET /api/boom" in caplog.text
    assert "RuntimeError: kaboom" in caplog.text


def test_every_api_request_leaves_a_log_line(client, caplog):
    with caplog.at_level(logging.INFO, logger="glassbox"):
        client.get("/api/posts")

    assert any(
        "GET /api/posts -> 200 in" in message for message in caplog.messages
    )
