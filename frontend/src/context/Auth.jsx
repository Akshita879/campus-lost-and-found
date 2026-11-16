import { createContext, useContext, useEffect, useState } from 'react'
import { fetchMe, login as apiLogin, logout as apiLogout, register as apiRegister } from '../services/authApi'

const Ctx = createContext(null)
export const useAuth = () => useContext(Ctx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)

  useEffect(() => {
    fetchMe().then(u => { setUser(u); setReady(true) })
  }, [])

  const login = async (creds) => {
    const data = await apiLogin(creds)
    setUser(data.user)
    setAuthOpen(false)
    return data.user
  }

  const register = async (payload) => {
    await apiRegister(payload)
    return login({ email: payload.email, password: payload.password })
  }

  const logout = () => {
    apiLogout()
    setUser(null)
  }

  const requireAuth = () => {
    if (user) return true
    setAuthOpen(true)
    return false
  }

  return (
    <Ctx.Provider value={{ user, ready, authOpen, setAuthOpen, login, register, logout, requireAuth }}>
      {children}
    </Ctx.Provider>
  )
}
