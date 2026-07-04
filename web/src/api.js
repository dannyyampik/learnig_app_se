// The single seam between the frontend and the backend.
//
// Every request the app ever makes goes through this file. Centralizing it
// means there is exactly one place that knows about headers, cookies, and
// error handling — and later (phase 5) one place to capture X-Ray traces.

const BASE = '/api'

// A typed error so callers can distinguish "the server said no" from
// "the network is down" or a bug in our own code.
export class ApiError extends Error {
  constructor(status, code, message) {
    super(message)
    this.status = status // HTTP status code, e.g. 404
    this.code = code // machine-readable code from the error envelope
  }
}

export async function apiGet(path) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { Accept: 'application/json' },
    // Send cookies with every request — this is how the session cookie
    // (phase 3) will travel. Harmless before then.
    credentials: 'include',
  })

  if (!response.ok) {
    // The design says all errors share one JSON shape; fall back to the
    // status text for anything that doesn't (e.g. a proxy error page).
    const body = await response.json().catch(() => null)
    const err = body?.error
    throw new ApiError(
      response.status,
      err?.code ?? 'UNKNOWN',
      err?.message ?? response.statusText,
    )
  }

  return response.json()
}
