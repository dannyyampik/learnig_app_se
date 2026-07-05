"""Business logic for posts.

Services know the *rules* (how big is a page? what makes a feed?) but
nothing about HTTP — no requests, no status codes. That keeps them easy
to test and easy to reuse. (Lesson: docs/lessons/03-the-layered-backend.md)
"""

import sqlite3

from ..db.repositories import post_repo
from ..schemas import FeedPage, PostOut

PAGE_SIZE = 10


def get_feed(
    conn: sqlite3.Connection, *, page: int, viewer_id: int | None = None
) -> FeedPage:
    offset = (page - 1) * PAGE_SIZE

    # The +1 trick: ask for one row more than a page. If we get it, there's
    # another page after this one — without a second COUNT query.
    rows = post_repo.list_feed(
        conn, viewer_id=viewer_id, limit=PAGE_SIZE + 1, offset=offset
    )
    has_more = len(rows) > PAGE_SIZE

    items = [PostOut(**dict(row)) for row in rows[:PAGE_SIZE]]
    return FeedPage(items=items, page=page, has_more=has_more)
