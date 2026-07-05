"""HTTP endpoints for posts.

Routers are translators: HTTP in, HTTP out, and *nothing else*. Parse and
validate the request, call a service, shape the response. If you spot an
if-statement about business rules in here, it's in the wrong layer.
"""

import sqlite3

from fastapi import APIRouter, Depends, Query

from ..db.database import get_db
from ..deps import get_current_user, require_user
from ..schemas import FeedPage, PostCreateIn, PostOut
from ..services import post_service

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=FeedPage)
def get_feed(
    # Query(1, ge=1) declares the contract: optional, defaults to 1, must
    # be >= 1. FastAPI enforces it before this function runs — a bad value
    # becomes a 400 via our validation handler (see errors.py).
    page: int = Query(1, ge=1),
    # Optional auth: the feed is public, but knowing the viewer lets the
    # query answer "did *I* like this?" per post.
    viewer: sqlite3.Row | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> FeedPage:
    """The public feed, newest first, ten posts per page."""
    return post_service.get_feed(
        conn, page=page, viewer_id=viewer["id"] if viewer else None
    )


@router.post("", response_model=PostOut, status_code=201)
def create_post(
    body: PostCreateIn,
    user: sqlite3.Row = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> PostOut:
    """Write a post. 201 Created + the post as the feed will show it."""
    return post_service.create_post(conn, author_id=user["id"], body=body.body)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    user: sqlite3.Row = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    """Delete your own post. Someone else's → 403; nonexistent → 404."""
    post_service.delete_post(conn, actor_id=user["id"], post_id=post_id)


# Like is PUT, not POST: "make it so that I like this post". Saying it
# twice leaves the world in the same state — idempotent — so a client can
# safely retry on a flaky network. Unlike is DELETE for the same reason.
@router.put("/{post_id}/like", status_code=204)
def like_post(
    post_id: int,
    user: sqlite3.Row = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    post_service.like_post(conn, actor_id=user["id"], post_id=post_id)


@router.delete("/{post_id}/like", status_code=204)
def unlike_post(
    post_id: int,
    user: sqlite3.Row = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> None:
    post_service.unlike_post(conn, actor_id=user["id"], post_id=post_id)
