import { useState } from 'react'
import { X } from 'lucide-react'
import { Button, Card } from './ui'
import { useAuth } from '../context/Auth'
import { apiErrorMessage } from '../lib/mappers'

export default function AuthModal() {
  const { authOpen, setAuthOpen, login, register } = useAuth()
  const [tab, setTab] = useState('login')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  if (!authOpen) return null

  const set = k => e => setForm({ ...form, [k]: e.target.value })

  const submit = async e => {
    e.preventDefault()
    setErr('')
    setBusy(true)
    const email = form.email.trim().toLowerCase()
    const password = form.password
    try {
      if (tab === 'login') {
        await login({ email, password })
      } else {
        if (form.name.trim().length < 2) throw new Error('Enter your name (2+ characters).')
        if (password.length < 8) throw new Error('Password must be at least 8 characters.')
        await register({ name: form.name.trim(), email, password })
      }
      setForm({ name: '', email: '', password: '' })
    } catch (x) {
      const msg = apiErrorMessage(x, x.message || 'Authentication failed')
      if (/already exists/i.test(msg)) {
        setErr('An account with this email already exists. Switch to Sign in.')
        setTab('login')
      } else {
        setErr(msg)
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[70] grid place-items-center bg-slate-900/50 p-4" onClick={() => setAuthOpen(false)}>
      <div className="w-full max-w-md" onClick={e => e.stopPropagation()}>
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold">{tab === 'login' ? 'Sign in' : 'Create account'}</h2>
            <button type="button" aria-label="Close" onClick={() => setAuthOpen(false)} className="rounded-lg p-1 hover:bg-surface-high"><X size={18} /></button>
          </div>
          <div className="mb-4 flex rounded-lg bg-surface-low p-1">
            {[['login', 'Sign in'], ['register', 'Register']].map(([v, l]) => (
              <button key={v} type="button" onClick={() => { setTab(v); setErr('') }}
                className={`flex-1 rounded-md px-3 py-2 text-sm font-semibold ${tab === v ? 'bg-white shadow-card' : 'text-on-surface-variant'}`}>{l}</button>
            ))}
          </div>
          <form onSubmit={submit} className="space-y-3">
            {tab === 'register' && (
              <label className="block"><span className="mb-1 block text-sm font-semibold">Full name</span>
                <input value={form.name} onChange={set('name')} placeholder="Alex Student" required minLength={2} autoComplete="name" /></label>
            )}
            <label className="block"><span className="mb-1 block text-sm font-semibold">Campus email</span>
              <input type="email" value={form.email} onChange={set('email')} placeholder="you@campus.edu" required autoComplete="email" /></label>
            <label className="block"><span className="mb-1 block text-sm font-semibold">Password</span>
              <input type="password" value={form.password} onChange={set('password')} placeholder="Min. 8 characters" required minLength={8} autoComplete={tab === 'login' ? 'current-password' : 'new-password'} /></label>
            {err && <p role="alert" className="rounded-lg bg-error-container/50 p-3 text-sm text-error">{err}</p>}
            <Button type="submit" loading={busy} className="w-full">{tab === 'login' ? 'Sign in' : 'Register & sign in'}</Button>
          </form>
        </Card>
      </div>
    </div>
  )
}
