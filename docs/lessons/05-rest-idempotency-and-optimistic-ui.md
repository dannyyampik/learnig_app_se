# Lesson 5 — REST Semantics, Idempotency, and Optimistic UI

*Code that demonstrates this:
[`server/app/routers/posts.py`](../../server/app/routers/posts.py),
[`server/app/services/post_service.py`](../../server/app/services/post_service.py),
[`web/src/components/LikeButton.jsx`](../../web/src/components/LikeButton.jsx)*

## The one idea

HTTP gives you a small vocabulary — methods and status codes — and using it
*precisely* is what makes an API predictable. Glassbox's post endpoints are
a tour of that vocabulary:

| Action | Method & path | Why this method |
|---|---|---|
| Create a post | `POST /api/posts` | POST = "make a new one each time" |
| Delete a post | `DELETE /api/posts/42` | says what it does |
| Like | `PUT /api/posts/42/like` | PUT = "make the world be this way" |
| Unlike | `DELETE /api/posts/42/like` | remove that state |

## Idempotency: the reason like is PUT

An operation is **idempotent** if doing it twice leaves the world exactly
as doing it once. `PUT /posts/42/like` means *"make it so I like post 42"*
— saying it again changes nothing. `POST` means *"create another"* — saying
it again makes a duplicate.

Why care? **Retries.** Networks fail after the server did the work but
before the response arrived. A client can safely retry an idempotent
request; retrying a POST risks doubles. That's why our like button can
fire-and-retry freely, and it's enforced in *the schema*, not by an
if-statement: `INSERT OR IGNORE` + the composite primary key
(see `test_like_is_idempotent`).

## Three refusals that mean different things

Deleting a post can fail three ways, and the status code tells you which
rule you broke (see [`post_service.py`](../../server/app/services/post_service.py)):

- **401 Unauthorized** — we don't know who you are. Log in.
- **403 Forbidden** — we know exactly who you are; this isn't your post.
- **404 Not Found** — there is no post 9999.

One more from signup: **409 Conflict** — the username is taken. Precise
status codes are how machines (and other developers) understand your API
without reading your source.

## The permission rule lives in one place

The frontend hides the ✕ button on other people's posts — but that's
*politeness, not security*. Anyone can send
`curl -X DELETE localhost:8000/api/posts/1` with any cookie they own. The
real rule — `post.user_id != actor_id → ForbiddenError` — lives in the
service, on the server, where it can't be bypassed. UI hides; server
forbids. Never confuse the two.

## Optimistic UI: lying to the user, briefly and honestly

Click a heart and it fills **immediately** — before the server has
answered ([`LikeButton.jsx`](../../web/src/components/LikeButton.jsx)):

```
1. remember the current state
2. show the new state NOW            ← the "optimism"
3. send the request
4. if it fails → put the old state back
```

The alternative (grey out the button, wait ~100ms, then update) feels
broken on every tap. The cost of optimism is that the screen can briefly
disagree with the database — which is why step 1 keeps the rollback state,
and why the server response, not the click, remains the source of truth.

Try it: open DevTools → Network, throttle to "Slow 3G", and like a post.
The heart fills instantly; the PUT completes a second later. Then stop the
backend and click — watch the heart fill and *un-fill* as the rollback
lands.
