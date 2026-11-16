import { useEffect, useState } from 'react'
import { BellOff, Trash2 } from 'lucide-react'
import { useNotifications } from '../context/Notifications'
import { useAuth } from '../context/Auth'
import { submitMeetup } from '../services/claimsApi'
import { submitFoundMeetup } from '../services/meetupApi'
import { deleteNotification } from '../services/notificationsApi'
import { Button, EmptyState, Skeleton } from '../components/ui'

export default function Notifications() {
  const { list, unread, loading, refresh, markAll } = useNotifications()
  const { user, requireAuth, ready } = useAuth()
  const [busyId, setBusyId] = useState(null)
  const [actionErr, setActionErr] = useState('')
  const [meetupDrafts, setMeetupDrafts] = useState({})
  const [meetupSent, setMeetupSent] = useState({})

  useEffect(() => {
    if (ready && user) refresh()
  }, [ready, user, refresh])

  if (ready && !user) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16">
        <EmptyState
          title="Sign in to view notifications"
          text="You’ll see updates when someone finds your lost item."
          action={<Button onClick={() => requireAuth()}>Sign in</Button>}
        />
      </div>
    )
  }

  const onDelete = async (id) => {
    setActionErr('')
    try {
      await deleteNotification(id)
      await refresh()
    } catch (e) {
      setActionErr(e.message)
    }
  }

  const onMeetupForFound = async (reportId) => {
    const text = (meetupDrafts[`r-${reportId}`] || '').trim()
    if (text.length < 10) {
      setActionErr('Meetup details must be at least 10 characters.')
      return
    }
    setActionErr(''); setBusyId(`r-${reportId}`)
    try {
      await submitFoundMeetup(reportId, text)
      setMeetupSent(s => ({ ...s, [`r-${reportId}`]: true }))
      await refresh()
    } catch (e) {
      setActionErr(e.message)
    } finally {
      setBusyId(null)
    }
  }

  const onMeetupForClaim = async (claimId) => {
    const text = (meetupDrafts[`c-${claimId}`] || '').trim()
    if (text.length < 10) {
      setActionErr('Meetup details must be at least 10 characters.')
      return
    }
    setActionErr(''); setBusyId(`c-${claimId}`)
    try {
      await submitMeetup(claimId, text)
      setMeetupSent(s => ({ ...s, [`c-${claimId}`]: true }))
      await refresh()
    } catch (e) {
      setActionErr(e.message)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-3xl font-bold">
          Notifications{unread > 0 && <span className="ml-2 text-base text-primary">{unread} new</span>}
        </h1>
        <Button variant="secondary" onClick={markAll} disabled={!unread}>Mark all read</Button>
      </div>
      {actionErr && <p role="alert" className="mb-4 rounded-lg bg-error-container/50 p-3 text-sm text-error">{actionErr}</p>}
      {loading ? (
        <div className="space-y-3">{[0, 1, 2].map(i => <Skeleton key={i} className="h-24" />)}</div>
      ) : list.length === 0 ? (
        <EmptyState
          title="You're all caught up"
          text="When someone reports finding your lost item, it shows up here so you can share meetup details."
          action={<BellOff className="text-slate-400" />}
        />
      ) : (
        <ul className="space-y-3">
          {list.map(n => (
            <li
              key={n.id}
              className={`rounded-2xl border p-4 ${n.read ? 'border-slate-200 bg-white' : 'border-primary/30 bg-primary-fixed/20'}`}
            >
              <div className="flex justify-between gap-3">
                <h2 className="font-bold">{n.title}</h2>
                <div className="flex items-center gap-2">
                  {!n.read && <span className="h-2 w-2 shrink-0 rounded-full bg-primary" aria-label="Unread" />}
                  <button
                    type="button"
                    aria-label="Delete notification"
                    className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-error"
                    onClick={() => onDelete(n.id)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <p className="mt-1 whitespace-pre-wrap text-sm text-on-surface-variant">{n.body}</p>
              <p className="mt-2 text-xs text-outline">{n.time}</p>

              {/* After a verified linked find: lost owner (A) sends meetup once — no second verification */}
              {n.kind === 'found_linked' && n.reportId && !meetupSent[`r-${n.reportId}`] && (
                <div className="mt-3 space-y-2 rounded-xl bg-surface-low p-3">
                  <p className="text-sm font-semibold">Where / when can you meet the finder?</p>
                  <textarea
                    rows={3}
                    value={meetupDrafts[`r-${n.reportId}`] || ''}
                    onChange={e => setMeetupDrafts(d => ({ ...d, [`r-${n.reportId}`]: e.target.value }))}
                    placeholder="Cafe entrance tomorrow 5 PM, near the red benches…"
                  />
                  <Button loading={busyId === `r-${n.reportId}`} onClick={() => onMeetupForFound(n.reportId)}>
                    Send meetup details
                  </Button>
                </div>
              )}

              {n.kind === 'claim_needs_meetup' && n.claimId && !meetupSent[`c-${n.claimId}`] && (
                <div className="mt-3 space-y-2 rounded-xl bg-surface-low p-3">
                  <p className="text-sm font-semibold">Where / when can you meet the finder?</p>
                  <textarea
                    rows={3}
                    value={meetupDrafts[`c-${n.claimId}`] || ''}
                    onChange={e => setMeetupDrafts(d => ({ ...d, [`c-${n.claimId}`]: e.target.value }))}
                    placeholder="Library lobby, tomorrow 5 PM…"
                  />
                  <Button loading={busyId === `c-${n.claimId}`} onClick={() => onMeetupForClaim(n.claimId)}>
                    Send meetup details
                  </Button>
                </div>
              )}

              {/* Finder (B) only sees info — no reply / approve buttons */}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
