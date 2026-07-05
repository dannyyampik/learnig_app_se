# Lesson 7 — Testing the Stack

*Code that demonstrates this:
[`server/tests/`](../../server/tests/),
[`web/src/components/PostComposer.test.jsx`](../../web/src/components/PostComposer.test.jsx),
[`web/src/components/LikeButton.test.jsx`](../../web/src/components/LikeButton.test.jsx)*

## The one idea

A test is a second program that uses your first program and complains when
it misbehaves. The craft is in choosing **where to stand** while testing —
each vantage point catches different bugs at a different cost:

```
        cost/realism ▲
   (few) e2e          │  a real browser drives the real app
         API tests    │  real HTTP against the real stack, fake DB   ← our backbone
  (many) component /  │  one piece in isolation, seams mocked
         unit tests   ▼
```

## Where Glassbox stands

**API tests** (`server/tests/`, 34 of them) are the backbone. `TestClient`
sends genuine HTTP through the *entire* backend — middleware, auth
dependencies, routers, services, SQL — against a throwaway database per
test (see [`conftest.py`](../../server/tests/conftest.py): a fixture is
setup-plus-teardown packaged for reuse). They assert on the **contract** —
status codes, JSON shapes, cookies — not on internals, which is why they
survive refactors: `test_like_is_idempotent` doesn't care *how* likes are
stored, only that liking twice counts once.

**Component tests** (`web/src/components/*.test.jsx`, Vitest + Testing
Library) render one React component in a fake DOM (jsdom — no browser)
with the seams mocked. `vi.mock('../api.js', …)` swaps the real network
layer for a puppet: the test decides whether the server "answers",
"refuses", or "never replies". That last one is how we test the defining
moment of optimistic UI — *the count changed and the promise hasn't
settled yet* — something almost impossible to catch reliably against a
real server.

**End-to-end**: not in the suite (a taste of it runs in CI-less form via
Playwright during development). E2e is the most realistic and the most
expensive — you keep only a few.

## Test the unhappy paths — especially the ugliest one

Half our tests are about things going wrong: wrong passwords, other
people's posts, pages that don't exist. Phase 6 adds the ugliest case —
a bug we didn't anticipate ([`test_hardening.py`](../../server/tests/test_hardening.py)).
A test-only route that just crashes lets us pin down how failure *looks*:

- the client gets the standard envelope, `500 INTERNAL`, and a message
  that leaks **nothing** (`assert "RuntimeError" not in response.text`)
- the log gets **everything** — the full traceback (asserted with pytest's
  `caplog`)

Same event, two audiences, two messages. That's error design in one test.

## Habits worth stealing

- **Arrange through the same door as production.** Test data goes in
  through the repositories, not hand-written INSERTs — if the schema
  changes, tests break loudly instead of testing a world that can't exist.
- **Each test gets a fresh world.** No test depends on another's leftovers
  (the auto-cleanup wired in `vite.config.js` exists for exactly this).
- **Name tests as claims**: `test_logout_kills_the_session_server_side`
  reads as documentation, and its failure message tells you what promise
  broke.

## Run them

```bash
cd server && python -m pytest        # 34 API + unit tests, ~8s
cd web && npm test                   # 7 component tests, ~1s
```
