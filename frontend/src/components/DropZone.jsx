import { useRef, useState } from 'react'
import { UploadCloud, X } from 'lucide-react'
const MAX_BYTES = 5 * 1024 * 1024
export default function DropZone({ files, setFiles, max = 5 }) {
  const ref = useRef(), [over, setOver] = useState(false), [err, setErr] = useState('')
  const add = list => {
    let e = '', ok = []
    ;[...list].forEach(f => {
      if (!/^image\/(jpeg|png|webp)$/.test(f.type)) e = 'Only JPEG, PNG or WebP images are supported.'
      else if (f.size > MAX_BYTES) e = 'Each photo must be under 5MB.'
      else ok.push({ id: crypto.randomUUID(), name: f.name, url: URL.createObjectURL(f), file: f })
    })
    if (files.length + ok.length > max) { e = `You can add up to ${max} photos.`; ok = ok.slice(0, max - files.length) }
    setErr(e); setFiles([...files, ...ok])
  }
  return (
    <div>
      <div onDragOver={e => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)}
        onDrop={e => { e.preventDefault(); setOver(false); add(e.dataTransfer.files) }}
        onClick={() => ref.current.click()} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && ref.current.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${over ? 'border-primary bg-primary/5' : 'border-slate-300 bg-surface-low'}`}>
        <UploadCloud className="mx-auto mb-2 text-primary" />
        <p className="text-sm font-semibold">Drop up to {max} clear photos here, or <span className="text-primary underline">browse files</span></p>
        <p className="mt-1 text-xs text-on-surface-variant">JPEG, PNG, WebP up to 5MB each (first photo is uploaded)</p>
        <input ref={ref} type="file" accept="image/jpeg,image/png,image/webp" multiple hidden onChange={e => { add(e.target.files); e.target.value = '' }} />
      </div>
      {err && <p role="alert" className="mt-2 text-sm text-error">{err}</p>}
      {files.length > 0 && <div className="mt-3 grid grid-cols-3 gap-3 sm:grid-cols-5">
        {files.map(f => <div key={f.id} className="relative aspect-square overflow-hidden rounded-xl border border-slate-200">
          <img src={f.url} alt={f.name} className="h-full w-full object-cover" />
          <button type="button" aria-label={`Remove ${f.name}`} onClick={() => setFiles(files.filter(x => x.id !== f.id))} className="absolute right-1 top-1 grid h-6 w-6 place-items-center rounded-full bg-black/60 text-white"><X size={14} /></button></div>)}
      </div>}
    </div>)
}
