import { Link, Navigate, useNavigate } from 'react-router-dom'
import AuthForm from '../components/AuthForm.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()

  // Already logged in? This page has nothing for you — bounce home.
  if (user) return <Navigate to="/" replace />

  return (
    <AuthForm
      title="Log in"
      submitLabel="log in"
      onSubmit={async (username, password) => {
        await login(username, password)
        navigate('/')
      }}
      hint={
        <p className="hint">
          No account? <Link to="/signup">Sign up</Link>. Seeded the demo
          data? Try <code>alice</code> / <code>password123</code>.
        </p>
      }
    />
  )
}
