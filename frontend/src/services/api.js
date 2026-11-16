import axios from 'axios'
// Flip VITE_USE_MOCKS=false and set VITE_API_URL to use a real backend.
export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false'
export const http = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api', timeout: 15000 })
export const delay = (ms = 600) => new Promise(r => setTimeout(r, ms))

const TOKEN_KEY = 'access_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

http.interceptors.request.use(config => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
