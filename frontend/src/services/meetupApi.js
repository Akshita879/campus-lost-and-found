import { http } from './api'
import { apiErrorMessage } from '../lib/mappers'

/** Lost owner → finder meetup note for a linked found report */
export async function submitFoundMeetup(foundReportId, meetupMessage) {
  try {
    return (await http.post(`/reports/${foundReportId}/meetup`, { meetup_message: meetupMessage })).data
  } catch (err) {
    throw new Error(apiErrorMessage(err, 'Could not save meetup details'))
  }
}
