# Lesson 4 — Auth: Passwords, Sessions, and Cookies

*Code that demonstrates this:
[`server/app/services/auth_service.py`](../../server/app/services/auth_service.py),
[`server/app/routers/auth.py`](../../server/app/routers/auth.py),
[`server/app/deps.py`](../../server/app/deps.py),
[`web/src/context/AuthContext.jsx`](../../web/src/context/AuthContext.jsx)*

## The problem

HTTP is **stateless**: every request arrives alone, with no memory of the
ones before it. So how does the server know request #47 comes from the same
person who logged in during request #3? Something must travel with every
request that says *"it's still me."*

## The solution: a session cookie

```
LOGIN                                    EVERY LATER REQUEST
browser → POST /api/auth/login           browser → GET /api/posts
          { alice, password123 }                   Cookie: sid=Kb3…9x
server:   check password ✓               server:   look up sid in the
          INSERT INTO sessions                     sessions table →
          (id: Kb3…9x, user: 1)                    "this is alice"
server → Set-Cookie: sid=Kb3…9x
```

A **cookie** is a tiny piece of data the server asks the browser to store;
the browser then attaches it to every request to that site, automatically.
Ours holds one thing: a random, unguessable session id. The id means
nothing by itself — it's a key into the `sessions` table, where the real
information (which user) lives **on the server**.

Being "logged in" is nothing more than: *your browser holds a cookie whose
id exists in our sessions table.* Logout is one `DELETE` — after that, the
cookie is a key to a lock that no longer exists
(see `test_logout_kills_the_session_server_side`).

## Passwords: never stored, never recoverable

We store `bcrypt(password)`, not the password
([`auth_service.py`](../../server/app/services/auth_service.py)). bcrypt:

- **salts** — the same password hashes differently for every user, so
  matching hashes can't reveal shared passwords;
- **is deliberately slow** — checking one password takes ~100ms, which is
  fine for a login and catastrophic for someone brute-forcing a stolen
  database at scale.

Login never "decrypts" anything — it hashes what you typed and compares.
This is why real sites can only *reset* your password, never *email it to
you*: they genuinely don't have it.

One subtle rule: wrong username and wrong password return the **identical**
error. A different message for "no such user" would let anyone probe which
usernames exist.

## The two cookie flags that matter

In [`routers/auth.py`](../../server/app/routers/auth.py) the cookie is set
with:

- **`httponly`** — JavaScript on the page cannot read the cookie. If an
  attacker sneaks a script into the page (XSS), it still can't steal your
  session.
- **`samesite=lax`** — other websites can't make your browser send our
  cookie along with forged requests (CSRF). Evil.com can *link* to us, but
  it can't *act as you*.

(Production adds `secure` — HTTPS only. We skip it so localhost works.)

## The frontend half

React state dies on every reload; the cookie doesn't. So on page load
[`AuthContext`](../../web/src/context/AuthContext.jsx) asks
`GET /api/auth/me` "who am I?" and the cookie answers. Note the three-state
answer — `undefined` (still asking), `null` (nobody), or a user — the nav
bar renders differently for each.

## Try it

1. Log in, open DevTools → Application → Cookies. There's `sid`. Try
   reading it from the console: `document.cookie` → it's not there
   (`httponly` at work).
2. Reload the page — still logged in. Delete the cookie by hand — reload —
   logged out. *You* just performed a logout, client-side half only.
3. `curl -i -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"password123"}'`
   and read the `Set-Cookie` header with your own eyes.
