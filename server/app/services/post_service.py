"""Business logic for posts.

Services know the *rules* (how big is a page? what makes a feed?) but
nothing about HTTP — no requests, no status codes. That keeps them easy
to test and easy to reuse. (Lesson: docs/lessons/03-the-layered-backend.md)
"""

import sqlite3

from ..db.repositories import like_repo, post_repo
from ..errors import ForbiddenError, NotFoundError
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


def create_post(conn: sqlite3.Connection, *, author_id: int, body: str) -> PostOut:
    post_id = post_repo.create(conn, author_id, body)
    # Return the post exactly as the feed would show it, so the frontend
    # can drop it straight into the list without a second request.
    row = post_repo.get_annotated(conn, post_id, viewer_id=author_id)
    return PostOut(**dict(row))


def delete_post(conn: sqlite3.Connection, *, actor_id: int, post_id: int) -> None:
    """The rule this app exists to demonstrate: you may only delete your
    own posts. Note the order — 404 before 403: whether a post exists is
    public knowledge (it's in the feed); who may touch it comes second."""
    post = post_repo.get(conn, post_id)
    if post is None:
        raise NotFoundError("No such post.")
    if post["user_id"] != actor_id:
        raise ForbiddenError("You can only delete your own posts.")
    post_repo.delete(conn, post_id)


def like_post(conn: sqlite3.Connection, *, actor_id: int, post_id: int) -> None:
    if post_repo.get(conn, post_id) is None:
        raise NotFoundError("No such post.")
    # Idempotent by construction (INSERT OR IGNORE + composite PK):
    # liking twice is exactly as liked as liking once.
    like_repo.add(conn, actor_id, post_id)


def unlike_post(conn: sqlite3.Connection, *, actor_id: int, post_id: int) -> None:
    if post_repo.get(conn, post_id) is None:
        raise NotFoundError("No such post.")
    like_repo.remove(conn, actor_id, post_id)
