"""HTTP endpoints for user profiles."""

import sqlite3

from fastapi import APIRouter, Depends

from ..db.database import get_db
from ..deps import get_current_user
from ..schemas import ProfileOut
from ..services import user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{username}", response_model=ProfileOut)
def get_profile(
    # {username} is a *path parameter* — part of the URL itself
    # (/api/users/alice), unlike ?page=2 which is a query parameter.
    # Identity of a resource goes in the path; options go in the query.
    username: str,
    viewer: sqlite3.Row | None = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> ProfileOut:
    """A user's public profile: stats plus all their posts."""
    return user_service.get_profile(
        conn, username=username, viewer_id=viewer["id"] if viewer else None
    )
