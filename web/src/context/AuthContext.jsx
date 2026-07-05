import { createContext, useContext, useEffect, useState } from 'react'
import { apiGet, apiPost } from '../api.js'

// Session state — "who is logged in?" — is needed by the nav bar, the
// feed, the auth pages… Passing it down as props through every layer
// would be miserable, so it lives in a React context: define it once,
// read it anywhere with useAuth().
//
// Three possible values for `user`:
//   undefined → still asking the server (first render)
//   null      → asked; nobody is logged in
//   {…}       → the logged-in user

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(undefined)

  useEffect(() => {
    // The cookie survives page reloads; React state does not. On every
    // load we ask the server "who am I?" and let the cookie answer.
    apiGet('/auth/me')
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  async function signup(username, password) {
    setUser(await apiPost('/auth/signup', { username, password }))
  }

  async function login(username, password) {
    setUser(await apiPost('/auth/login', { username, password }))
  }

  async function logout() {
    await apiPost('/auth/logout')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
