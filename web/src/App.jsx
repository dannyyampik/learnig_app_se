import { BrowserRouter, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import FeedPage from './pages/FeedPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SignupPage from './pages/SignupPage.jsx'

// App is the frame: auth state on the outside, router inside it, pages
// within. Client-side routing means the URL changes and components swap
// WITHOUT asking the server for a new page — watch the Network tab while
// you click between / and /login: no document loads, only API calls.
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </AuthProvider>
  )
}

function Shell() {
  const { user } = useAuth()

  return (
    <>
      <NavBar />
      <main className="page">
        <Routes>
          {/* key: when the viewer changes (login/logout), remount the
              feed so likedByMe is refetched for the new viewer. */}
          <Route path="/" element={<FeedPage key={user?.id ?? 'anon'} />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="*"
            element={<p className="status bad">404 — no such page.</p>}
          />
        </Routes>
      </main>
    </>
  )
}
