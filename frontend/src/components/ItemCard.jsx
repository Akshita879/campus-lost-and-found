import { MapPin, Clock } from 'lucide-react'
import { motion } from 'framer-motion'
import { Badge, Button } from './ui'
import { useState } from 'react'
import { CATEGORY_ICONS } from '../lib/constants'
import { IMAGES } from '../data/images'
export default function ItemCard({ item, onDetails }) {
  const [bad, setBad] = useState(false)
  const src = item.image || IMAGES[item.id]
  const Icon = CATEGORY_ICONS[item.category] || CATEGORY_ICONS.Electronics
  const found = item.type === 'found'
  return (
    <motion.article layout initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col rounded-2xl border border-slate-200 bg-white p-4 shadow-card transition hover:-translate-y-0.5 hover:shadow-lift">
      <div className="relative mb-3 grid aspect-video place-items-center rounded-xl bg-gradient-to-br from-surface-low to-surface-high">
        {src && !bad ? <img src={src} alt={item.title} loading="lazy" onError={() => setBad(true)} className="absolute inset-0 h-full w-full rounded-xl object-cover" /> : <Icon size={44} className="text-primary/60" aria-hidden />}
        <span className="absolute left-2 top-2 flex gap-1"><Badge tone={found ? 'teal' : 'slate'}>{found ? 'Found' : 'Lost'}</Badge><Badge tone="slate">{item.category}</Badge></span>
        <span className="absolute bottom-2 right-2 flex items-center gap-1 rounded-full bg-white/90 px-2 py-0.5 text-xs font-semibold"><Clock size={12} />{item.time}</span>
      </div>
      <div className="flex justify-between text-xs text-on-surface-variant"><span>{found ? 'Held at desk' : 'Owner searching'}</span><span>ID: #{item.id}</span></div>
      <h3 className="mt-1 font-bold leading-snug">{item.title}</h3>
      <p className="mt-1 line-clamp-2 text-sm text-on-surface-variant">{item.description}</p>
      <p className="mt-2 flex items-center gap-1 text-sm text-on-surface-variant"><MapPin size={14} className="text-primary" />{item.location}</p>
      <div className="mt-auto grid grid-cols-5 gap-2 pt-4">
        <Button variant="secondary" className="col-span-2 !bg-surface-low" onClick={() => onDetails?.(item)}>View details</Button>
        {found
          ? (item.relatedLostId
              ? <Button variant="secondary" className="col-span-3 !bg-surface-low" disabled>Verified find</Button>
              : <Button to={`/verify/${item.id}`} className="col-span-3">I'm the owner</Button>)
          : <Button to={`/report?type=found&related=${item.id}`} variant="muted" className="col-span-3">I found this</Button>}
      </div>
    </motion.article>)
}
