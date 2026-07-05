import { useState } from 'react'

// The shared shape of the login and signup forms: two fields, a submit
// button, and a place to show the server's objection. The page that
// renders it decides what "submit" means.
export default function AuthForm({ title, submitLabel, hint, onSubmit }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    // Stop the browser's built-in form behavior (a full-page POST +
    // reload); we make the request ourselves and stay on the page.
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await onSubmit(username, password)
    } catch (err) {
      // The server said no — an ApiError with a human-readable message
      // from the error envelope (409 taken, 401 wrong password, 400 …).
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <form className="card auth-form" onSubmit={handleSubmit}>
      <h2>{title}</h2>
      <label>
        username
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          autoFocus
          required
        />
      </label>
      <label>
        password
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </label>
      {error && <p className="status bad">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? '…' : submitLabel}
      </button>
      {hint}
    </form>
  )
}
