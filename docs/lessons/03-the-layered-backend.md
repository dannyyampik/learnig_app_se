# Lesson 3 — The Layered Backend

*Code that demonstrates this:
[`server/app/routers/posts.py`](../../server/app/routers/posts.py),
[`server/app/services/post_service.py`](../../server/app/services/post_service.py),
[`server/app/db/repositories/post_repo.py`](../../server/app/db/repositories/post_repo.py)*

## The one idea

The backend is a stack of layers, and **each layer has exactly one job**:

```
routers/         speak HTTP        "parse the request, shape the response"
services/        know the rules    "a page is 10 posts; newest first"
repositories/    speak SQL         "here's the query that fetches it"
```

Follow `GET /api/posts?page=2` down the stack:

1. **Router** ([`posts.py`](../../server/app/routers/posts.py)) — declares
   `page: int = Query(1, ge=1)`. FastAPI parses `"2"` into `2` and rejects
   `0` or `"banana"` before our code runs. The router calls the service and
   returns its result. That's all a router does.
2. **Service** ([`post_service.py`](../../server/app/services/post_service.py))
   — turns *page 2* into *limit 11, offset 10* (the +1 row is the
   `hasMore` trick), calls the repository, wraps rows into the response
   model. Notice what's absent: no request, no status codes, no SQL.
3. **Repository** ([`post_repo.py`](../../server/app/db/repositories/post_repo.py))
   — runs the one big feed query and returns rows. It doesn't know what a
   "page" is; it was told limit and offset.

## Why bother, in a 300-line app?

Because the payoff isn't size, it's **change** and **testing**:

- Want Postgres instead of SQLite? Touch only `db/`.
- Want the feed sorted by likes? Touch only the repository's query.
- Want 20 posts per page? Touch one constant in the service.
- Testing business rules? Call the service with a database — no web server
  required. (See how [`tests/test_feed.py`](../../server/tests/test_feed.py)
  arranges data through repositories, then asserts through real HTTP.)

Every layer boundary is also a **trust boundary rehearsal**: the router
validates shape ("is `page` a positive integer?"), the schema validates
data ("is the body ≤ 280 chars?"), so inner layers get to assume clean
input.

## Dependency injection without the buzzword

The router receives its database connection as a parameter:

```python
def get_feed(page: int = Query(1, ge=1),
             conn: sqlite3.Connection = Depends(get_db)):
```

`Depends(get_db)` tells FastAPI: *before calling this handler, run
[`get_db`](../../server/app/db/database.py) and pass in what it yields* —
a fresh connection, opened per request, committed and closed after (a
phone call per question). Handing a function its dependencies instead of
letting it construct them is **dependency injection** — and it's why tests
can swap in a throwaway database just by changing an environment variable.

## One error shape, one place

[`errors.py`](../../server/app/errors.py) turns every validation failure
into the same JSON envelope:

```json
{ "error": { "code": "VALIDATION", "message": "Invalid request.",
             "details": [{ "field": "query.page", "message": "..." }] } }
```

Clients get to write one error handler, not one per endpoint. Try it:
`curl 'http://localhost:8000/api/posts?page=0'`.
