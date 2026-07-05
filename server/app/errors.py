"""One place where failures become HTTP responses.

The design promises every error the same JSON shape:

    { "error": { "code": "...", "message": "...", "details": [...] } }

Two kinds of failure flow through here:

* **Validation** — FastAPI rejected the request before our code ran.
* **AppError** — a *business* rule said no. Services raise these without
  knowing anything about HTTP; the handler below translates them to a
  status code in exactly one place. No route ever calls
  ``JSONResponse(status_code=...)`` by hand.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("glassbox")


class AppError(Exception):
    """Base class for 'the rules say no'. Subclasses pin the status/code."""

    status = 500
    code = "INTERNAL"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UnauthorizedError(AppError):
    """401 — we don't know who you are (log in first)."""

    status = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    """403 — we know who you are, and you still can't do that."""

    status = 403
    code = "FORBIDDEN"


class NotFoundError(AppError):
    """404 — no such thing."""

    status = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    """409 — collides with something that already exists."""

    status = 409
    code = "CONFLICT"


def error_response(status: int, code: str, message: str, details: list | None = None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


async def app_error_handler(request: Request, exc: AppError):
    return error_response(exc.status, exc.code, exc.message)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Bad input → 400 with a readable list of what's wrong where.

    FastAPI raises this before our route code even runs — the framework
    checked the request against the declared types (e.g. ``page: int >= 1``)
    and it didn't fit.
    """
    details = [
        {
            # e.g. "query.page" or "body.password" — where in the request
            "field": ".".join(str(part) for part in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return error_response(400, "VALIDATION", "Invalid request.", details)


async def unexpected_error_handler(request: Request, exc: Exception):
    """The last line of defense: a bug we didn't anticipate.

    Two audiences, two very different messages. *We* get the full
    traceback in the server log; *the client* gets the envelope with a
    deliberately vague message — internals in error responses (stack
    traces, table names, file paths) are a classic information leak.
    """
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return error_response(500, "INTERNAL", "Something went wrong on our side.")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    # Exception (the catch-all) is special-cased by Starlette: it runs in
    # the outermost middleware, after ours has already seen the failure.
    app.add_exception_handler(Exception, unexpected_error_handler)
