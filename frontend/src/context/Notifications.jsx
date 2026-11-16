import { createContext, useContext, useState, useCallback } from 'react'
import { USE_MOCKS } from '../services/api'
import { NOTIFICATIONS } from '../data/items'
const Ctx = createContext(null)
export const useNotifications = () => useContext(Ctx)
export function NotificationsProvider({ children }) {
  const [list, setList] = useState(USE_MOCKS ? NOTIFICATIONS : [])
  const markRead = id => setList(l => l.map(n => n.id === id ? { ...n, read: true } : n))
  const markAll = () => setList(l => l.map(n => ({ ...n, read: true })))
  const push = useCallback((n) => {
    setList(l => [{ id: Date.now(), read: false, time: 'Just now', ...n }, ...l])
  }, [])
  return <Ctx.Provider value={{ list, unread: list.filter(n => !n.read).length, markRead, markAll, push }}>{children}</Ctx.Provider>
}
