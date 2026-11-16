import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { CheckCircle2, ShieldCheck, MapPin } from 'lucide-react'
import { Button, Card, Skeleton, EmptyState } from '../components/ui'
import { getItem, submitClaim } from '../services/itemsApi'
import { submitMeetup } from '../services/claimsApi'
import { useAuth } from '../context/Auth'
import { useNotifications } from '../context/Notifications'

export default function Verify() {
  const { id } = useParams()
  const [item, setItem] = useState(undefined)
  const [question, setQuestion] = useState('')
  const [ans, setAns] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [claim, setClaim] = useState(null)
  const [meetup, setMeetup] = useState('')
  const [meetupDone, setMeetupDone] = useState(false)
  const { requireAuth } = useAuth()
  const { refresh } = useNotifications()

  useEffect(() => {
    if (!id) { setItem(null); return }
    getItem(id).then(async (found) => {
      if (!found) { setItem(null); return }
      setItem(found)
      if (found.question) {
        setQuestion(found.question)
        return
      }
      if (found.relatedLostId) {
        const lost = await getItem(found.relatedLostId)
        setQuestion(lost?.question || '')
      } else {
        setQuestion('')
      }
    }).catch(() => setItem(null))
  }, [id])

  if (item === undefined) return <div className="mx-auto max-w-xl px-4 py-10"><Skeleton className="h-64" /></div>
  if (!item || item.type !== 'found') {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <EmptyState title="Choose a found item to claim" text="Open a found listing in Explore and press “I'm the owner”." action={<Button to="/explore">Browse items</Button>} />
      </div>
    )
  }
  // Linked finds already verified when the finder submitted — owner uses Notifications for meetup
  if (item.relatedLostId) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <EmptyState
          title="This find is already verified"
          text="Open Notifications to share where and when you can meet the finder. No second verification step."
          action={<Button to="/notifications">Open notifications</Button>}
        />
      </div>
    )
  }

  const send = async e => {
    e.preventDefault()
    if (ans.trim().length < 2) return setErr('Enter your answer (2+ characters).')
    if (!requireAuth()) return
    setErr(''); setBusy(true)
    try {
      const created = await submitClaim(item.id, ans.trim())
      setClaim(created)
      refresh?.()
    } catch (x) {
      setErr(x.message || 'Could not send your claim. Try again.')
    } finally {
      setBusy(false)
    }
  }

  const sendMeetup = async e => {
    e.preventDefault()
    if (meetup.trim().length < 10) return setErr('Add meetup details (at least 10 characters).')
    if (!claim?.id) return
    setErr(''); setBusy(true)
    try {
      await submitMeetup(claim.id, meetup.trim())
      setMeetupDone(true)
      refresh?.()
    } catch (x) {
      setErr(x.message || 'Could not save meetup details.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-10">
      <Card className="p-6">
        <p className="text-xs font-semibold text-primary">Ownership verification · #{item.id}</p>
        <h1 className="mt-1 text-2xl font-bold">{item.title}</h1>
        {claim ? (
          <div className="mt-6 space-y-4">
            <div className="rounded-xl bg-emerald-50 p-5 text-emerald-900">
              <CheckCircle2 className="mb-2" />
              <h2 className="font-bold">Claim submitted — answer matched</h2>
              <p className="mt-1 text-sm">
                Tell the finder where and when you can meet so they can hand over the item.
              </p>
            </div>
            {meetupDone ? (
              <div className="rounded-xl bg-surface-low p-4 text-sm">
                <p className="font-semibold">Meetup details sent to the finder.</p>
                <p className="mt-1 text-on-surface-variant">{meetup}</p>
                <Button to="/notifications" className="mt-4">View notifications</Button>
              </div>
            ) : (
              <form onSubmit={sendMeetup} className="space-y-3 rounded-xl border border-slate-200 p-4">
                <h3 className="flex items-center gap-2 font-bold"><MapPin size={16} className="text-primary" />Meetup details</h3>
                <label className="block">
                  <span className="mb-1 block text-sm font-semibold">Where / when / landmark</span>
                  <textarea
                    rows={4}
                    value={meetup}
                    onChange={e => setMeetup(e.target.value)}
                    placeholder="e.g. Library lobby near the help desk, tomorrow 4:30–5:00 PM, look for a blue backpack"
                  />
                </label>
                {err && <span role="alert" className="block text-xs text-error">{err}</span>}
                <Button type="submit" loading={busy} className="w-full">Send meetup details</Button>
              </form>
            )}
          </div>
        ) : (
          <form onSubmit={send} className="mt-5 space-y-4">
            <div className="flex gap-3 rounded-xl bg-surface-low p-4 text-sm">
              <ShieldCheck className="shrink-0 text-primary" />
              <span>Answer the verification question set when the item was reported lost.</span>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-xs font-semibold text-primary">Verification question</p>
              <p className="mt-1 font-semibold">
                {question || 'No verification question is available for this listing.'}
              </p>
            </div>
            <label className="block">
              <span className="mb-1 block text-sm font-semibold">Your answer</span>
              <input value={ans} onChange={e => setAns(e.target.value)} placeholder="Must match the owner’s answer" disabled={!question} />
              {err && <span role="alert" className="mt-1 block text-xs text-error">{err}</span>}
            </label>
            <Button type="submit" loading={busy} className="w-full" disabled={!question}>Submit claim</Button>
          </form>
        )}
      </Card>
    </div>
  )
}
