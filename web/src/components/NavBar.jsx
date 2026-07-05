import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function NavBar() {
  const { user, logout } = useAuth()

  return (
    <header className="nav">
      <Link to="/" className="brand">
        🔍 Glassbox
      </Link>
      <nav className="nav-right">
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
          API docs
        </a>
        {user === undefined ? null : user ? (
          <>
            <span className="nav-user">@{user.username}</span>
            <button className="linklike" onClick={logout}>
              log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">log in</Link>
            <Link to="/signup">sign up</Link>
          </>
        )}
      </nav>
    </header>
  )
}
