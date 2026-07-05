"""All SQL that touches the ``users`` table.

Repositories are the only place SQL is allowed to live. They know nothing
about HTTP or business rules — they just move rows in and out.
(Lesson: docs/lessons/03-the-layered-backend.md)

Every query uses ``?`` placeholders. The database driver inserts the values
itself, so user input can never be mistaken for SQL — this is the defense
against SQL injection, and it's non-negotiable.
"""

import sqlite3


def create(conn: sqlite3.Connection, username: str, password_hash: str) -> sqlite3.Row:
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    return get_by_id(conn, cursor.lastrowid)


def get_by_id(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def get_by_username(conn: sqlite3.Connection, username: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
