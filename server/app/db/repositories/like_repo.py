"""All SQL that touches the ``likes`` table."""

import sqlite3


def add(conn: sqlite3.Connection, user_id: int, post_id: int) -> None:
    # OR IGNORE: if the (user, post) row already exists, do nothing instead
    # of erroring. Combined with the composite primary key, this makes
    # liking *idempotent* — pressing the button twice is safe by design.
    conn.execute(
        "INSERT OR IGNORE INTO likes (user_id, post_id) VALUES (?, ?)",
        (user_id, post_id),
    )


def remove(conn: sqlite3.Connection, user_id: int, post_id: int) -> None:
    # Deleting a row that isn't there is also a no-op: idempotent again.
    conn.execute(
        "DELETE FROM likes WHERE user_id = ? AND post_id = ?",
        (user_id, post_id),
    )
