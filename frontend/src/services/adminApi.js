import { http } from './api'
import { apiErrorMessage, reportToItem } from '../lib/mappers'

export async function adminListUsers() {
  try {
    return (await http.get('/admin/users')).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load users'))
  }
}

export async function adminDeleteUser(userId) {
  try {
    return (await http.delete(`/admin/users/${userId}`)).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not delete user'))
  }
}

export async function adminListReports() {
  try {
    const rows = (await http.get('/admin/reports')).data
    return (rows || []).map(reportToItem)
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load reports'))
  }
}

export async function adminDeleteReport(reportId) {
  try {
    return (await http.delete(`/admin/reports/${reportId}`)).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not delete report'))
  }
}

export async function adminClearReports() {
  try {
    return (await http.post('/admin/clear-reports')).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not clear reports'))
  }
}
