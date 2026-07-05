import { Link } from 'react-router-dom'
import { apiDelete } from '../api.js'
import { useAuth } from '../context/AuthContext.jsx'
import LikeButton from './LikeButton.jsx'

// One post in the feed (or on a profile). Mostly presentational — the
// only actions are the like button (its own component) and deleting
// your own posts.

function timeAgo(isoString) {
  // The backend sends an absolute UTC timestamp; turning it into "5m ago"
  // is presentation, so it belongs here on the client.
  const seconds = Math.floor((Date.now() - new Date(isoString)) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function PostCard({ post, onDeleted }) {
  const { user } = useAuth()
  const isMine = user && user.username === post.author

  async function handleDelete() {
    // The server is the real judge of "is this yours?" (403 if not) —
    // hiding the button for others is UI politeness, not security.
    await apiDelete(`/posts/${post.id}`)
    onDeleted?.(post.id)
  }

  return (
    <article className="post">
      <div className="post-head">
        <Link to={`/u/${post.author}`} className="author-link">
          @{post.author}
        </Link>
        <span className="post-head-right">
          <time dateTime={post.createdAt} title={post.createdAt}>
            {timeAgo(post.createdAt)}
          </time>
          {isMine && (
            <button
              className="delete"
              onClick={handleDelete}
              title="Delete this post"
            >
              ✕
            </button>
          )}
        </span>
      </div>
      {/* React escapes post.body automatically — a post containing
          <script> renders as text, not code. That's XSS protection
          working silently on our behalf. */}
      <p className="post-body">{post.body}</p>
      <div className="post-foot">
        <LikeButton key={`${post.id}-${post.likedByMe}`} post={post} />
      </div>
    </article>
  )
}
