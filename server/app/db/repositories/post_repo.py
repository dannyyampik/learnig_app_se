"""All SQL that touches the ``posts`` table."""

import sqlite3

# The annotated-post SELECT — the teaching centerpiece of the data layer.
#
#   JOIN users          → attach the author's username to each post
#   correlated COUNT    → how many likes does *this* post have?
#   correlated EXISTS   → did *the viewing user* like this post?
#
# Every place the API shows a post (feed, profile, a fresh create) reuses
# this same shape, so a post always means the same thing.
ANNOTATED_POST = """
    SELECT
        p.id,
        p.body,
        p.created_at,
        u.username AS author,
        (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS like_count,
        EXISTS(
            SELECT 1 FROM likes l
            WHERE l.post_id = p.id AND l.user_id = :viewer_id
        ) AS liked_by_me
    FROM posts p
    JOIN users u ON u.id = p.user_id
"""

# The feed adds ordering (newest first, id breaks same-millisecond ties)
# and pagination (fetch one page, skip the pages before). One round trip
# to the database per feed page, no matter how many posts.
FEED_QUERY = ANNOTATED_POST + """
    ORDER BY p.created_at DESC, p.id DESC
    LIMIT :limit OFFSET :offset
"""


def list_feed(
    conn: sqlite3.Connection,
    *,
    viewer_id: int | None,
    limit: int,
    offset: int,
) -> list[sqlite3.Row]:
    """Newest-first page of posts, annotated for the viewing user.

    ``viewer_id`` may be None (nobody is logged in — phases 2 and 3);
    the EXISTS check then simply never matches and ``liked_by_me`` is 0.
    """
    return conn.execute(
        FEED_QUERY,
        {"viewer_id": viewer_id, "limit": limit, "offset": offset},
    ).fetchall()


def get_annotated(
    conn: sqlite3.Connection, post_id: int, *, viewer_id: int | None
) -> sqlite3.Row | None:
    """One post in the same annotated shape the feed uses."""
    return conn.execute(
        ANNOTATED_POST + " WHERE p.id = :post_id",
        {"post_id": post_id, "viewer_id": viewer_id},
    ).fetchone()


def list_by_user(
    conn: sqlite3.Connection, user_id: int, *, viewer_id: int | None
) -> list[sqlite3.Row]:
    """All of one user's posts, newest first (for their profile page)."""
    return conn.execute(
        ANNOTATED_POST
        + " WHERE p.user_id = :user_id ORDER BY p.created_at DESC, p.id DESC",
        {"user_id": user_id, "viewer_id": viewer_id},
    ).fetchall()


def get(conn: sqlite3.Connection, post_id: int) -> sqlite3.Row | None:
    """The bare row — enough to check existence and ownership."""
    return conn.execute(
        "SELECT * FROM posts WHERE id = ?", (post_id,)
    ).fetchone()


def create(conn: sqlite3.Connection, user_id: int, body: str) -> int:
    cursor = conn.execute(
        "INSERT INTO posts (user_id, body) VALUES (?, ?)",
        (user_id, body),
    )
    return cursor.lastrowid


def delete(conn: sqlite3.Connection, post_id: int) -> None:
    # The likes go with it automatically — ON DELETE CASCADE in the schema.
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
