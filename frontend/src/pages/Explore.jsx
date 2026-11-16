import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, X } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import ItemCard from '../components/ItemCard'
import { Button, Badge, Skeleton, EmptyState, ErrorState } from '../components/ui'
import { listItems } from '../services/itemsApi'
import { CATEGORIES } from '../lib/constants'
const PAGE = 6
export default function Explore() {
  const [sp] = useSearchParams()
  const [q, setQ] = useState(sp.get('q') || '')
  const [dq, setDq] = useState(q)
  const [cat, setCat] = useState(sp.get('category') || 'All')
  const [type, setType] = useState('all')
  const [page, setPage] = useState(1)
  const [state, setState] = useState({ status: 'loading', items: [], total: 0 })
  const [sel, setSel] = useState(null)

  useEffect(() => {
    const t = setTimeout(() => { setDq(q); setPage(1) }, 350)
    return () => clearTimeout(t)
  }, [q])

  const load = useCallback(() => {
    setState(s => ({ ...s, status: 'loading' }))
    listItems({ q: dq, category: cat, type, page, pageSize: PAGE })
      .then(r => setState({ status: 'ok', ...r }))
      .catch(e => setState({ status: 'error', items: [], total: 0, msg: e.message }))
  }, [dq, cat, type, page])

  useEffect(load, [load])
  const pages = Math.max(1, Math.ceil(state.total / PAGE))
  const reset = () => { setQ(''); setCat('All'); setType('all') }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 lg:px-8">
      <h1 className="text-3xl font-bold">Campus Lost &amp; Found Directory</h1>
      <p className="mt-1 text-sm text-on-surface-variant">
        {state.status === 'ok' ? `${state.total} listing${state.total === 1 ? '' : 's'}` : 'Loading listings…'}
      </p>
      <div className="mt-6 space-y-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-3.5 text-slate-500" />
            <input aria-label="Search items" className="!pl-9 !pr-9" placeholder="MacBook, Hydro Flask, keys…" value={q} onChange={e => setQ(e.target.value)} />
            {q && <button aria-label="Clear search" onClick={() => setQ('')} className="absolute right-2 top-2.5 p-1"><X size={16} /></button>}
          </div>
          <div className="flex rounded-lg bg-surface-low p-1" role="tablist">
            {[['all', 'All'], ['lost', 'Lost'], ['found', 'Found']].map(([v, l]) => (
              <button key={v} role="tab" aria-selected={type === v} onClick={() => { setType(v); setPage(1) }}
                className={`rounded-md px-4 py-1.5 text-sm font-semibold ${type === v ? 'bg-white shadow-card' : 'text-on-surface-variant'}`}>{l}</button>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {['All', ...CATEGORIES].map(c => (
            <button key={c} onClick={() => { setCat(c); setPage(1) }}
              className={`rounded-full border px-3 py-1.5 text-sm font-semibold ${cat === c ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>{c}</button>
          ))}
        </div>
      </div>
      <div className="mt-6">
        {state.status === 'error' ? <ErrorState message={state.msg} onRetry={load} />
          : state.status === 'loading' ? <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{[0, 1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-80" />)}</div>
          : state.items.length === 0 ? <EmptyState title="No items found" text="Try a different keyword or clear your filters." action={<Button onClick={reset}>Clear filters</Button>} />
          : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{state.items.map(i => <ItemCard key={i.id} item={i} onDetails={setSel} />)}</div>}
      </div>
      {state.status === 'ok' && pages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <Button variant="secondary" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</Button>
          <span className="text-sm font-semibold">Page {page} of {pages}</span>
          <Button variant="secondary" disabled={page === pages} onClick={() => setPage(page + 1)}>Next</Button>
        </div>
      )}
      <AnimatePresence>
        {sel && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[60] grid place-items-center bg-slate-900/50 p-4" onClick={() => setSel(null)}>
            <motion.div initial={{ y: 16 }} animate={{ y: 0 }} role="dialog" aria-modal="true" onClick={e => e.stopPropagation()} className="w-full max-w-md rounded-3xl bg-white p-6 shadow-lift">
              <div className="flex justify-between">
                <Badge tone={sel.type === 'found' ? 'teal' : 'slate'}>{sel.type === 'found' ? 'Found' : 'Lost'}</Badge>
                <button aria-label="Close" onClick={() => setSel(null)}><X size={18} /></button>
              </div>
              <h2 className="mt-3 text-xl font-bold">{sel.title}</h2>
              <p className="mt-2 text-sm text-on-surface-variant">{sel.description}</p>
              <dl className="mt-4 space-y-1 text-sm">
                <div><dt className="inline font-semibold">Location: </dt><dd className="inline">{sel.location}</dd></div>
                <div><dt className="inline font-semibold">Reported: </dt><dd className="inline">{sel.time}</dd></div>
                <div><dt className="inline font-semibold">ID: </dt><dd className="inline">#{sel.id}</dd></div>
              </dl>
              <div className="mt-5">
                {sel.type === 'found'
                  ? (sel.relatedLostId
                      ? <Button variant="secondary" className="w-full !bg-surface-low" disabled>Verified find</Button>
                      : <Button to={`/verify/${sel.id}`} className="w-full">I'm the owner</Button>)
                  : <Button to={`/report?type=found&related=${sel.id}`} className="w-full">I found this</Button>}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
