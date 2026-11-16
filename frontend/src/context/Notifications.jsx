import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { USE_MOCKS } from '../services/api'
import { useAuth } from './Auth'
import { listNotifications, markAllNotificationsRead } from '../services/notificationsApi'

const Ctx = createContext(null)
export const useNotifications = () => useContext(Ctx)

export function NotificationsProvider({ children }) {
  const { user, ready } = useAuth()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (USE_MOCKS || !user) {
      setList([])
      return
    }
    setLoading(true)
    try {
      const data = await listNotifications()
      setList(data.notifications || [])
    } catch (err) {
      console.error('Failed to load notifications', err)
      setList([])
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    if (!ready) return
    refresh()
  }, [ready, refresh])

  const markAll = async () => {
    if (!user) return
    try {
      const data = await markAllNotificationsRead()
      setList(data.notifications)
    } catch {
      setList(l => l.map(n => ({ ...n, read: true })))
    }
  }

  return (
    <Ctx.Provider value={{
      list,
      unread: list.filter(n => !n.read).length,
      loading,
      refresh,
      markAll,
    }}>
      {children}
    </Ctx.Provider>
  )
}
