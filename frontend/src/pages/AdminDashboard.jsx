import { useCallback, useEffect, useState } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { Trash2, Users, ClipboardList, Eraser } from 'lucide-react'
import { useAuth } from '../context/Auth'
import { Button, Card, Skeleton, Badge } from '../components/ui'
import {
  adminClearReports,
  adminDeleteReport,
  adminDeleteUser,
  adminListReports,
  adminListUsers,
} from '../services/adminApi'

export default function AdminDashboard() {
  const { user, ready } = useAuth()
  const [tab, setTab] = useState('reports')
  const [reports, setReports] = useState(null)
  const [users, setUsers] = useState(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    setErr('')
    try {
      const [r, u] = await Promise.all([adminListReports(), adminListUsers()])
      setReports(r)
      setUsers(u)
    } catch (e) {
      setErr(e.message)
    }
  }, [])

  useEffect(() => {
    if (ready && user?.is_admin) load()
  }, [ready, user, load])

  if (!ready) return <div className="mx-auto max-w-5xl px-4 py-10"><Skeleton className="h-64" /></div>
  if (!user?.is_admin) return <Navigate to="/admin/login" replace />

  const removeReport = async (id) => {
    if (!confirm(`Delete report #${id}?`)) return
    setBusy(true)
    try {
      await adminDeleteReport(id)
      await load()
    } catch (e) { setErr(e.message) }
    finally { setBusy(false) }
  }

  const removeUser = async (id, name) => {
    if (!confirm(`Delete user ${name} (#${id})? Their reports will also be removed.`)) return
    setBusy(true)
    try {
      await adminDeleteUser(id)
      await load()
    } catch (e) { setErr(e.message) }
    finally { setBusy(false) }
  }

  const clearAll = async () => {
    if (!confirm('Delete ALL lost/found listings, claims, and notifications? Users stay.')) return
    setBusy(true)
    try {
      const res = await adminClearReports()
      alert(`Cleared ${res.deleted_reports} reports, ${res.deleted_claims} claims, ${res.deleted_notifications} notifications.`)
      await load()
    } catch (e) { setErr(e.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 lg:px-8">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-primary">Admin portal</p>
          <h1 className="text-3xl font-bold">Campus control</h1>
          <p className="mt-1 text-sm text-on-surface-variant">Signed in as {user.name} ({user.email})</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={clearAll} disabled={busy}><Eraser size={16} /> Clear all listings</Button>
          <Button to="/explore" variant="ghost">Student site</Button>
        </div>
      </div>

      {err && <p role="alert" className="mb-4 rounded-lg bg-error-container/50 p-3 text-sm text-error">{err}</p>}

      <div className="mb-4 flex rounded-lg bg-surface-low p-1 w-fit">
        {[['reports', 'Listings', ClipboardList], ['users', 'Users', Users]].map(([v, l, I]) => (
          <button key={v} type="button" onClick={() => setTab(v)}
            className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold ${tab === v ? 'bg-white shadow-card' : 'text-on-surface-variant'}`}>
            <I size={16} />{l}
          </button>
        ))}
      </div>

      {tab === 'reports' && (
        <Card className="overflow-hidden">
          <div className="border-b border-slate-200 px-4 py-3 font-semibold">
            All lost &amp; found reports ({reports ? reports.length : '…'})
          </div>
          {!reports ? <div className="p-4"><Skeleton className="h-40" /></div> : (
            <div className="divide-y divide-slate-100">
              {reports.length === 0 && <p className="p-4 text-sm text-on-surface-variant">No listings.</p>}
              {reports.map(r => (
                <div key={r.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge tone={r.type === 'found' ? 'teal' : 'slate'}>{r.type === 'found' ? 'Found' : 'Lost'}</Badge>
                      <span className="font-semibold">#{r.id} {r.title}</span>
                    </div>
                    <p className="mt-0.5 truncate text-sm text-on-surface-variant">{r.category} · {r.location} · {r.status}</p>
                  </div>
                  <Button variant="secondary" disabled={busy} onClick={() => removeReport(r.id)}>
                    <Trash2 size={14} /> Delete
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {tab === 'users' && (
        <Card className="overflow-hidden">
          <div className="border-b border-slate-200 px-4 py-3 font-semibold">
            Users ({users ? users.length : '…'})
          </div>
          {!users ? <div className="p-4"><Skeleton className="h-40" /></div> : (
            <div className="divide-y divide-slate-100">
              {users.map(u => (
                <div key={u.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
                  <div>
                    <p className="font-semibold">{u.name} {u.is_admin && <Badge tone="amber">Admin</Badge>}</p>
                    <p className="text-sm text-on-surface-variant">{u.email} · {u.reports_count} reports · {u.claims_count} claims</p>
                  </div>
                  {!u.is_admin && (
                    <Button variant="secondary" disabled={busy} onClick={() => removeUser(u.id, u.name)}>
                      <Trash2 size={14} /> Remove user
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
