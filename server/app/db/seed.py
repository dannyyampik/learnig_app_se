"""Fill the database with believable demo data.

Run from the ``server/`` directory:

    python -m app.db.seed

Seeding goes through the same repositories the app uses — if the schema
and the repos disagree, the seed fails loudly, which is exactly what we
want from a smoke test.
"""

import random
import sys

import bcrypt

from . import database
from .repositories import like_repo, post_repo, user_repo

# Every demo account gets the same password so you can log in as any of
# them: password123 (bad password, great classroom).
DEMO_PASSWORD = "password123"

USERNAMES = ["alice", "bob", "carol"]

POST_BODIES = [
    "just set up glassbox — apparently I can watch my own HTTP requests?",
    "TIL: the browser and the server are two totally separate programs.",
    "wrote my first SQL JOIN today. posts + users, one query. felt great.",
    "hot take: LIMIT/OFFSET pagination is just 'skip N, take M'.",
    "the database rejects a duplicate like all by itself. composite keys!",
    "reading the feed query line by line — it's four ideas in one SELECT.",
    "migrations are just .sql files that run once, in order. that's it??",
    "asked the API for page=0 and got a 400 with a proper error body. tidy.",
    "foreign keys mean my posts can't point at a user that doesn't exist.",
    "repositories: the only files allowed to speak SQL. everything else asks.",
    "the ? placeholders in queries are what stop SQL injection. always.",
    "found out FastAPI writes API docs for me at /docs. free lunch.",
    "a connection per request is like a phone call per question.",
    "COUNT(*) per post, computed by the database, not by my Python. fast.",
    "you can read this feed without logging in — reads are public here.",
    "newest-first ordering is just ORDER BY created_at DESC. plus a tiebreak.",
    "the frontend has no idea SQLite exists. it only ever sees JSON.",
    "seeded thirty posts with a script. instant busy little town.",
    "indexes: pay a little on write, get fast reads. the feed says thanks.",
    "next phase is auth — cookies, sessions, bcrypt. the good stuff.",
    "curl http://localhost:8000/api/posts | jq — the app without the app.",
    "liking will be a PUT because doing it twice should change nothing.",
    "error envelopes: every failure, same JSON shape. clients love that.",
    "the server never trusts the browser. validation happens twice.",
    "somehow the schema file is the most honest documentation in the repo.",
    "each page of this feed is exactly one SQL round trip. count them.",
    "ON DELETE CASCADE: remove a user, their posts follow. tidy by default.",
    "phase 2 done: real rows, real joins, real pagination. onwards.",
]


def seed(conn) -> tuple[int, int, int]:
    # Hash once, reuse for all three — bcrypt is deliberately slow, and
    # they all share the demo password anyway.
    password_hash = bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt()).decode()
    users = [user_repo.create(conn, name, password_hash) for name in USERNAMES]

    # Deterministic "randomness": same seed, same demo data, every time.
    rng = random.Random(42)

    post_ids = []
    for body in POST_BODIES:
        author = rng.choice(users)
        post_ids.append(post_repo.create(conn, author["id"], body))

    like_count = 0
    for post_id in post_ids:
        for user in users:
            if rng.random() < 0.4:  # each user likes ~40% of posts
                like_repo.add(conn, user["id"], post_id)
                like_count += 1

    conn.commit()
    return len(users), len(post_ids), like_count


def main() -> None:
    conn = database.connect()
    database.apply_migrations(conn)

    existing = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    if existing:
        sys.exit(
            f"Refusing to seed: database already has {existing} user(s).\n"
            f"Delete {database.db_path()} and run again for a fresh start."
        )

    n_users, n_posts, n_likes = seed(conn)
    conn.close()
    print(
        f"Seeded {n_users} users, {n_posts} posts, {n_likes} likes "
        f"into {database.db_path()}\n"
        f"Log in as any of {', '.join(USERNAMES)} — password: {DEMO_PASSWORD}"
    )


if __name__ == "__main__":
    main()
