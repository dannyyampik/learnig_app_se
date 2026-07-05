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
| 3. Auth | ⏳ | Signup/login, sessions, cookies |
| 4. Core features | ⏳ | Posting, likes, profiles, pagination |
| 5. X-Ray panel | ⏳ | Live request-lifecycle inspector |
| 6. Hardening | ⏳ | Tests, error envelope, polish |

## Running it

You need **Python 3.10+** and **Node 18+**. The app is two programs — a
backend and a frontend — run in two terminals. (That's the first lesson:
see [docs/lessons/01-the-client-server-split.md](./docs/lessons/01-the-client-server-split.md).)

**Terminal 1 — the backend (Python):**

```bash
cd server
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -e ".[dev]"                              # first time only
python -m app.db.seed                                # demo data (optional, once)
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
cd server && source .venv/bin/activate && python -m pytest
```
