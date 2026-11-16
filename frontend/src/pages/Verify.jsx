import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Clock3, ShieldCheck } from 'lucide-react'
import { Button, Card, Skeleton, EmptyState } from '../components/ui'
import { getItem, submitClaim } from '../services/itemsApi'
import { useAuth } from '../context/Auth'
import { useNotifications } from '../context/Notifications'
export default function Verify() {
  const { id } = useParams(), [item, setItem] = useState(undefined), [ans, setAns] = useState(''), [busy, setBusy] = useState(false), [err, setErr] = useState(''), [ok, setOk] = useState(false)
  const { requireAuth } = useAuth()
  const { push } = useNotifications()
  useEffect(() => { if (id) getItem(id).then(setItem).catch(() => setItem(null)); else setItem(null) }, [id])
  if (item === undefined) return <div className="mx-auto max-w-xl px-4 py-10"><Skeleton className="h-64" /></div>
  if (!item) return <div className="mx-auto max-w-xl px-4 py-16"><EmptyState title="Choose an item to claim" text="Open a found item in the directory and press “I'm the owner”." action={<Button to="/explore">Browse items</Button>} /></div>
  const send = async e => {
    e.preventDefault(); if (ans.trim().length < 5) return setErr('Enter your answer (5+ characters).')
    if (!requireAuth()) return
    setErr(''); setBusy(true)
    try {
      await submitClaim(item.id, ans.trim())
      setOk(true)
      push({ title: `Claim received on #${item.id}`, body: 'The desk will review your verification answer.', to: `/verify/${item.id}` })
    } catch (x) { setErr(x.message || 'Could not send your claim. Try again.') } finally { setBusy(false) }
  }
  return (
    <div className="mx-auto max-w-xl px-4 py-10"><Card className="p-6">
      <p className="text-xs font-semibold text-primary">Ownership verification · #{item.id}</p><h1 className="mt-1 text-2xl font-bold">{item.title}</h1>
      {ok ? <div className="mt-6 rounded-xl bg-amber-50 p-5 text-amber-800"><Clock3 className="mb-2" /><h2 className="font-bold">Claim pending review</h2><p className="mt-1 text-sm">Desk staff will check your answer and notify you. You'll then get pickup details.</p><Button to="/notifications" className="mt-4">View notifications</Button></div>
      : <form onSubmit={send} className="mt-5 space-y-4"><div className="flex gap-3 rounded-xl bg-surface-low p-4 text-sm"><ShieldCheck className="shrink-0 text-primary" /><span>Answer with private identifying details to prove the item is yours. Your answer is only shown to desk staff.</span></div>
        <label className="block"><span className="mb-1 block text-sm font-semibold">What distinctive mark is on the item's base or inside?</span><input value={ans} onChange={e => setAns(e.target.value)} placeholder="Your answer" />{err && <span role="alert" className="mt-1 block text-xs text-error">{err}</span>}</label>
        <Button type="submit" loading={busy} className="w-full">Submit claim</Button></form>}
    </Card></div>)
}
