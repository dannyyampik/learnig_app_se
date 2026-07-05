# Glassbox

> A tiny social message board that shows you its own internals — built to
> learn how applications work, one layer at a time.

📖 **Start here:** [DESIGN.md](./DESIGN.md) explains the whole system and why
every piece exists. Concept explainers live in [docs/lessons/](./docs/lessons/).

## What's here so far

| Phase | Status | What it adds |
|---|---|---|
| 1. Skeleton | ✅ | FastAPI backend + React frontend talking over HTTP |
| 2. Data layer | ✅ | SQLite, migrations, repositories, a real paginated feed |
| 3. Auth | ✅ | Signup/login, bcrypt, sessions, cookies |
| 4. Core features | ✅ | Posting, deleting, optimistic likes, profiles |
| 5. X-Ray panel | ✅ | Live request-lifecycle inspector (press `` ` ``) |
| 6. Hardening | ✅ | Request log, 500 envelope, frontend tests |

## Running it

You need **Python 3.10+** and **Node 18+**. The app is two programs — a
backend and a frontend — run in two terminals. (That's the first lesson:
see [docs/lessons/01-the-client-server-split.md](./docs/lessons/01-the-client-server-split.md).)

**Terminal 1 — the backend (Python):**

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -e ".[dev]"                              # first time only
python -m app.db.seed    # demo data (optional, once) — log in as alice/password123
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — the frontend (JavaScript):**

```bash
cd web
npm install        # first time only
npm run dev
```

Then open:

- **<http://localhost:5173>** — the app
- **<http://localhost:8000/docs>** — the API playground (FastAPI generates
  this for free; try calling `/api/health` from it)

## Running the tests

```bash
cd server && source .venv/bin/activate && python -m pytest   # 34 backend tests
cd web && npm test                                           # 7 component tests
```

## The lessons

One short page per concept, each linked from the code that demonstrates it:

1. [The client/server split](docs/lessons/01-the-client-server-split.md)
2. [SQL and the schema](docs/lessons/02-sql-and-the-schema.md)
3. [The layered backend](docs/lessons/03-the-layered-backend.md)
4. [Auth: passwords, sessions, cookies](docs/lessons/04-auth-sessions-and-cookies.md)
5. [REST, idempotency, optimistic UI](docs/lessons/05-rest-idempotency-and-optimistic-ui.md)
6. [Observability and tracing](docs/lessons/06-observability-and-tracing.md)
7. [Testing the stack](docs/lessons/07-testing-the-stack.md)

## Where to go next

All six phases of [the design](DESIGN.md) are built. Each future extension
in [DESIGN.md §12](DESIGN.md#12-build-plan--6-phases) is a system-design
lesson waiting to happen: swap SQLite for Postgres (the repository layer
earns its keep), JWT vs sessions, WebSockets for a live feed, caching,
rate limiting, Docker.
