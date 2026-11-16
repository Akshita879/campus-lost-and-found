import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Camera, ScanSearch, ShieldCheck } from 'lucide-react'
import { Button } from '../components/ui'
import { useAuth } from '../context/Auth'

const STEPS = [
  [Camera, 'Report', 'Lost or found something? Add details, place, and an optional photo.'],
  [ScanSearch, 'Match', 'We compare your lost reports with found listings using text similarity — not an AI model.'],
  [ShieldCheck, 'Verify & collect', 'The finder answers your private question once. Then you share where to meet.'],
]

export default function Landing() {
  const nav = useNavigate()
  const { user, ready, setAuthOpen } = useAuth()

  useEffect(() => {
    if (!ready || !user) return
    nav(user.is_admin ? '/admin' : '/explore', { replace: true })
  }, [ready, user, nav])

  if (!ready || user) {
    return <div className="min-h-[50vh]" />
  }

  return (
    <section className="relative overflow-hidden px-4 pb-20 pt-16 text-center">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary-fixed/40 via-background to-background" />
      <div className="relative mx-auto max-w-3xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Campus Lost &amp; Found</p>
        <h1 className="mt-4 text-4xl font-extrabold tracking-tight md:text-6xl">
          FindIt
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-on-surface-variant">
          A private, campus-first way to report lost belongings, browse found items, and reconnect owners with what they lost.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Button onClick={() => setAuthOpen(true)}>Sign in to continue</Button>
          <Button variant="secondary" onClick={() => setAuthOpen(true)}>Create account</Button>
        </div>
        <p className="mt-4 text-sm text-on-surface-variant">
          Campus staff?{' '}
          <Link to="/admin/login" className="font-semibold text-primary underline-offset-2 hover:underline">
            I am an admin
          </Link>
        </p>
      </div>
      <div className="relative mx-auto mt-16 grid max-w-5xl gap-5 md:grid-cols-3">
        {STEPS.map(([I, t, d]) => (
          <div key={t} className="rounded-2xl border border-slate-200 bg-white/90 p-6 text-left shadow-card backdrop-blur">
            <I className="mb-3 text-primary" />
            <h2 className="font-bold">{t}</h2>
            <p className="mt-1 text-sm text-on-surface-variant">{d}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
