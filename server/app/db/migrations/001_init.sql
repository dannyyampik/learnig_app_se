-- Migration 001 — the initial schema.
--
-- A migration is just SQL that moves the database from one shape to the
-- next. Files run once, in filename order, and the database remembers which
-- ones it has seen (see database.py). That's the whole trick behind every
-- migration tool. (Lesson: docs/lessons/02-sql-and-the-schema.md)

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    -- UNIQUE makes the database itself reject duplicate usernames — we
    -- don't have to remember to check in code.
    username      TEXT    NOT NULL UNIQUE CHECK (length(username) BETWEEN 3 AND 20),
    -- Never the password itself; a bcrypt hash of it (phase 3).
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE posts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    -- The foreign key: every post must point at a real user. ON DELETE
    -- CASCADE means deleting a user takes their posts with them.
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body       TEXT    NOT NULL CHECK (length(body) BETWEEN 1 AND 280),
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE likes (
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id    INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    -- Composite primary key: one row per (user, post) pair, enforced by
    -- the database. "You can't like a post twice" is a schema fact, not
    -- an if-statement somewhere.
    PRIMARY KEY (user_id, post_id)
);

-- Login sessions (used from phase 3): the cookie stores the id, the row
-- says who it belongs to.
CREATE TABLE sessions (
    id         TEXT    PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Indexes: the feed reads posts newest-first and counts likes per post
-- constantly, so we pay a little on every write to make those reads fast.
CREATE INDEX idx_posts_created ON posts (created_at DESC, id DESC);
CREATE INDEX idx_likes_post ON likes (post_id);
