"""The X-Ray trace collector — miniature distributed tracing.

While a request is being handled, anything in the app can drop a note
here ("ran this SQL in 2ms", "resolved session → @alice"). The middleware
in main.py opens a trace when a request arrives and closes it when the
response leaves, shipping the collected notes to the browser in a
response header. (Lesson: docs/lessons/06-observability-and-tracing.md)

The one piece of machinery: a ``ContextVar``. It's like a global variable
that is *per request* — two requests being handled at the same time each
see their own trace, never each other's. This is exactly the problem real
tracing systems (OpenTelemetry etc.) solve with "context propagation".
"""

import contextvars
import re
import time

_current: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "glassbox_trace", default=None
)


def start(method: str, path: str) -> None:
    _current.set(
        {
            "method": method,
            "path": path,
            "steps": [],
            "sql": [],
            "started": time.perf_counter(),
        }
    )


def add_step(label: str) -> None:
    """A breadcrumb from anywhere in the request's path (auth, services…)."""
    trace = _current.get()
    if trace is not None:
        trace["steps"].append(label)


def add_sql(query: str, duration_ms: float) -> None:
    trace = _current.get()
    if trace is not None:
        trace["sql"].append(
            {
                # collapse whitespace so multi-line queries read as one line
                "query": re.sub(r"\s+", " ", query).strip(),
                "ms": round(duration_ms, 2),
            }
        )


def finish(status: int) -> dict | None:
    """Close the trace and return everything collected, ready for the header."""
    trace = _current.get()
    if trace is None:
        return None
    _current.set(None)
    return {
        "method": trace["method"],
        "path": trace["path"],
        "status": status,
        "durationMs": round((time.perf_counter() - trace["started"]) * 1000, 1),
        "steps": trace["steps"],
        "sql": trace["sql"],
    }
