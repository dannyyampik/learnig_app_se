import { useEffect, useState } from 'react'
import { apiGet } from '../api.js'
import PostCard from '../components/PostCard.jsx'

// The feed: fetch a page of posts from the backend, render it, and let
// the user pull more. Every post you see was a row in SQLite one moment
// ago — JOINed with its author, counted for likes, and serialized to
// JSON on its way here.
export default function FeedPage() {
  const [posts, setPosts] = useState([])
  const [hasMore, setHasMore] = useState(false)
  const [page, setPage] = useState(1)
  // 'loading' covers the first fetch; 'loading-more' keeps the existing
  // posts on screen while the next page arrives.
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    // Re-runs whenever `page` changes. The `cancelled` flag ignores the
    // result if the component unmounted while the request was in flight —
    // a race you must handle any time you fetch from an effect.
    let cancelled = false
    setStatus(page === 1 ? 'loading' : 'loading-more')

    apiGet(`/posts?page=${page}`)
      .then((data) => {
        if (cancelled) return
        // Page 1 replaces the list; later pages append to it.
        setPosts((prev) => (page === 1 ? data.items : [...prev, ...data.items]))
        setHasMore(data.hasMore)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        setError(err)
        setStatus('error')
      })

    return () => {
      cancelled = true
    }
  }, [page])

  if (status === 'loading') {
    return <p className="status pending">⏳ Loading the feed…</p>
  }

  if (status === 'error') {
    return (
      <div className="card">
        <p className="status bad">❌ Couldn't load the feed: {error.message}</p>
        <p className="hint">
          Is the server running? Try:{' '}
          <code>cd server && uvicorn app.main:app --reload --port 8000</code>
        </p>
      </div>
    )
  }

  if (posts.length === 0) {
    return (
      <div className="card">
        <p>The feed is empty — the database has no posts yet.</p>
        <p className="hint">
          Give it some demo data: <code>cd server && python -m app.db.seed</code>{' '}
          then reload this page.
        </p>
      </div>
    )
  }

  return (
    <>
      <section className="feed">
        {posts.map((post) => (
          // `key` lets React match list items across re-renders; the post
          // id is perfect because the database guarantees it's unique.
          <PostCard key={post.id} post={post} />
        ))}
      </section>

      {hasMore ? (
        <button
          className="load-more"
          disabled={status === 'loading-more'}
          onClick={() => setPage(page + 1)}
        >
          {status === 'loading-more' ? 'Loading…' : 'Load more'}
        </button>
      ) : (
        <p className="hint feed-end">
          That's every post — the last page came back with{' '}
          <code>hasMore: false</code>.
        </p>
      )}
    </>
  )
}
