import { http, USE_MOCKS, delay } from './api'
import { ITEMS } from '../data/items'
import { reportToItem, apiErrorMessage } from '../lib/mappers'

// SIMULATED matching (mocks only): plain word overlap plus category bonus on sample text.
const tok = s => new Set(s.toLowerCase().match(/[a-z0-9]{3,}/g) || [])
function similarity(a, b) {
  const A = tok(`${a.title} ${a.description}`), B = tok(`${b.title} ${b.description}`)
  let n = 0; A.forEach(t => B.has(t) && n++)
  const j = n / (A.size + B.size - n || 1)
  return Math.round(Math.min(0.97, j * 2.2 + (a.category === b.category ? 0.2 : 0)) * 100)
}

export async function getMatches() {
  if (USE_MOCKS) {
    await delay(900)
    const lost = ITEMS.filter(i => i.type === 'lost'), found = ITEMS.filter(i => i.type === 'found')
    return lost.flatMap(l => found.map(f => ({ id: `${l.id}-${f.id}`, lost: l, found: f, score: similarity(l, f) })))
      .filter(m => m.score >= 45).sort((a, b) => b.score - a.score)
  }
  try {
    const data = (await http.get('/matches')).data
    const list = Array.isArray(data) ? data : (data.matches || [])
    return list.map(m => {
      const lost = m.lost
        ? reportToItem(m.lost)
        : {
            id: m.lost_report_id,
            type: 'lost',
            title: m.lost_item_name || m.lost_title || 'Lost item',
            location: m.lost_location || '',
            description: m.lost_description || '',
            category: m.lost_category || '',
          }
      const found = m.found
        ? reportToItem(m.found)
        : {
            id: m.found_report_id,
            type: 'found',
            title: m.item_name || m.found_item_name || 'Found item',
            location: m.location || m.found_location || '',
            description: m.description || m.found_description || '',
            category: m.category || m.found_category || '',
            image: m.image_path ? undefined : undefined,
          }
      if (!found.image && m.image_path) {
        found.image = `/${String(m.image_path).replace(/^\//, '')}`
      }
      return {
        id: m.id || `${lost.id}-${found.id}`,
        lost,
        found,
        score: Math.round(m.similarity_score ?? m.score ?? 0),
        breakdown: m.score_breakdown || null,
      }
    }).sort((a, b) => b.score - a.score)
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load matches'))
  }
}
