import { http, USE_MOCKS, delay } from './api'
import { ITEMS } from '../data/items'
import { reportToItem, apiErrorMessage } from '../lib/mappers'

export async function listItems({ q = '', category = 'All', type = 'all', page = 1, pageSize = 6 } = {}) {
  if (USE_MOCKS) {
    await delay(500)
    const s = q.trim().toLowerCase()
    const r = ITEMS.filter(i => (type === 'all' || i.type === type) && (category === 'All' || i.category === category)
      && (!s || `${i.title} ${i.description} ${i.location}`.toLowerCase().includes(s)))
    return { items: r.slice((page - 1) * pageSize, page * pageSize), total: r.length }
  }
  try {
    const params = { page, page_size: pageSize }
    if (q.trim()) params.keyword = q.trim()
    if (category && category !== 'All') params.category = category
    if (type === 'lost') params.report_type = 'LOST'
    if (type === 'found') params.report_type = 'FOUND'
    const data = (await http.get('/reports/search', { params })).data
    return { items: (data.items || []).map(reportToItem), total: data.total || 0 }
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load items'))
  }
}

export async function getItem(id) {
  if (USE_MOCKS) {
    await delay(300)
    return ITEMS.find(i => String(i.id) === String(id)) || null
  }
  try {
    const data = (await http.get(`/reports/${id}`)).data
    return reportToItem(data)
  } catch (err) {
    if (err?.response?.status === 404) return null
    throw new Error(apiErrorMessage(err, 'Could not load item'))
  }
}

/**
 * payload: { title, category, description, location, date, type, question, answer, relatedLostId, files }
 */
export async function reportItem(payload) {
  if (USE_MOCKS) {
    await delay(1000)
    if (payload.title.toLowerCase().includes('fail')) throw new Error('Mock server error. Try again.')
    return { id: 'UT-' + Math.floor(Math.random() * 9000 + 1000) }
  }
  try {
    const reportType = payload.type === 'found' ? 'FOUND' : 'LOST'
    const approximateDate = payload.date || new Date().toISOString().slice(0, 10)
    const description = payload.description || ''
    const file = payload.files?.[0]?.file
    const body = {
      item_name: payload.title,
      category: payload.category,
      description,
      report_type: reportType,
      approximate_date: approximateDate,
      location: payload.location,
    }
    if (reportType === 'LOST') {
      if (payload.question) body.verification_question = payload.question
      if (payload.answer) body.verification_answer = payload.answer
    }
    if (reportType === 'FOUND' && payload.relatedLostId) {
      body.related_lost_report_id = Number(payload.relatedLostId)
      body.verification_answer = payload.answer
    }
    let data
    if (file) {
      const form = new FormData()
      Object.entries(body).forEach(([k, v]) => {
        if (v !== undefined && v !== null) form.append(k, String(v))
      })
      form.append('image', file)
      data = (await http.post('/reports/upload', form)).data
    } else {
      data = (await http.post('/reports', body)).data
    }
    return { id: data.id, item: reportToItem(data) }
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not submit report'))
  }
}

export async function submitClaim(id, answer) {
  if (USE_MOCKS) {
    await delay(900)
    return { status: 'pending_review' }
  }
  try {
    const data = (await http.post('/claims', {
      report_id: Number(id),
      verification_details: answer,
    })).data
    return {
      ...data,
      status: String(data.status || 'PENDING').toLowerCase(),
      id: data.id,
    }
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not send your claim'))
  }
}
