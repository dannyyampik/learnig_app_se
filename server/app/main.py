"""Glassbox API — the entry point of the backend.

This file only *assembles* the app: wire up routers, error handlers, and
startup work. The interesting code lives a layer down —

    routers/       HTTP in, JSON out
    services/      business rules
    db/            SQL and the database

Run it with:  uvicorn app.main:app --reload --port 8000
(`uvicorn` is the web server; this module just describes the app.)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from .db import database
from .errors import register_error_handlers
from .routers import posts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: make sure the database schema is current before we accept
    # a single request. Code before `yield` runs at startup, code after
    # it at shutdown.
    conn = database.connect()
    applied = database.apply_migrations(conn)
    conn.close()
    if applied:
        print(f"Applied migrations: {', '.join(applied)}")
    yield


app = FastAPI(
    title="Glassbox API",
    description="A tiny message board that shows you its own internals.",
    version="0.2.0",
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(posts.router)


@app.get("/api/health")
def health() -> dict:
    """Report that the backend is alive.

    Nearly every real service has an endpoint like this — load balancers
    and monitoring systems call it to decide whether the server is healthy.
    The current server time proves each response is freshly computed.
    """
    return {
        "status": "ok",
        "service": "glassbox-api",
        "time": datetime.now(timezone.utc).isoformat(),
    }
