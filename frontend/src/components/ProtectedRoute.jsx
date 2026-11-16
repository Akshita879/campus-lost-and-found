import { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/Auth'
import { Skeleton } from './ui'

export default function ProtectedRoute({ children }) {
  const { user, ready, setAuthOpen } = useAuth()
  const location = useLocation()

  useEffect(() => {
    if (ready && !user) setAuthOpen(true)
  }, [ready, user, setAuthOpen])

  if (!ready) {
    return <div className="mx-auto max-w-lg px-4 py-20"><Skeleton className="h-40" /></div>
  }

  if (!user) {
    return <Navigate to="/" replace state={{ from: location.pathname }} />
  }

  return children
}
