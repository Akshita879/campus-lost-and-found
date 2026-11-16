import { useState } from 'react'
import { NavLink, Outlet, Link, useLocation } from 'react-router-dom'
import { Bell, Menu, X, MapPin } from 'lucide-react'
import { Logo, Button } from '../components/ui'
import AuthModal from '../components/AuthModal'
import { useNotifications } from '../context/Notifications'
import { useAuth } from '../context/Auth'
const NAV = [['/explore','Explore'],['/report','Report Item'],['/matches','AI Matches'],['/verify','Verification'],['/notifications','Notifications']]
export default function Layout() {
  const [open, setOpen] = useState(false), { unread } = useNotifications(); useLocation()
  const { user, setAuthOpen, logout } = useAuth()
  const cls = ({ isActive }) => `rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${isActive ? 'bg-primary-container text-white' : 'text-on-surface-variant hover:bg-surface-high'}`
  return (
    <div className="flex min-h-screen flex-col">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 lg:px-8">
          <div className="flex items-center gap-4"><Logo /><span className="hidden items-center gap-1 rounded-full bg-surface-low px-3 py-1.5 text-xs font-semibold xl:flex"><MapPin size={14} className="text-primary" />Central Campus &amp; Libraries</span></div>
          <nav className="hidden items-center gap-1 lg:flex">{NAV.slice(0, 4).map(([to, l]) => <NavLink key={to} to={to} className={cls}>{l}</NavLink>)}</nav>
          <div className="flex items-center gap-2">
            <Button to="/report" className="hidden sm:inline-flex">+ Report Item</Button>
            {user ? (
              <div className="hidden items-center gap-2 sm:flex">
                <span className="max-w-[10rem] truncate text-xs font-semibold text-on-surface-variant">{user.name}</span>
                <Button variant="secondary" onClick={logout}>Sign out</Button>
              </div>
            ) : (
              <Button variant="secondary" className="hidden sm:inline-flex" onClick={() => setAuthOpen(true)}>Sign in</Button>
            )}
            <Link to="/notifications" aria-label={`Notifications, ${unread} unread`} className="relative rounded-full p-2 hover:bg-surface-high"><Bell size={20} />
              {unread > 0 && <span className="absolute right-0.5 top-0.5 grid h-4 w-4 place-items-center rounded-full bg-error text-[10px] font-bold text-white">{unread}</span>}</Link>
            <button className="rounded-lg p-2 lg:hidden" aria-label="Menu" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
          </div>
        </div>
        {open && <nav className="flex flex-col gap-1 border-t border-slate-200 bg-white p-3 lg:hidden">
          {NAV.map(([to, l]) => <NavLink key={to} to={to} className={cls} onClick={() => setOpen(false)}>{l}</NavLink>)}
          {user
            ? <button type="button" className={cls({ isActive: false })} onClick={() => { logout(); setOpen(false) }}>Sign out ({user.name})</button>
            : <button type="button" className={cls({ isActive: false })} onClick={() => { setAuthOpen(true); setOpen(false) }}>Sign in</button>}
        </nav>}
      </header>
      <main className="flex-1 pt-16"><Outlet /></main>
      <footer className="border-t border-slate-200 bg-white"><div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-on-surface-variant md:flex-row md:justify-between lg:px-8">
        <span>FindIt – Connected Campus Recovery System</span><span>© 2025 FindIt Network</span></div></footer>
      <AuthModal />
    </div>
  )
}
