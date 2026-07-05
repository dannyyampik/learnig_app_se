"""Who is making this request? — the auth dependencies.

This is the only piece of FastAPI "magic" we lean on, so here's the trick
in full: ``Depends(f)`` means "run ``f`` first and hand its return value to
my parameter". That's it. These two functions run before any route that
declares them:

* ``get_current_user`` — the user for the request's session cookie, or
  ``None``. For routes that work either way (the feed).
* ``require_user``     — same, but a missing/invalid session raises 401.
  For routes that only make sense logged in.
"""

import sqlite3

from fastapi import Depends, Request

from . import trace
from .db.database import get_db
from .errors import UnauthorizedError
from .services import auth_service

SESSION_COOKIE = "sid"


def get_current_user(
    request: Request, conn: sqlite3.Connection = Depends(get_db)
) -> sqlite3.Row | None:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        trace.add_step("no session cookie → anonymous")
        return None
    # An unknown/expired session id is the same as no session: None, not an
    # error — being logged out isn't a mistake.
    user = auth_service.user_for_session(conn, session_id)
    trace.add_step(
        f"session cookie → @{user['username']}" if user else "session unknown → anonymous"
    )
    return user


def require_user(user: sqlite3.Row | None = Depends(get_current_user)) -> sqlite3.Row:
    if user is None:
        raise UnauthorizedError("You need to log in for that.")
    return user
