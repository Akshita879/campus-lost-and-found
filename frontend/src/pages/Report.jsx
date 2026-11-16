import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CheckCircle2, ShieldCheck, Check } from 'lucide-react'
import { motion } from 'framer-motion'
import DropZone from '../components/DropZone'
import { Button, Card } from '../components/ui'
import { getItem, reportItem } from '../services/itemsApi'
import { CATEGORIES } from '../lib/constants'
import { useAuth } from '../context/Auth'
const empty = { title: '', category: '', description: '', location: '', date: '', question: '', answer: '' }
const Field = ({ label, error, children }) => <label className="block"><span className="mb-1 block text-sm font-semibold">{label}</span>{children}{error && <span role="alert" className="mt-1 block text-xs text-error">{error}</span>}</label>
export default function Report() {
  const [sp] = useSearchParams()
  const relatedId = sp.get('related')
  const [kind, setKind] = useState(sp.get('type') === 'found' || relatedId ? 'found' : 'lost')
  const [step, setStep] = useState(0)
  const [f, setF] = useState(empty)
  const [files, setFiles] = useState([])
  const [errs, setErrs] = useState({})
  const [busy, setBusy] = useState(false)
  const [fail, setFail] = useState('')
  const [done, setDone] = useState(null)
  const [related, setRelated] = useState(null)
  const { requireAuth } = useAuth()

  const linkedFound = kind === 'found' && !!relatedId
  // Standalone found: skip verification step. Lost / linked-found: 4 steps.
  const steps = kind === 'found' && !linkedFound
    ? ['Item details', 'Photos', 'Location & time']
    : ['Item details', 'Photos', 'Location & time', 'Verification']
  const lastStep = steps.length - 1

  useEffect(() => {
    if (!relatedId) { setRelated(null); return }
    setKind('found')
    getItem(relatedId).then(item => {
      setRelated(item)
      if (item) {
        setF(prev => ({
          ...prev,
          title: prev.title || item.title || '',
          category: prev.category || item.category || '',
          question: item.question || '',
        }))
      }
    }).catch(() => setRelated(null))
  }, [relatedId])

  const set = k => e => setF({ ...f, [k]: e.target.value })
  const validate = n => {
    const er = {}
    if (n === 0) {
      if (f.title.trim().length < 3) er.title = 'Enter at least 3 characters.'
      if (!f.category) er.category = 'Choose a category.'
      if (f.description.trim().length < 10) er.description = 'Describe distinguishing marks (10+ characters).'
    }
    if (n === 2 && !f.location.trim()) er.location = 'Say where it was.'
    if (n === 3 && kind === 'lost') {
      if (f.question.trim().length < 3) er.question = 'Add a question only someone who knows the item can answer.'
      if (f.answer.trim().length < 2) er.answer = 'Add the correct answer.'
    }
    if (n === 3 && linkedFound) {
      if (f.answer.trim().length < 2) er.answer = 'Enter your answer to the owner\'s question.'
    }
    setErrs(er)
    return !Object.keys(er).length
  }
  const next = () => validate(step) && setStep(step + 1)
  const submit = async e => {
    e.preventDefault()
    if (step < lastStep) return next()
    if (!validate(lastStep)) return
    if (!requireAuth()) return
    setBusy(true); setFail('')
    try {
      const res = await reportItem({
        ...f,
        type: kind,
        files,
        relatedLostId: linkedFound ? Number(relatedId) : null,
        question: kind === 'lost' ? f.question : undefined,
        answer: (kind === 'lost' || linkedFound) ? f.answer : undefined,
      })
      setDone(res)
    } catch (x) { setFail(x.message) } finally { setBusy(false) }
  }

  if (done) return (
    <div className="mx-auto max-w-lg px-4 py-20 text-center">
      <motion.div initial={{ scale: .8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
        <CheckCircle2 size={56} className="mx-auto text-primary" />
        <h1 className="mt-4 text-2xl font-bold">Report submitted</h1>
        <p className="mt-2 text-on-surface-variant">Reference #{done.id}. Your listing is visible in the directory.</p>
        {linkedFound && <p className="mt-2 text-sm text-on-surface-variant">The owner of the lost report has been notified.</p>}
        <div className="mt-6 flex justify-center gap-3">
          <Button to="/matches">See suggested matches</Button>
          <Button variant="secondary" onClick={() => { setF(empty); setFiles([]); setDone(null); setStep(0) }}>Report another</Button>
        </div>
      </motion.div>
    </div>
  )

  return (
    <form onSubmit={submit} noValidate className="mx-auto max-w-5xl px-4 py-8 lg:px-8">
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-3xl font-bold">Report an item</h1>
          <p className="mt-1 text-sm text-on-surface-variant">
            {linkedFound
              ? `Reporting a find related to lost listing #${relatedId}${related?.title ? ` — ${related.title}` : ''}.`
              : 'Add details and photos so owners and desks can recognise it.'}
          </p>
        </div>
        {!linkedFound && (
          <div className="flex rounded-lg bg-surface-low p-1">
            {[['lost', 'I lost something'], ['found', 'I found something']].map(([v, l]) => (
              <button type="button" key={v} onClick={() => { setKind(v); setStep(0); setErrs({}) }}
                className={`rounded-md px-4 py-2 text-sm font-semibold ${kind === v ? 'bg-white text-primary shadow-card' : 'text-on-surface-variant'}`}>{l}</button>
            ))}
          </div>
        )}
      </div>
      <ol className={`mb-6 grid gap-2 rounded-2xl border border-slate-200 bg-white p-3 shadow-card`} style={{ gridTemplateColumns: `repeat(${steps.length}, minmax(0, 1fr))` }} aria-label="Progress">
        {steps.map((t, i) => (
          <li key={t} className="flex items-center gap-2" aria-current={i === step ? 'step' : undefined}>
            <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm font-bold ${i < step ? 'bg-primary text-white' : i === step ? 'bg-primary-container text-white' : 'bg-secondary-container text-on-secondary-container'}`}>{i < step ? <Check size={16} /> : i + 1}</span>
            <span className="hidden min-w-0 sm:block"><span className="block truncate text-sm font-semibold">{t}</span><span className="text-xs text-on-surface-variant">{i < step ? 'Done' : i === step ? 'In progress' : 'Next'}</span></span>
          </li>
        ))}
      </ol>
      <div className="mx-auto max-w-2xl space-y-5">
        {step === 0 && (
          <Card className="space-y-4 p-5"><h2 className="font-bold">Item details</h2>
            <Field label="Title" error={errs.title}><input value={f.title} onChange={set('title')} placeholder="e.g. Midnight blue Stanley tumbler" /></Field>
            <Field label="Category" error={errs.category}><select value={f.category} onChange={set('category')}><option value="">Select…</option>{CATEGORIES.map(c => <option key={c}>{c}</option>)}</select></Field>
            <Field label="Distinctive features" error={errs.description}><textarea rows={4} value={f.description} onChange={set('description')} placeholder="Stickers, dents, engravings…" /></Field>
          </Card>
        )}
        {step === 1 && <Card className="space-y-4 p-5"><h2 className="font-bold">Photos <span className="text-xs font-normal text-on-surface-variant">(optional, up to 5)</span></h2><DropZone files={files} setFiles={setFiles} /></Card>}
        {step === 2 && (
          <Card className="space-y-4 p-5"><h2 className="font-bold">Location &amp; time</h2>
            <Field label="Building / area" error={errs.location}><input value={f.location} onChange={set('location')} placeholder="Perry-Castañeda Library, 3rd floor" /></Field>
            <Field label="Date"><input type="date" value={f.date} onChange={set('date')} /></Field>
          </Card>
        )}
        {step === 3 && kind === 'lost' && (
          <Card className="space-y-4 p-5">
            <h2 className="flex items-center gap-2 font-bold"><ShieldCheck size={18} className="text-primary" />Private ownership check</h2>
            <Field label="Verification question" error={errs.question}><input value={f.question} onChange={set('question')} placeholder="What sticker is on the base?" /></Field>
            <Field label="Correct answer" error={errs.answer}><input value={f.answer} onChange={set('answer')} placeholder="Only you should know this" /></Field>
            <p className="text-xs text-on-surface-variant">If someone finds a similar item, they will see your question and must answer it when reporting the find.</p>
          </Card>
        )}
        {step === 3 && linkedFound && (
          <Card className="space-y-4 p-5">
            <h2 className="flex items-center gap-2 font-bold"><ShieldCheck size={18} className="text-primary" />Private ownership check</h2>
            <div className="rounded-xl bg-surface-low p-4">
              <p className="text-xs font-semibold text-primary">Owner&apos;s verification question</p>
              <p className="mt-1 font-semibold">
                {!related
                  ? 'Loading question…'
                  : (related.question || 'This lost listing has no verification question from the owner.')}
              </p>
            </div>
            <Field label="Your answer" error={errs.answer}>
              <input
                value={f.answer}
                onChange={set('answer')}
                placeholder="Must match the owner’s answer"
                disabled={!related?.question}
              />
            </Field>
            <p className="text-xs text-on-surface-variant">Your answer must match what the owner set. They will be notified after a correct submit.</p>
          </Card>
        )}
      </div>
      {fail && <p role="alert" className="mt-4 rounded-lg bg-error-container/50 p-3 text-sm text-error">{fail}</p>}
      <div className="mx-auto mt-6 flex max-w-2xl justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-card">
        <Button type="button" variant="secondary" disabled={step === 0} onClick={() => { setErrs({}); setStep(step - 1) }}>Back</Button>
        {step < lastStep ? <Button type="submit">Continue</Button> : <Button type="submit" loading={busy}>Submit report</Button>}
      </div>
    </form>
  )
}
