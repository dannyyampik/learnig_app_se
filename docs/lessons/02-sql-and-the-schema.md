# Lesson 2 — SQL and the Schema

*Code that demonstrates this:
[`server/app/db/migrations/001_init.sql`](../../server/app/db/migrations/001_init.sql),
[`server/app/db/database.py`](../../server/app/db/database.py),
[`server/app/db/repositories/post_repo.py`](../../server/app/db/repositories/post_repo.py)*

## The one idea

A relational database stores data as **tables of rows**, and the schema —
the set of table definitions — is a *contract about what data can exist*.
Glassbox has four tables:

```
users:    id │ username │ password_hash │ created_at
posts:    id │ user_id → users.id │ body │ created_at
likes:    user_id → users.id │ post_id → posts.id │ created_at
sessions: id │ user_id → users.id │ created_at
```

The arrows are **foreign keys**: a post's `user_id` must be the `id` of a
real user. The database refuses anything else. This is the running theme of
the schema: **push invariants into the database**, because code has bugs
and the database never blinks:

- `UNIQUE` on `username` → no duplicate accounts, ever
- `CHECK (length(body) BETWEEN 1 AND 280)` → no empty or oversized posts
- `PRIMARY KEY (user_id, post_id)` on `likes` → you *can't* like twice

## Migrations: how schemas evolve

You can't just edit a table definition on a live database — you write a
**migration**: a SQL file that moves the schema from shape N to shape N+1.
Our runner ([`database.py`](../../server/app/db/database.py)) is ~20 lines:
run every `*.sql` file in order, remember which ones ran in a
`schema_migrations` table, never run one twice. Professional tools
(Alembic, Flyway, Rails migrations) are this idea with more safety rails.

## The feed query, line by line

One query produces the entire feed page
([`post_repo.py`](../../server/app/db/repositories/post_repo.py)):

```sql
SELECT p.id, p.body, p.created_at,
       u.username AS author,                          -- ①
       (SELECT COUNT(*) FROM likes l
         WHERE l.post_id = p.id) AS like_count,       -- ②
       EXISTS(SELECT 1 FROM likes l
         WHERE l.post_id = p.id
           AND l.user_id = :viewer_id) AS liked_by_me -- ③
FROM posts p
JOIN users u ON u.id = p.user_id                      -- ①
ORDER BY p.created_at DESC, p.id DESC                 -- ④
LIMIT :limit OFFSET :offset                           -- ⑤
```

1. **JOIN** — glue each post to its author's row so we can show `@alice`
   instead of `user_id = 1`.
2. **Aggregate subquery** — the database counts likes per post; we never
   ship all the like rows to Python just to count them.
3. **Correlated EXISTS** — "did the viewing user like this one?" — asked
   per post, answered by the index in microseconds.
4. **Deterministic order** — newest first; `id` breaks ties for posts
   created in the same millisecond. Unordered SQL results are *allowed to
   come back in any order*, so feeds must always say ORDER BY.
5. **Pagination** — skip `offset` rows, take `limit`. The service asks for
   one extra row: if it arrives, there's another page (`hasMore`).

## Placeholders, or: the injection lesson

Every query uses `?` / `:name` placeholders and passes values separately:

```python
conn.execute("SELECT * FROM users WHERE username = ?", (username,))
```

The driver guarantees the value is treated as *data*, never as SQL. The
alternative — string concatenation — is how SQL injection happens, and it
has no legitimate use. If you remember one thing from this lesson: **never
build SQL out of user input with string formatting.**

## Try it yourself

```bash
cd server && python -m app.db.seed        # fill the database
sqlite3 glassbox.db                       # open a SQL prompt on the file
```

```sql
.tables                                   -- see the schema in the wild
SELECT username, COUNT(*) FROM posts p
  JOIN users u ON u.id = p.user_id
  GROUP BY username;                      -- who posts the most?
INSERT INTO posts (user_id, body) VALUES (1, '');  -- watch CHECK reject it
```
