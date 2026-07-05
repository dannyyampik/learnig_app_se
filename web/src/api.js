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

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { Accept: 'application/json', ...options.headers },
    // Send cookies with every request — this is how the session cookie
    // travels. The browser attaches it; we just don't opt out.
    credentials: 'include',
    ...options,
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

  // 204 No Content has no body to parse (e.g. logout).
  if (response.status === 204) return null
  return response.json()
}

export function apiGet(path) {
  return request(path)
}

export function apiPost(path, body) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
}
