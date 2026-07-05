"""HTTP endpoints for accounts and sessions.

The interesting part is the cookie. On signup/login the server *sets* it;
the browser then attaches it to every later request automatically — that's
the entire mechanism that keeps you logged in across clicks and reloads.
"""

import sqlite3

from fastapi import APIRouter, Depends, Request, Response

from ..db.database import get_db
from ..deps import SESSION_COOKIE, get_current_user, require_user
from ..schemas import CredentialsIn, UserOut
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        session_id,
        # httponly: JavaScript cannot read this cookie — even a successful
        #   XSS attack can't just exfiltrate the session.
        httponly=True,
        # samesite=lax: other sites can't ride along on our cookie when
        #   POSTing at us — the everyday CSRF defense.
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 days
        # In production this would also say `secure=True` (HTTPS only);
        # left off so plain http://localhost works while learning.
    )


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(
    body: CredentialsIn,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
):
    """Create an account and log it in (one step — no separate login dance)."""
    user, session_id = auth_service.signup(conn, body.username, body.password)
    _set_session_cookie(response, session_id)
    return UserOut(**dict(user))


@router.post("/login", response_model=UserOut)
def login(
    body: CredentialsIn,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
):
    user, session_id = auth_service.login(conn, body.username, body.password)
    _set_session_cookie(response, session_id)
    return UserOut(**dict(user))


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    user: sqlite3.Row = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """End the session server-side AND clear the cookie client-side.

    Deleting the row is the part that matters — a copied cookie is dead
    the moment the row is gone. Clearing the cookie is just tidiness.
    """
    auth_service.logout(conn, request.cookies[SESSION_COOKIE])
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me", response_model=UserOut | None)
def me(user: sqlite3.Row | None = Depends(get_current_user)):
    """Who am I? The frontend calls this once on page load to restore the
    session — the cookie survives reloads; React state does not."""
    return UserOut(**dict(user)) if user else None
