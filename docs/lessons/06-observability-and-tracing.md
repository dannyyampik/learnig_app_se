# Lesson 6 — Observability: Watching Your Own System Work

*Code that demonstrates this:
[`server/app/trace.py`](../../server/app/trace.py),
[`server/app/main.py`](../../server/app/main.py) (the `xray` middleware),
[`server/app/db/database.py`](../../server/app/db/database.py) (`TracedConnection`),
[`web/src/components/XRayPanel.jsx`](../../web/src/components/XRayPanel.jsx)*

## The one idea

In production you can't attach a debugger. The only way to know what a
system *did* is if it **tells you** — logs, metrics, and traces, emitted
while it works. That discipline is called **observability**, and the X-Ray
panel (press `` ` ``) is a working miniature of its most powerful tool:
the **request trace**.

Every `/api` response carries an extra header:

```
X-Glassbox-Trace: {"method":"POST","path":"/api/posts","status":201,
  "durationMs":14.2,
  "steps":["session cookie → @alice"],
  "sql":[{"query":"SELECT u.* FROM sessions s JOIN users u …","ms":0.1},
         {"query":"INSERT INTO posts (user_id, body) VALUES (?, ?)","ms":0.4},
         {"query":"SELECT p.id, p.body, … WHERE p.id = :post_id","ms":0.2}]}
```

That's the request's whole biography: which route, who was authenticated,
every SQL query with its timing, and the total. The frontend reads the
header in `api.js` and the panel shows it. Real-world tracing systems
(OpenTelemetry, Jaeger, Datadog) do exactly this across *many* services —
same idea, bigger graph.

## How the pieces snap together

1. **Middleware first and last**
   ([`main.py`](../../server/app/main.py)): wraps every request — opens a
   trace on the way in, harvests it on the way out. Middleware is the
   natural home for cross-cutting work precisely because *everything*
   passes through it.
2. **A per-request bag** ([`trace.py`](../../server/app/trace.py)): a
   `ContextVar` — like a global, but scoped to the current request, so
   two simultaneous requests can't mix their notes. "Context propagation"
   is the hard problem of real tracing systems; Python gives us a small
   version for free.
3. **Instrumented layers**: the database connection subclass times every
   `execute` ([`TracedConnection`](../../server/app/db/database.py)) —
   repositories don't even know they're being watched. The auth dependency
   drops a breadcrumb about who the cookie resolved to.
4. **The wire**: the finished trace travels in a response *header* —
   metadata about the response, alongside the body rather than inside it.
5. **The viewer** ([`XRayPanel.jsx`](../../web/src/components/XRayPanel.jsx)):
   `api.js` publishes each trace; the panel subscribes and renders.

## What traces are *for*: finding the expensive truth

Open the panel and load the feed. One page = one SELECT, ~1ms. Now
imagine the feed had been written the naive way — fetch posts, then for
each post fetch its author and count its likes: 1 + 2×10 queries per page.
The infamous **N+1 problem**, and the single most common backend
performance bug in the wild. In the panel it would be unmissable — a
wall of tiny queries. That's the point of observability: *making the
invisible cost visible*.

## The security flip side

We ship internals to any browser because teaching them is this app's job.
In a real system this trace header would be a serious information leak
(schema, timings, auth flow — an attacker's shopping list). Real apps gate
tracing to internal tools. Try the off switch:
`GLASSBOX_TRACE=0 uvicorn app.main:app` — the app still works, but it's
gone opaque. That toggle-of-visibility is itself the lesson.

## Try it

1. Press `` ` ``, then like a post: watch the `PUT …/like` trace appear —
   session lookup, existence check, `INSERT OR IGNORE` — while the heart
   filled *before* the trace arrived (optimistic UI, lesson 5, now visible).
2. Log out and load the feed: the trace's steps now say `anonymous`, and
   the SQL runs with `viewer_id = None`.
3. `curl -si localhost:8000/api/posts | grep -i x-glassbox` — the trace is
   just a header; nothing about it needs a browser.
