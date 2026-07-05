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
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("glassbox")

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
    version="1.0.0",
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)


@app.middleware("http")
async def observe(request: Request, call_next):
    """Observability middleware: wraps EVERY api request, first in, last out.

    Two jobs, same vantage point:

    * **Log** one line per request — method, path, status, duration.
      This is the heartbeat of every production service; when something
      breaks at 3am, this log is where the investigation starts.
    * **Trace** (the X-Ray): open a trace, let the whole stack run (auth
      deps, router, service, SQL — each dropping notes into it), then
      ship what was collected back to the browser in a response header.
      The frontend's api.js reads the header and feeds the X-Ray panel.

    Real systems gate tracing like this behind an environment (never
    expose internals to the public internet!). We keep it on by default
    because exposing internals is this app's entire point — set
    GLASSBOX_TRACE=0 to see the app go opaque. The log line stays on
    either way.
    """
    if not request.url.path.startswith("/api"):
        return await call_next(request)

    tracing = os.environ.get("GLASSBOX_TRACE", "1") != "0"
    if tracing:
        trace.start(request.method, request.url.path)

    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # The catch-all handler (errors.py) will turn this into a 500
        # envelope for the client; we still owe the log its line.
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "%s %s -> 500 in %.1fms", request.method, request.url.path, elapsed_ms
        )
        raise

    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "%s %s -> %s in %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    if tracing:
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
