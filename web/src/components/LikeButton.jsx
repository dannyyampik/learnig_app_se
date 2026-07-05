import { useState } from 'react'
import { apiDelete, apiPut } from '../api.js'
import { useAuth } from '../context/AuthContext.jsx'

// The optimistic-UI lesson, in one component.
//
// Clicking updates the heart IMMEDIATELY — before the server has said
// anything — then sends the request. If the request fails, we roll back
// to what the server last told us. The UI feels instant; the server
// stays the source of truth. Watch the Network tab: the heart fills
// *before* the PUT completes.
export default function LikeButton({ post }) {
  const { user } = useAuth()
  const [state, setState] = useState({
    liked: post.likedByMe,
    count: post.likeCount,
  })

  async function toggle() {
    const before = state
    const optimistic = {
      liked: !before.liked,
      count: before.count + (before.liked ? -1 : 1),
    }
    setState(optimistic) // 1. update the screen now

    try {
      // 2. tell the server. PUT/DELETE are idempotent, so even a
      //    double-click that fires twice can't over-count.
      if (optimistic.liked) await apiPut(`/posts/${post.id}/like`)
      else await apiDelete(`/posts/${post.id}/like`)
    } catch {
      setState(before) // 3. the server said no — undo the lie
    }
  }

  return (
    <button
      className={state.liked ? 'like liked' : 'like'}
      onClick={toggle}
      disabled={!user}
      title={user ? undefined : 'Log in to like posts'}
    >
      ♥ {state.count}
    </button>
  )
}
