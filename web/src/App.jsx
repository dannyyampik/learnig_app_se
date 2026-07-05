import FeedPage from './pages/FeedPage.jsx'

// App is the frame: header + whichever page is showing. There's only one
// page so far; client-side routing arrives when we have a second one.
export default function App() {
  return (
    <>
      <header className="nav">
        <span className="brand">🔍 Glassbox</span>
        <span className="nav-note">
          phase 2 — real data ·{' '}
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
            API docs
          </a>
        </span>
      </header>
      <main className="page">
        <FeedPage />
      </main>
    </>
  )
}
