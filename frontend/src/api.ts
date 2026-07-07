import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pos_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && !location.pathname.startsWith('/login')) {
      localStorage.removeItem('pos_token')
      location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api

export const fmt = (n?: number) =>
  n == null ? 'Rp 0' : new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(Number(n))
