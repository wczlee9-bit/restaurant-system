import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000
})

// 获取菜单
export const getMenu = async (storeId = 1) => {
  const response = await api.get(`/menu/?store_id=${storeId}`)
  return response.data
}

// 创建订单
export const createOrder = async (orderData) => {
  const response = await api.post('/orders/', orderData)
  return response.data
}

// 获取订单详情
export const getOrder = async (orderId) => {
  const response = await api.get(`/orders/${orderId}`)
  return response.data
}

// 获取订单列表
export const getOrders = async (params = {}) => {
  const response = await api.get('/orders/', { params })
  return response.data
}

// 用户登录
export const login = async (username, password) => {
  const response = await api.post('/auth/login', { username, password })
  return response.data
}

export default api
