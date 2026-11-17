/** Map backend report → frontend item shape used by cards/pages. */
export function reportToItem(r) {
  if (!r) return null
  const type = String(r.report_type || r.type || '').toLowerCase() === 'found' ? 'found' : 'lost'
  return {
    id: r.id,
    type,
    title: r.item_name || r.title || '',
    description: r.description || '',
    category: r.category || '',
    location: r.location || '',
    time: formatWhen(r.created_at || r.approximate_date),
    date: r.approximate_date || null,
    image: imageUrl(r.image_path),
    status: r.status || null,
    user_id: r.user_id,
    question: r.verification_question || r.question || null,
    relatedLostId: r.related_lost_report_id || null,
  }
}

export function imageUrl(path) {
  if (!path) return null
  if (/^https?:\/\//i.test(path)) return path
  const cleaned = String(path).replace(/^\//, '')
  const api = import.meta.env.VITE_API_URL || ''
  const origin = api.replace(/\/api\/v1\/?$/i, '')
  // Prefer same-origin (vite proxy) when API URL points at localhost backend
  if (!origin || /localhost|127\.0\.0\.1/i.test(origin)) return `/${cleaned}`
  return `${origin}/${cleaned}`
}

function formatWhen(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  const diff = Date.now() - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${Math.max(1, mins)} mins ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs} hr${hrs === 1 ? '' : 's'} ago`
  const days = Math.floor(hrs / 24)
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return d.toLocaleDateString()
}

export function apiErrorMessage(err, fallback = 'Request failed') {
  const data = err?.response?.data
  if (!data) return err?.message || fallback
  if (typeof data.message === 'string') return data.message
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.errors) && data.errors[0]?.message) return data.errors[0].message
  return fallback
}
