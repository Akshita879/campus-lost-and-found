import { Link } from 'react-router-dom'
import { Loader2, AlertTriangle, SearchX } from 'lucide-react'
const V = { primary:'bg-primary text-white hover:bg-primary-container shadow-sm', secondary:'bg-white border border-slate-200 text-slate-900 hover:bg-slate-50',
  ghost:'text-primary hover:bg-primary/10', muted:'bg-slate-600 text-white hover:bg-slate-700' }
export function Button({ variant='primary', to, loading, className='', children, ...p }) {
  const c = `inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors disabled:opacity-60 ${V[variant]} ${className}`
  if (to) return <Link to={to} className={c}>{children}</Link>
  return <button className={c} disabled={loading || p.disabled} {...p}>{loading && <Loader2 size={16} className="animate-spin" />}{children}</button>
}
export const Badge = ({ tone='teal', children }) => {
  const t = { teal:'bg-teal-100 text-teal-700', amber:'bg-amber-100 text-amber-700', green:'bg-emerald-50 text-emerald-700', rose:'bg-rose-100 text-rose-600', slate:'bg-slate-100 text-slate-700' }
  return <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${t[tone]}`}>{children}</span>
}
export const Card = ({ className='', children }) => <div className={`rounded-2xl border border-slate-200 bg-white shadow-card ${className}`}>{children}</div>
export const Skeleton = ({ className='' }) => <div className={`animate-pulse rounded-lg bg-slate-200/70 ${className}`} />
export const EmptyState = ({ title, text, action }) => (
  <div className="flex flex-col items-center rounded-2xl border border-dashed border-slate-300 bg-white py-14 text-center">
    <SearchX className="mb-3 text-slate-400" size={36} /><h3 className="font-bold">{title}</h3>
    <p className="mt-1 max-w-sm text-sm text-on-surface-variant">{text}</p><div className="mt-4">{action}</div></div>)
export const ErrorState = ({ message, onRetry }) => (
  <div role="alert" className="flex flex-col items-center rounded-2xl border border-error/20 bg-error-container/40 py-12 text-center">
    <AlertTriangle className="mb-3 text-error" size={34} /><h3 className="font-bold">Something went wrong</h3>
    <p className="mt-1 text-sm">{message}</p><Button variant="secondary" className="mt-4" onClick={onRetry}>Try again</Button></div>)
export const Logo = () => (
  <Link to="/" className="flex items-center gap-2"><span className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-white font-extrabold">F</span>
    <span className="text-xl font-bold tracking-tight">FindIt</span><span className="hidden rounded-full bg-secondary-container px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-on-secondary-container sm:inline">Campus Beta</span></Link>)
