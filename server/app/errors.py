"""One place where failures become HTTP responses.

The design promises every error the same JSON shape:

    { "error": { "code": "...", "message": "...", "details": [...] } }

Handlers registered here enforce that promise, so no route ever
hand-crafts an error response.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(status: int, code: str, message: str, details: list | None = None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Bad input → 400 with a readable list of what's wrong where.

    FastAPI raises this before our route code even runs — the framework
    checked the request against the declared types (e.g. ``page: int >= 1``)
    and it didn't fit.
    """
    details = [
        {
            # e.g. "query.page" or "body.body" — where in the request
            "field": ".".join(str(part) for part in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return error_response(400, "VALIDATION", "Invalid request.", details)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
