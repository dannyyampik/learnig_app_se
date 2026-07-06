# Lesson 1 — The Client/Server Split

*Code that demonstrates this: [`server/app/main.py`](../../server/app/main.py),
[`web/src/pages/FeedPage.jsx`](../../web/src/pages/FeedPage.jsx), [`web/vite.config.js`](../../web/vite.config.js)*

## The one idea

A web app is **two programs that never share memory**:

- The **client** — JavaScript running in the user's browser, on *their*
  machine. It draws the UI and reacts to clicks.
- The **server** — a program running somewhere else (here: Python on your
  laptop, in production: a machine in a datacenter). It owns the data and
  enforces the rules.

The *only* way they can communicate is by sending messages over the network,
using **HTTP**: the client sends a *request*, the server sends back exactly
one *response*. No shared variables, no function calls across the gap —
just bytes on a wire, which both sides agree to format as **JSON**.

```
  your browser                          your Python process
 ┌─────────────┐   GET /api/health     ┌──────────────────┐
 │  React app  │ ────────────────────▶ │   FastAPI app    │
 │             │ ◀──────────────────── │                  │
 └─────────────┘   200 {"status":"ok"} └──────────────────┘
```

## Why is it split like this?

- **The browser is on someone else's computer.** You can't trust it, you
  can't control it, and it can't be allowed to touch your database directly.
- **One server, many clients.** A thousand browsers can talk to the same
  backend; the data has to live in the one place they all reach.
- **Independent evolution.** The frontend and backend can be written in
  different languages (ours are!), deployed separately, and replaced
  separately — as long as the HTTP contract between them stays the same.

## See it in Glassbox

1. Run both halves (see the [README](../../README.md)), then open
   <http://localhost:5173>.
2. Open DevTools → **Network**, reload, and look at the requests the page
   made: `me` ("who is logged in?") and `posts` (the feed). Click one —
   you can read the actual request headers and the JSON response. This is
   the entire relationship between the two programs, laid bare. (The
   X-Ray panel — press `` ` `` — shows the same requests, plus what the
   server did to answer them.)
3. Kill the Python server (Ctrl-C in its terminal) and reload. The
   frontend still renders (it's a separate program!) but its requests
   fail — and the UI shows the error state we wrote for exactly this case.

## One wrinkle: the dev proxy

In development the browser talks only to Vite (port 5173). Vite serves the
frontend files itself and **forwards** anything under `/api` to the Python
server on port 8000. This is what nginx or a load balancer does in
production, and it spares us CORS configuration while learning. See the
comment in [`web/vite.config.js`](../../web/vite.config.js).

## Vocabulary that now means something

| Term | Meaning here |
|---|---|
| Client | The React app in your browser |
| Server / backend | The FastAPI process on port 8000 |
| Request / response | The one-question-one-answer HTTP exchange |
| Endpoint | A URL the server answers, like `GET /api/health` |
| JSON | The text format both sides agree on for data |
| Proxy | A middleman that forwards requests (Vite in dev) |
