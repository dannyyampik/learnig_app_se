import { useEffect, useState } from 'react'
import { apiGet } from './api.js'

// Phase 1: prove the whole round trip works.
//
//   this component (browser) → api.js → fetch → vite proxy →
//   FastAPI /api/health → JSON response → back into React state → screen
//
// The three-state pattern below (loading / error / data) is the beating
// heart of frontend work: server data is never instantly there, and it
// can always fail. We model both honestly instead of pretending.

export default function App() {
  const [state, setState] = useState({ status: 'loading' })

  useEffect(() => {
    // useEffect with [] runs once, right after the component first renders:
    // the standard place to kick off an initial data fetch.
    apiGet('/health')
      .then((data) => setState({ status: 'ready', data }))
      .catch((error) => setState({ status: 'error', error }))
  }, [])

  return (
    <main className="page">
      <h1>🔍 Glassbox</h1>
      <p className="tagline">A little app that shows you how apps work.</p>

      <section className="card">
        <h2>Phase 1 — the round trip</h2>
        <p>
          This page is React running <strong>in your browser</strong>. Below
          is what happened when it asked the <strong>Python backend</strong>{' '}
          how it's doing:
        </p>

        {state.status === 'loading' && (
          <p className="status pending">⏳ Asking the backend…</p>
        )}

        {state.status === 'error' && (
          <div>
            <p className="status bad">❌ The backend didn't answer: {state.error.message}</p>
            <p className="hint">
              Is the server running? Try:{' '}
              <code>cd server && uvicorn app.main:app --reload --port 8000</code>
            </p>
          </div>
        )}

        {state.status === 'ready' && (
          <div>
            <p className="status good">✅ Backend says: {state.data.status}</p>
            <p className="hint">
              Raw JSON it sent over the wire:
            </p>
            <pre>{JSON.stringify(state.data, null, 2)}</pre>
            <p className="hint">
              Reload the page — the <code>time</code> field changes because
              the Python server computes each response fresh.
            </p>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Poke at it</h2>
        <ul>
          <li>
            Open <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            the API playground</a> — the backend documents itself.
          </li>
          <li>
            Open your browser's DevTools → Network tab and reload: you'll see
            the <code>health</code> request this page made.
          </li>
          <li>
            Stop the Python server and reload this page to see the error
            state — the frontend keeps working even when the backend is gone.
          </li>
        </ul>
      </section>
    </main>
  )
}
