// One post in the feed. Purely presentational: it receives a post object
// (already fetched by FeedPage) and renders it. Components like this are
// easy to reuse and easy to test because they hold no state of their own.

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

export default function PostCard({ post }) {
  return (
    <article className="post">
      <div className="post-head">
        <strong>@{post.author}</strong>
        <time dateTime={post.createdAt} title={post.createdAt}>
          {timeAgo(post.createdAt)}
        </time>
      </div>
      {/* React escapes post.body automatically — a post containing
          <script> renders as text, not code. That's XSS protection
          working silently on our behalf. */}
      <p className="post-body">{post.body}</p>
      <div className="post-foot">
        <button
          className="like"
          disabled
          title="Liking needs an account — that's phase 3"
        >
          ♥ {post.likeCount}
        </button>
      </div>
    </article>
  )
}
