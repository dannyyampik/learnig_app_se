import { useState } from 'react'
import { apiPost } from '../api.js'

// The write path: a controlled textarea, client-side length feedback,
// and POST /api/posts on submit. The server re-validates everything —
// this counter is a courtesy, not a defense (anyone can curl the API).
export default function PostComposer({ onCreated }) {
  const [body, setBody] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const remaining = 280 - body.length
  const valid = body.length >= 1 && remaining >= 0

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      // The 201 response carries the post exactly as the feed shows it,
      // so the parent can prepend it without refetching the whole feed.
      const post = await apiPost('/posts', { body })
      setBody('')
      onCreated(post)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Say something (max 280 chars)…"
        rows={3}
      />
      <div className="composer-foot">
        <span className={remaining < 0 ? 'counter over' : 'counter'}>
          {remaining}
        </span>
        <button type="submit" disabled={!valid || busy}>
          {busy ? '…' : 'Post'}
        </button>
      </div>
      {error && <p className="status bad">{error}</p>}
    </form>
  )
}
