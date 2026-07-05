"""Business logic for user profiles."""

import sqlite3

from ..db.repositories import post_repo, user_repo
from ..errors import NotFoundError
from ..schemas import PostOut, ProfileOut


def get_profile(
    conn: sqlite3.Connection, *, username: str, viewer_id: int | None
) -> ProfileOut:
    user = user_repo.get_by_username(conn, username)
    if user is None:
        raise NotFoundError("No such user.")

    rows = post_repo.list_by_user(conn, user["id"], viewer_id=viewer_id)
    posts = [PostOut(**dict(row)) for row in rows]

    return ProfileOut(
        username=user["username"],
        created_at=user["created_at"],
        post_count=len(posts),
        # An aggregate computed from data we already have; with pagination
        # this would become its own SUM() query.
        likes_received=sum(post.like_count for post in posts),
        posts=posts,
    )
