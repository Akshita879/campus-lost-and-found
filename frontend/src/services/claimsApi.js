import { http } from './api'
import { apiErrorMessage } from '../lib/mappers'

export async function approveClaim(claimId) {
  try {
    return (await http.post(`/claims/${claimId}/approve`)).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not approve claim'))
  }
}

export async function rejectClaim(claimId) {
  try {
    return (await http.post(`/claims/${claimId}/reject`)).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not reject claim'))
  }
}

export async function submitMeetup(claimId, meetupMessage) {
  try {
    return (await http.post(`/claims/${claimId}/meetup`, { meetup_message: meetupMessage })).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not save meetup details'))
  }
}

export async function listIncomingClaims() {
  try {
    return (await http.get('/claims/incoming')).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not load claims'))
  }
}
