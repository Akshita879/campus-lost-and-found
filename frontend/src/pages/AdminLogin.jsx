import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Button, Card } from '../components/ui'
import { useAuth } from '../context/Auth'
import { apiErrorMessage } from '../lib/mappers'

export default function AdminLogin() {
  const nav = useNavigate()
  const { login, logout } = useAuth()
  const [email, setEmail] = useState('admin@campus.edu')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const submit = async e => {
    e.preventDefault()
    setErr(''); setBusy(true)
    try {
      const user = await login(
        { email: email.trim().toLowerCase(), password },
        { redirectTo: null },
      )
      if (!user?.is_admin) {
        logout()
        throw new Error('This account is not an admin.')
      }
      nav('/admin', { replace: true })
    } catch (x) {
      setErr(apiErrorMessage(x, x.message || 'Admin login failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-12">
      <Card className="p-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary">Campus admin</p>
        <h1 className="mt-2 text-2xl font-bold">Admin sign in</h1>
        <p className="mt-1 text-sm text-on-surface-variant">Manage listings and users for FindIt.</p>
        <form onSubmit={submit} className="mt-5 space-y-3">
          <label className="block"><span className="mb-1 block text-sm font-semibold">Admin email</span>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></label>
          <label className="block"><span className="mb-1 block text-sm font-semibold">Password</span>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} /></label>
          {err && <p role="alert" className="rounded-lg bg-error-container/50 p-3 text-sm text-error">{err}</p>}
          <Button type="submit" loading={busy} className="w-full">Enter admin portal</Button>
        </form>
        <Link to="/" className="mt-4 inline-block text-sm font-semibold text-primary">← Back to FindIt</Link>
      </Card>
    </div>
  )
}
