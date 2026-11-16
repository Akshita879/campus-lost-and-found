import { http, USE_MOCKS, setToken, getToken } from './api'

export async function register({ name, email, password }) {
  if (USE_MOCKS) return { id: 1, name, email }
  return (await http.post('/auth/register', { name, email, password })).data
}

export async function login({ email, password }) {
  if (USE_MOCKS) {
    setToken('mock-token')
    return { access_token: 'mock-token', token_type: 'bearer', user: { id: 1, name: 'Demo User', email } }
  }
  const data = (await http.post('/auth/login', { email, password })).data
  setToken(data.access_token)
  return data
}

export async function fetchMe() {
  if (USE_MOCKS) {
    if (!getToken()) return null
    return { id: 1, name: 'Demo User', email: 'demo@campus.edu' }
  }
  if (!getToken()) return null
  try {
    return (await http.get('/auth/me')).data
  } catch {
    setToken(null)
    return null
  }
}

export function logout() {
  setToken(null)
}
