"""Shared test fixtures.

Every test gets a brand-new database in a temp directory — tests must
never touch the real ``glassbox.db``, and must not depend on each other.
"""

import pytest
from fastapi.testclient import TestClient

from app.db import database
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """An HTTP client wired to the app, backed by a throwaway database.

    Entering the ``with`` block runs the app's startup (lifespan), which
    applies migrations — same code path as production.
    """
    monkeypatch.setenv("GLASSBOX_DB", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db(client):
    """A direct connection to the same throwaway database, for arranging
    test data through the repositories."""
    conn = database.connect()
    yield conn
    conn.close()
