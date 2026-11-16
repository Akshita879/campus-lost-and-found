import { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchMe, login as apiLogin, logout as apiLogout, register as apiRegister } from '../services/authApi'

const Ctx = createContext(null)
export const useAuth = () => useContext(Ctx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)
  const [authOpen, setAuthOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchMe().then(u => { setUser(u); setReady(true) })
  }, [])

  const login = async (creds, { redirectTo } = {}) => {
    const data = await apiLogin({
      email: String(creds.email || '').trim().toLowerCase(),
      password: creds.password,
    })
    setUser(data.user)
    setAuthOpen(false)
    if (redirectTo !== null) {
      navigate(redirectTo || (data.user?.is_admin ? '/admin' : '/explore'), { replace: true })
    }
    return data.user
  }

  const register = async (payload) => {
    const email = String(payload.email || '').trim().toLowerCase()
    await apiRegister({ ...payload, email })
    return login({ email, password: payload.password })
  }

  const logout = () => {
    apiLogout()
    setUser(null)
    navigate('/', { replace: true })
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
