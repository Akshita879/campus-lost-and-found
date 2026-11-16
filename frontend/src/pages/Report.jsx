import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CheckCircle2, ShieldCheck, Check } from 'lucide-react'
import { motion } from 'framer-motion'
import DropZone from '../components/DropZone'
import { Button, Card } from '../components/ui'
import { reportItem } from '../services/itemsApi'
import { CATEGORIES } from '../lib/constants'
import { useAuth } from '../context/Auth'
import { useNotifications } from '../context/Notifications'
const STEPS = ['Item details', 'Photos', 'Location & time', 'Verification']
const empty = { title: '', category: '', description: '', location: '', date: '', question: '', answer: '' }
const Field = ({ label, error, children }) => <label className="block"><span className="mb-1 block text-sm font-semibold">{label}</span>{children}{error && <span role="alert" className="mt-1 block text-xs text-error">{error}</span>}</label>
export default function Report() {
  const [sp] = useSearchParams(), [kind, setKind] = useState(sp.get('type') === 'found' ? 'found' : 'lost')
  const [step, setStep] = useState(0), [f, setF] = useState(empty), [files, setFiles] = useState([]), [errs, setErrs] = useState({}), [busy, setBusy] = useState(false), [fail, setFail] = useState(''), [done, setDone] = useState(null)
  const { requireAuth } = useAuth()
  const { push } = useNotifications()
  const set = k => e => setF({ ...f, [k]: e.target.value })
  const validate = n => {
    const er = {}
    if (n === 0) { if (f.title.trim().length < 3) er.title = 'Enter at least 3 characters.'; if (!f.category) er.category = 'Choose a category.'; if (f.description.trim().length < 10) er.description = 'Describe distinguishing marks (10+ characters).' }
    if (n === 2 && !f.location.trim()) er.location = 'Say where it was.'
    if (n === 3 && kind === 'found' && !f.question.trim()) er.question = 'Add a question only the owner can answer.'
    setErrs(er); return !Object.keys(er).length
  }
  const next = () => validate(step) && setStep(step + 1)
  const submit = async e => {
    e.preventDefault(); if (step < 3) return next()
    if (!validate(3)) return
    if (!requireAuth()) return
    setBusy(true); setFail('')
    try {
      const res = await reportItem({ ...f, type: kind, files })
      setDone(res)
      push({ title: 'Report submitted', body: `Your ${kind} item report #${res.id} is now visible in the directory.`, to: '/explore' })
    } catch (x) { setFail(x.message) } finally { setBusy(false) }
  }
  if (done) return <div className="mx-auto max-w-lg px-4 py-20 text-center"><motion.div initial={{ scale: .8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}><CheckCircle2 size={56} className="mx-auto text-primary" />
    <h1 className="mt-4 text-2xl font-bold">Report submitted</h1><p className="mt-2 text-on-surface-variant">Reference #{done.id}. Your listing is visible in the directory.</p>
    <div className="mt-6 flex justify-center gap-3"><Button to="/matches">See suggested matches</Button><Button variant="secondary" onClick={() => { setF(empty); setFiles([]); setDone(null); setStep(0) }}>Report another</Button></div></motion.div></div>
  return (
    <form onSubmit={submit} noValidate className="mx-auto max-w-5xl px-4 py-8 lg:px-8">
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end"><div><h1 className="text-3xl font-bold">Report an item</h1><p className="mt-1 text-sm text-on-surface-variant">Add details and photos so owners and desks can recognise it.</p></div>
        <div className="flex rounded-lg bg-surface-low p-1">{[['lost', 'I lost something'], ['found', 'I found something']].map(([v, l]) => <button type="button" key={v} onClick={() => setKind(v)} className={`rounded-md px-4 py-2 text-sm font-semibold ${kind === v ? 'bg-white text-primary shadow-card' : 'text-on-surface-variant'}`}>{l}</button>)}</div></div>
      <ol className="mb-6 grid grid-cols-4 gap-2 rounded-2xl border border-slate-200 bg-white p-3 shadow-card" aria-label="Progress">{STEPS.map((t, i) => <li key={t} className="flex items-center gap-2" aria-current={i === step ? 'step' : undefined}>
        <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm font-bold ${i < step ? 'bg-primary text-white' : i === step ? 'bg-primary-container text-white' : 'bg-secondary-container text-on-secondary-container'}`}>{i < step ? <Check size={16} /> : i + 1}</span>
        <span className="hidden min-w-0 sm:block"><span className="block truncate text-sm font-semibold">{t}</span><span className="text-xs text-on-surface-variant">{i < step ? 'Done' : i === step ? 'In progress' : 'Next'}</span></span></li>)}</ol>
      <div className="mx-auto max-w-2xl space-y-5">
        {step === 0 && <Card className="space-y-4 p-5"><h2 className="font-bold">Item details</h2>
          <Field label="Title" error={errs.title}><input value={f.title} onChange={set('title')} placeholder="e.g. Midnight blue Stanley tumbler" /></Field>
          <Field label="Category" error={errs.category}><select value={f.category} onChange={set('category')}><option value="">Select…</option>{CATEGORIES.map(c => <option key={c}>{c}</option>)}</select></Field>
          <Field label="Distinctive features" error={errs.description}><textarea rows={4} value={f.description} onChange={set('description')} placeholder="Stickers, dents, engravings…" /></Field></Card>}
        {step === 1 && <Card className="space-y-4 p-5"><h2 className="font-bold">Photos <span className="text-xs font-normal text-on-surface-variant">(optional, up to 5)</span></h2><DropZone files={files} setFiles={setFiles} /></Card>}
        {step === 2 && <Card className="space-y-4 p-5"><h2 className="font-bold">Location &amp; time</h2>
          <Field label="Building / area" error={errs.location}><input value={f.location} onChange={set('location')} placeholder="Perry-Castañeda Library, 3rd floor" /></Field>
          <Field label="Date"><input type="date" value={f.date} onChange={set('date')} /></Field></Card>}
        {step === 3 && <Card className="space-y-4 p-5"><h2 className="flex items-center gap-2 font-bold"><ShieldCheck size={18} className="text-primary" />Private ownership check{kind === 'lost' && <span className="text-xs font-normal text-on-surface-variant">(optional)</span>}</h2>
          <Field label="Verification question" error={errs.question}><input value={f.question} onChange={set('question')} placeholder="What sticker is on the base?" /></Field>
          <Field label="Correct answer"><input value={f.answer} onChange={set('answer')} /></Field>
          <p className="text-xs text-on-surface-variant">Use this to remember what only the owner would know. Claimants submit private verification details when claiming.</p></Card>}
      </div>
      {fail && <p role="alert" className="mt-4 rounded-lg bg-error-container/50 p-3 text-sm text-error">{fail}</p>}
      <div className="mx-auto mt-6 flex max-w-2xl justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-card"><Button type="button" variant="secondary" disabled={step === 0} onClick={() => { setErrs({}); setStep(step - 1) }}>Back</Button>
        {step < 3 ? <Button type="submit">Continue</Button> : <Button type="submit" loading={busy}>Submit report</Button>}</div>
    </form>)
}
