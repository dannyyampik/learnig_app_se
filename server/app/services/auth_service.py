"""Business logic for accounts and logins.

The rules that live here:
* passwords are stored only as bcrypt hashes — never recoverable
* a username can exist once
* wrong username and wrong password produce the *same* error
* logging in (or signing up) starts a session; logging out ends it

(Lesson: docs/lessons/04-auth-sessions-and-cookies.md)
"""

import secrets
import sqlite3

import bcrypt

from ..db.repositories import session_repo, user_repo
from ..errors import ConflictError, UnauthorizedError


def signup(conn: sqlite3.Connection, username: str, password: str):
    """Create an account and log it straight in. Returns (user, session_id)."""
    if user_repo.get_by_username(conn, username):
        raise ConflictError("That username is taken.")

    # bcrypt does two jobs: it salts (same password → different hash for
    # every user) and it's deliberately slow (brute-forcing a stolen
    # database costs centuries, not seconds).
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = user_repo.create(conn, username, password_hash)
    return user, _start_session(conn, user["id"])


def login(conn: sqlite3.Connection, username: str, password: str):
    """Verify credentials and start a session. Returns (user, session_id)."""
    user = user_repo.get_by_username(conn, username)
    if user is None or not _password_matches(password, user["password_hash"]):
        # One error for both failure modes, on purpose: a different message
        # for "no such user" would let anyone probe which usernames exist.
        raise UnauthorizedError("Wrong username or password.")
    return user, _start_session(conn, user["id"])


def logout(conn: sqlite3.Connection, session_id: str) -> None:
    session_repo.delete(conn, session_id)


def user_for_session(conn: sqlite3.Connection, session_id: str):
    return session_repo.get_user(conn, session_id)


def _start_session(conn: sqlite3.Connection, user_id: int) -> str:
    # 32 random bytes from the OS — unguessable. The id itself carries no
    # information; it's only a key into the sessions table.
    session_id = secrets.token_urlsafe(32)
    session_repo.create(conn, session_id, user_id)
    return session_id


def _password_matches(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        # The stored value isn't a bcrypt hash at all (e.g. a placeholder
        # from old seed data) — treat it as "no password works".
        return False
