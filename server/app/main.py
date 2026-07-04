"""Glassbox API — the entry point of the backend.

Phase 1 is deliberately tiny: one endpoint, `GET /api/health`, whose only
job is to prove that a browser and a Python process can talk to each other
over HTTP. Everything else the app will ever do is a variation of this
round trip. (Lesson: docs/lessons/01-the-client-server-split.md)

Run it with:  uvicorn app.main:app --reload --port 8000
`uvicorn` is the web server; this file only *describes* the app —
which URLs exist and what to answer. The split between "server program"
and "application code" is itself a standard piece of how backends work.
"""

from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="Glassbox API",
    description="A tiny message board that shows you its own internals.",
    version="0.1.0",
)


@app.get("/api/health")
def health() -> dict:
    """Report that the backend is alive.

    Nearly every real service has an endpoint like this — load balancers
    and monitoring systems call it to decide whether the server is healthy.
    Ours also returns the current server time so the frontend can show
    that each response is freshly computed, not cached.

    FastAPI converts the returned dict to JSON and sets
    `Content-Type: application/json` — open http://localhost:8000/docs
    and try it from the browser.
    """
    return {
        "status": "ok",
        "service": "glassbox-api",
        "time": datetime.now(timezone.utc).isoformat(),
    }
