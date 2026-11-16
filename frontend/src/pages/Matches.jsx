import { useEffect, useState, useCallback } from 'react'
import { Info, ArrowLeftRight } from 'lucide-react'
import { Button, Badge, Card, Skeleton, EmptyState, ErrorState } from '../components/ui'
import { getMatches } from '../services/matchesApi'
import { useAuth } from '../context/Auth'
import { USE_MOCKS } from '../services/api'
export default function Matches() {
  const [st, setSt] = useState({ status: 'loading', list: [] }), [dec, setDec] = useState({})
  const { user, requireAuth, ready } = useAuth()
  const load = useCallback(() => {
    if (!USE_MOCKS && !user) {
      setSt({ status: 'ok', list: [] })
      return
    }
    setSt({ status: 'loading', list: [] })
    getMatches().then(list => setSt({ status: 'ok', list })).catch(e => setSt({ status: 'error', list: [], msg: e.message }))
  }, [user])
  useEffect(() => { if (ready) load() }, [load, ready])
  const tone = s => s >= 75 ? 'green' : s >= 55 ? 'teal' : 'amber'
  return (
    <div className="mx-auto max-w-5xl px-4 py-8 lg:px-8">
      <h1 className="text-3xl font-bold">Suggested matches</h1>
      {!USE_MOCKS && !user ? (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <p className="font-bold">Sign in to see matches for your lost reports</p>
          <p className="mt-1 text-sm text-on-surface-variant">Matches are computed from your active lost listings against found items.</p>
          <Button className="mt-4" onClick={() => requireAuth()}>Sign in</Button>
        </div>
      ) : (
        <>
          <div className="mt-4 flex gap-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-800"><Info size={18} className="shrink-0" /><span>{USE_MOCKS
            ? <><b>Demo data.</b> Scores are simulated from text overlap in sample listings.</>
            : <>Scores come from the deterministic matching engine (category, name, description, location, and date).</>}</span></div>
          <div className="mt-6 space-y-4">
            {st.status === 'loading' ? [0, 1, 2].map(i => <Skeleton key={i} className="h-40" />)
              : st.status === 'error' ? <ErrorState message={st.msg} onRetry={load} />
              : st.list.length === 0 ? <EmptyState title="No matches yet" text="Report a lost item and suggestions will appear here when similar found items are listed." action={<Button to="/report">Report item</Button>} />
              : st.list.map(m => <Card key={m.id} className="p-5">
                <div className="flex flex-wrap items-center justify-between gap-2"><Badge tone={tone(m.score)}>{m.score}% similarity</Badge>{dec[m.id] && <Badge tone={dec[m.id] === 'confirmed' ? 'green' : 'slate'}>{dec[m.id] === 'confirmed' ? 'Match confirmed' : 'Dismissed'}</Badge>}</div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100" role="progressbar" aria-valuenow={m.score} aria-valuemin={0} aria-valuemax={100}><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${m.score}%` }} /></div>
                <div className="mt-4 grid items-center gap-3 md:grid-cols-[1fr_auto_1fr]">{[['Lost report', m.lost], null, ['Found listing', m.found]].map((x, i) => x ? <div key={i} className="rounded-xl bg-surface-low p-3"><p className="text-xs font-semibold text-primary">{x[0]} #{x[1].id}</p><p className="font-bold">{x[1].title}</p><p className="text-sm text-on-surface-variant">{x[1].location}</p></div> : <ArrowLeftRight key={i} className="mx-auto hidden text-slate-400 md:block" />)}</div>
                {!dec[m.id] && <div className="mt-4 flex gap-2"><Button onClick={() => setDec({ ...dec, [m.id]: 'confirmed' })}>Confirm match</Button><Button variant="secondary" onClick={() => setDec({ ...dec, [m.id]: 'dismissed' })}>Dismiss</Button><Button to={`/verify/${m.found.id}`} variant="ghost">Verify ownership</Button></div>}
              </Card>)}
          </div>
        </>
      )}
    </div>)
}
