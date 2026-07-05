"""All SQL that touches the ``sessions`` table.

A session row is the server-side half of "being logged in": the browser
holds the id in a cookie, this table says which user it belongs to.
Delete the row and that cookie is worthless — that's what logout is.
"""

import sqlite3


def create(conn: sqlite3.Connection, session_id: str, user_id: int) -> None:
    conn.execute(
        "INSERT INTO sessions (id, user_id) VALUES (?, ?)",
        (session_id, user_id),
    )


def get_user(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row | None:
    """The user this session belongs to, or None if the session is unknown."""
    return conn.execute(
        """
        SELECT u.* FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ?
        """,
        (session_id,),
    ).fetchone()


def delete(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
