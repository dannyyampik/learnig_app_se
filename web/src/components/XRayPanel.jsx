import { useState } from 'react'
import { useXRay } from '../context/XRayContext.jsx'

// The X-Ray panel: every request the app has made, and what the server
// did to answer it — the route, the auth steps, the SQL, the timings.
// This is the app showing you its own internals; press ` to toggle.

function statusClass(status) {
  if (status >= 500) return 'xray-status s5'
  if (status >= 400) return 'xray-status s4'
  return 'xray-status s2'
}

function Entry({ entry }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <li className="xray-entry">
      <button className="xray-summary" onClick={() => setExpanded(!expanded)}>
        <span className="xray-method">{entry.method}</span>
        <span className="xray-path">{entry.path}</span>
        <span className={statusClass(entry.status)}>{entry.status}</span>
        <span className="xray-ms">{entry.durationMs}ms</span>
      </button>

      {expanded && (
        <div className="xray-detail">
          {entry.steps.length > 0 && (
            <>
              <h4>server steps</h4>
              <ul>
                {entry.steps.map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            </>
          )}
          <h4>SQL ({entry.sql.length})</h4>
          {entry.sql.length === 0 ? (
            <p className="xray-none">no queries — this endpoint never touched the database</p>
          ) : (
            <ul>
              {entry.sql.map((q, i) => (
                <li key={i}>
                  <span className="xray-ms">{q.ms}ms</span> {q.query}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
  )
}

export default function XRayPanel() {
  const { entries, open, toggle, clear } = useXRay()

  if (!open) return null

  return (
    <aside className="xray">
      <div className="xray-head">
        <strong>🩻 X-Ray</strong>
        <span className="xray-hint">every request, traced · press ` to hide</span>
        <span className="xray-actions">
          <button className="linklike" onClick={clear}>
            clear
          </button>
          <button className="linklike" onClick={toggle}>
            ✕
          </button>
        </span>
      </div>
      {entries.length === 0 ? (
        <p className="xray-none">
          No requests yet. Do anything — load the feed, like a post — and
          its full server-side story appears here.
        </p>
      ) : (
        <ul className="xray-list">
          {entries.map((entry) => (
            <Entry key={entry.id} entry={entry} />
          ))}
        </ul>
      )}
    </aside>
  )
}
