import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Camera, ScanSearch, ShieldCheck, ArrowRight } from 'lucide-react'
import { Button, Skeleton } from '../components/ui'
import ItemCard from '../components/ItemCard'
import { listItems } from '../services/itemsApi'
import { CATEGORIES } from '../lib/constants'
const STEPS = [
  [Camera, 'Report', 'Lost or found something? Add a short description, where, and an optional photo.'],
  [ScanSearch, 'Match', 'Lost reports are compared with found listings to suggest likely pairs.'],
  [ShieldCheck, 'Claim', 'If you recognise a found item, send private identifying details for desk review.'],
]
export default function Landing() {
  const nav = useNavigate()
  const [q, setQ] = useState('')
  const [cat, setCat] = useState('All')
  const [recent, setRecent] = useState(null)
  useEffect(() => { listItems({ type: 'found', pageSize: 4 }).then(r => setRecent(r.items)).catch(() => setRecent([])) }, [])
  const go = (term = q, c = cat) => nav(`/explore?q=${encodeURIComponent(term)}${c !== 'All' ? `&category=${encodeURIComponent(c)}` : ''}`)
  return (
    <>
      <section className="bg-gradient-to-b from-primary-fixed/30 to-background px-4 pb-14 pt-14 text-center">
        <h1 className="mx-auto max-w-3xl text-4xl font-extrabold tracking-tight md:text-5xl">
          Lost something on campus?
          <span className="block text-primary">Lost it? Find it.</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-on-surface-variant">
          Report lost belongings, browse found items, and get suggested matches for your listings.
        </p>
        <form onSubmit={e => { e.preventDefault(); go() }} className="mx-auto mt-8 flex max-w-3xl flex-col gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-lift sm:flex-row">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-3.5 text-slate-500" />
            <input aria-label="Search" value={q} onChange={e => setQ(e.target.value)} placeholder="Item name or keyword" className="!border-0 !pl-9 !ring-0" />
          </div>
          <select aria-label="Category" value={cat} onChange={e => setCat(e.target.value)} className="sm:!w-44">
            <option>All</option>
            {CATEGORIES.map(c => <option key={c}>{c}</option>)}
          </select>
          <Button type="submit">Search <ArrowRight size={16} /></Button>
        </form>
        <div className="mt-6 flex justify-center gap-3">
          <Button to="/report">Report lost item</Button>
          <Button to="/report?type=found" variant="secondary">I found an item</Button>
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-4 py-12 lg:px-8">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold">Recently found</h2>
            <p className="text-sm text-on-surface-variant">Latest found-item listings.</p>
          </div>
          <Button to="/explore" variant="ghost">View all</Button>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {recent
            ? recent.length
              ? recent.map(i => <ItemCard key={i.id} item={i} />)
              : <p className="col-span-full text-sm text-on-surface-variant">No found items yet. Be the first to report one.</p>
            : [0, 1, 2, 3].map(i => <Skeleton key={i} className="h-72" />)}
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-4 pb-16 lg:px-8">
        <h2 className="mb-6 text-center text-2xl font-bold">How it works</h2>
        <div className="grid gap-5 md:grid-cols-3">
          {STEPS.map(([I, t, d]) => (
            <div key={t} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
              <I className="mb-3 text-primary" />
              <h3 className="font-bold">{t}</h3>
              <p className="mt-1 text-sm text-on-surface-variant">{d}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
