// ==========================================
// 文件：request.js - HTTP 请求封装层
// 作用：创建一个统一的 axios 实例，配置请求拦截器和响应拦截器
// 为什么需要这个文件：
//   1. 避免每个 API 请求都重复配置 baseURL 和超时时间
//   2. 自动在请求头中携带用户 token（登录凭证）
//   3. 统一处理后端返回的错误，避免在每个组件中重复写错误处理代码
// ==========================================

// 从 axios 库导入 axios 对象
// axios 是一个用于发送 HTTP 请求的 JavaScript 库，可以向服务器发送 GET、POST 等请求
import axios from 'axios'

// 创建一个 axios 实例（可以理解为一个定制化的 HTTP 客户端）
// 后续所有 API 调用都使用这个实例，而不是直接使用 axios
const api = axios.create({
  // 所有请求的基础 URL，所有 API 请求都会自动加上这个前缀
  // 例如：api.get('/products') 实际会请求 '/api/v1/products'
  // 这样写是因为后端所有接口都在 /api/v1 路径下
  baseURL: '/api/v1',

  // 请求超时时间设置为 15 秒（15000 毫秒）
  // 为什么是 15 秒：太短可能网络慢时请求会失败，太长用户等待体验差
  timeout: 15000,
})

// ==========================================
// 请求拦截器：在每个请求发出之前自动执行的函数
// 作用：自动为每个请求添加用户认证 token
// 为什么需要：
//   后端 API 需要验证用户身份，每次请求都要带上 token
//   如果不加拦截器，就需要在每个 API 调用处手动添加 token，非常麻烦
// ==========================================
api.interceptors.request.use(
  // 第一个参数：请求成功时执行的函数
  // config 是 axios 的请求配置对象，包含 headers（请求头）等信息
  (config) => {
    // 从浏览器的 localStorage（本地存储）中读取 token
    // localStorage 是浏览器提供的持久化存储，关闭浏览器后数据不会丢失
    // 用户登录后 token 会保存在这里
    const token = localStorage.getItem('token')

    // 如果 token 存在（用户已登录），则将 token 添加到请求头中
    // Authorization 是 HTTP 标准的认证头字段
    // Bearer 是一种认证方案，表示这是一个持有者 token
    // 后端会检查这个头来验证用户身份
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 返回修改后的配置对象，让请求继续发送
    // 如果不返回 config，请求会被阻止
    return config
  },
  // 第二个参数：请求配置出错时执行的函数
  // Promise.reject 表示抛出一个错误，让后续的 catch 能捕获到
  (error) => Promise.reject(error)
)

// ==========================================
// 响应拦截器：在每个响应返回后自动执行的函数
// 作用：
//   1. 解包后端返回的数据（后端格式是 {code, msg, data}，我们只需要 data）
//   2. 统一处理业务错误（code 不为 0 表示业务逻辑出错）
//   3. 处理 HTTP 状态码错误（如 401 未授权、500 服务器错误）
// ==========================================
api.interceptors.response.use(
  // 第一个参数：HTTP 请求成功（状态码 2xx）时执行的函数
  // response 是 axios 的响应对象，response.data 是服务器返回的原始数据
  (response) => {
    // 获取响应体数据
    const body = response.data

    // 检查响应体是否是统一的业务响应格式：{code, msg, data}
    // 为什么要检查：后端有两种返回格式，一种是标准格式，一种是文件流等特殊格式
    // 只有标准格式才需要解包处理
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      // code === 0 表示业务逻辑执行成功
      // 为什么用 0 表示成功：这是后端约定的，0 通常表示无错误
      if (body.code === 0) {
        // 直接返回 data 字段，这样组件中使用时不需要再写 response.data
        // 例如：const result = await api.get('/products') 直接得到数据
        return body.data
      }

      // code 不为 0 表示业务逻辑出错（如：商品不存在、权限不足等）
      // 创建一个 Error 对象，包含后端返回的错误消息
      const err = new Error(body.msg || '请求失败')
      // 将业务错误码附加到错误对象上，方便后续判断具体错误类型
      err.code = body.code
      // 标记这是业务错误（区别于网络错误或 HTTP 错误）
      err.businessError = true
      // 抛出错误，让调用方的 catch 能捕获到
      return Promise.reject(err)
    }

    // 非统一结构的响应（极少见，如文件下载返回二进制流）
    // 直接返回原始响应体，不进行解包处理
    return body
  },
  // 第二个参数：HTTP 请求失败（状态码非 2xx）时执行的函数
  // error 是 axios 的错误对象，error.response 包含服务器的响应信息
  (error) => {
    // 从错误对象中提取 HTTP 状态码（如 401、403、404、500 等）
    // 使用可选链操作符 ?. 防止 error.response 为 undefined 时报错
    const status = error.response?.status
    // 提取服务器返回的错误响应体
    const body = error.response?.data
    // 从响应体中提取错误消息，优先使用 msg，其次是 detail，最后使用 axios 自带的错误消息
    // 为什么有多个备选：不同后端框架返回的错误字段名可能不同
    const msg = body?.msg || body?.detail || error.message || '网络异常'

    // 特殊处理 401 状态码（未授权/未登录/登录过期）
    // 为什么要特殊处理：401 表示用户的 token 已失效，需要重新登录
    if (status === 401) {
      // 清除本地存储中的 token 和用户信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 如果当前不在登录页面，则跳转到登录页面
      // 为什么要检查路径：避免已经在登录页面时重复跳转导致死循环
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
    }

    // 创建一个新的错误对象，包含详细的错误信息
    const err = new Error(msg)
    // 将 HTTP 状态码附加到错误对象上
    err.status = status
    // 将业务错误码或 HTTP 状态码附加到错误对象上
    err.code = body?.code ?? status
    // 抛出错误，让调用方的 catch 能捕获到
    return Promise.reject(err)
  }
)

// 导出这个定制化的 axios 实例
// 其他文件可以通过 import api from './request' 使用这个实例
export default api
