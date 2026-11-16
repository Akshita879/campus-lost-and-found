import { http, USE_MOCKS, delay } from './api'
import { apiErrorMessage } from '../lib/mappers'

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

function mapNote(n) {
  return {
    id: n.id,
    title: n.title,
    body: n.body,
    read: !!n.is_read,
    kind: n.kind || null,
    claimId: n.claim_id || null,
    reportId: n.report_id || null,
    time: formatWhen(n.created_at),
  }
}

export async function listNotifications() {
  if (USE_MOCKS) {
    await delay(300)
    return { notifications: [], unread: 0 }
  }
  try {
    const data = (await http.get('/notifications')).data
    const notifications = (data.notifications || []).map(mapNote)
    return { notifications, unread: data.unread_count || 0 }
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load notifications'))
  }
}

export async function markAllNotificationsRead() {
  if (USE_MOCKS) return { notifications: [], unread: 0 }
  try {
    const data = (await http.post('/notifications/read-all')).data
    return { notifications: (data.notifications || []).map(mapNote), unread: 0 }
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not update notifications'))
  }
}

export async function deleteNotification(id) {
  try {
    return (await http.delete(`/notifications/${id}`)).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not delete notification'))
  }
}
