import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// 请求拦截器：自动注入 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：解包 {code, msg, data}，非 0 抛出业务错误
api.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      if (body.code === 0) {
        return body.data
      }
      const err = new Error(body.msg || '请求失败')
      err.code = body.code
      err.businessError = true
      return Promise.reject(err)
    }
    // 非统一结构（极少见，如文件流）直接返回
    return body
  },
  (error) => {
    const status = error.response?.status
    const body = error.response?.data
    const msg = body?.msg || body?.detail || error.message || '网络异常'

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
    }
    const err = new Error(msg)
    err.status = status
    err.code = body?.code ?? status
    return Promise.reject(err)
  }
)

export default api
