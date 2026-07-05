import { Link, Navigate, useNavigate } from 'react-router-dom'
import AuthForm from '../components/AuthForm.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export default function SignupPage() {
  const { user, signup } = useAuth()
  const navigate = useNavigate()

  if (user) return <Navigate to="/" replace />

  return (
    <AuthForm
      title="Create an account"
      submitLabel="sign up"
      onSubmit={async (username, password) => {
        await signup(username, password)
        navigate('/')
      }}
      hint={
        <p className="hint">
          3–20 letters/digits/underscores; password 8+ characters. Already
          have one? <Link to="/login">Log in</Link>.
        </p>
      }
    />
  )
}
