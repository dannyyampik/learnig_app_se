"""The door to the database: connections and migrations.

SQLite is a database in a single file (``server/glassbox.db``) — no server
to install, but real SQL. Two jobs live here:

* ``connect()``   — open a connection with sane settings
* ``apply_migrations()`` — bring the schema up to date at startup

(Lesson: docs/lessons/02-sql-and-the-schema.md)
"""

import os
import sqlite3
import time
from pathlib import Path

from .. import trace

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

# server/glassbox.db by default; tests point GLASSBOX_DB at a throwaway file.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "glassbox.db"


def db_path() -> str:
    return os.environ.get("GLASSBOX_DB", str(DEFAULT_DB_PATH))


class TracedConnection(sqlite3.Connection):
    """A normal SQLite connection that reports every query to the X-Ray
    trace. Repositories don't know or care — they call ``execute`` as
    always; the timing happens underneath them."""

    def execute(self, sql, parameters=(), /):
        started = time.perf_counter()
        try:
            return super().execute(sql, parameters)
        finally:
            trace.add_sql(sql, (time.perf_counter() - started) * 1000)


def connect(path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or db_path(), factory=TracedConnection)
    # Rows behave like dicts (row["username"]) instead of bare tuples.
    conn.row_factory = sqlite3.Row
    # SQLite doesn't enforce foreign keys unless you ask. We ask.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_migrations(conn: sqlite3.Connection) -> list[str]:
    """Run every migration file that hasn't run yet, in filename order.

    The database keeps its own record of applied migrations in a
    ``schema_migrations`` table — so running this twice is harmless.
    This is the essence of what tools like Alembic or Flyway do.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename   TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    already = {
        row["filename"]
        for row in conn.execute("SELECT filename FROM schema_migrations")
    }

    applied = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in already:
            continue
        conn.executescript(path.read_text())
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)", (path.name,)
        )
        applied.append(path.name)
    conn.commit()
    return applied


def get_db():
    """FastAPI dependency: one fresh connection per request.

    Think of it as a phone call: dial when the request arrives, hang up
    when the response leaves. ``yield`` hands the connection to the route
    handler; everything after it runs once the response is done — commit
    on success, and always close.
    """
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
