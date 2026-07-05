"""HTTP endpoints for posts.

Routers are translators: HTTP in, HTTP out, and *nothing else*. Parse and
validate the request, call a service, shape the response. If you spot an
if-statement about business rules in here, it's in the wrong layer.
"""

import sqlite3

from fastapi import APIRouter, Depends, Query

from ..db.database import get_db
from ..schemas import FeedPage
from ..services import post_service

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=FeedPage)
def get_feed(
    # Query(1, ge=1) declares the contract: optional, defaults to 1, must
    # be >= 1. FastAPI enforces it before this function runs — a bad value
    # becomes a 400 via our validation handler (see errors.py).
    page: int = Query(1, ge=1),
    conn: sqlite3.Connection = Depends(get_db),
) -> FeedPage:
    """The public feed, newest first, ten posts per page."""
    return post_service.get_feed(conn, page=page)
