"""Glassbox API — the entry point of the backend.

This file only *assembles* the app: wire up routers, error handlers, and
startup work. The interesting code lives a layer down —

    routers/       HTTP in, JSON out
    services/      business rules
    db/            SQL and the database

Run it with:  uvicorn app.main:app --reload --port 8000
(`uvicorn` is the web server; this module just describes the app.)
"""

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request

from . import trace
from .db import database
from .errors import register_error_handlers
from .routers import auth, posts, users


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
    version="0.5.0",
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)


@app.middleware("http")
async def xray(request: Request, call_next):
    """The X-Ray middleware: wraps EVERY api request, first in, last out.

    Open a trace, let the whole stack run (auth deps, router, service,
    SQL — each dropping notes into the trace), then ship what was
    collected back to the browser in a response header. The frontend's
    api.js reads the header and feeds the X-Ray panel.

    Real systems gate observability like this behind an environment
    (never expose internals to the public internet!). We keep it on by
    default because exposing internals is this app's entire point —
    set GLASSBOX_TRACE=0 to see the app go opaque.
    """
    if os.environ.get("GLASSBOX_TRACE", "1") == "0" or not request.url.path.startswith(
        "/api"
    ):
        return await call_next(request)

    trace.start(request.method, request.url.path)
    response = await call_next(request)
    collected = trace.finish(response.status_code)
    if collected is not None:
        response.headers["X-Glassbox-Trace"] = json.dumps(collected)
    return response


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
