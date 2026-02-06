import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/admin/#/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关
export const login = (username, password) => api.post('/auth/login', { username, password })
export const getCurrentUser = () => api.get('/auth/me')

// 菜单相关
export const getMenu = (storeId = 1) => api.get(`/menu/?store_id=${storeId}`)
export const createMenuItem = (data) => api.post('/menu/', data)
export const updateMenuItem = (id, data) => api.put(`/menu/${id}`, data)
export const deleteMenuItem = (id) => api.delete(`/menu/${id}`)

// 订单相关
export const getOrders = (params = {}) => api.get('/orders/', { params })
export const getOrder = (id) => api.get(`/orders/${id}`)
export const updateOrderStatus = (id, status) => api.put(`/orders/${id}/status`, null, { params: { status } })
export const updatePaymentStatus = (id, paymentStatus) => api.put(`/orders/${id}/payment`, null, { params: { payment_status: paymentStatus } })

// 库存相关
export const updateStock = (id, stock) => api.put(`/menu/${id}/stock`, { stock })

// 统计相关
export const getStats = (params = {}) => api.get('/stats/', { params })

export default api
