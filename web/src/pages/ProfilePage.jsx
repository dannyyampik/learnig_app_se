import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiGet } from '../api.js'
import PostCard from '../components/PostCard.jsx'

// /u/:username — the router extracts the username from the URL
// (useParams), and we ask the API for that user's profile. Same
// three-state fetch pattern as the feed.
export default function ProfilePage() {
  const { username } = useParams()
  const [state, setState] = useState({ status: 'loading' })

  useEffect(() => {
    let cancelled = false
    setState({ status: 'loading' })
    apiGet(`/users/${username}`)
      .then((profile) => !cancelled && setState({ status: 'ready', profile }))
      .catch((error) => !cancelled && setState({ status: 'error', error }))
    return () => {
      cancelled = true
    }
  }, [username]) // refetch when the URL's username changes

  if (state.status === 'loading') {
    return <p className="status pending">⏳ Loading @{username}…</p>
  }

  if (state.status === 'error') {
    // A 404 here is a *normal* outcome (someone typed a bad URL), so the
    // page handles it as content, not as a crash.
    return (
      <div className="card">
        <p className="status bad">
          {state.error.status === 404
            ? `No user called @${username}.`
            : `Couldn't load this profile: ${state.error.message}`}
        </p>
      </div>
    )
  }

  const { profile } = state
  return (
    <>
      <section className="card profile-head">
        <h2>@{profile.username}</h2>
        <p className="hint">
          {profile.postCount} posts · {profile.likesReceived} likes received ·
          joined {new Date(profile.createdAt).toLocaleDateString()}
        </p>
      </section>
      <section className="feed">
        {profile.posts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            onDeleted={(id) =>
              setState((s) => ({
                ...s,
                profile: {
                  ...s.profile,
                  postCount: s.profile.postCount - 1,
                  posts: s.profile.posts.filter((p) => p.id !== id),
                },
              }))
            }
          />
        ))}
        {profile.posts.length === 0 && (
          <p className="hint">No posts yet.</p>
        )}
      </section>
    </>
  )
}
