"""All SQL that touches the ``posts`` table."""

import sqlite3

# The feed query — the teaching centerpiece of the data layer.
#
#   JOIN users          → attach the author's username to each post
#   correlated COUNT    → how many likes does *this* post have?
#   correlated EXISTS   → did *the viewing user* like this post?
#   ORDER BY ... DESC   → newest first (id breaks ties for posts created
#                         in the same millisecond)
#   LIMIT / OFFSET      → pagination: fetch one page, skip the pages before
#
# One round trip to the database per feed page, no matter how many posts.
FEED_QUERY = """
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


def create(conn: sqlite3.Connection, user_id: int, body: str) -> int:
    cursor = conn.execute(
        "INSERT INTO posts (user_id, body) VALUES (?, ?)",
        (user_id, body),
    )
    return cursor.lastrowid
