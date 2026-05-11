// ==========================================
// 文件：auth.js - 用户认证状态管理（Pinia Store）
// 作用：管理用户的登录状态、token、用户信息
// 为什么需要：
//   1. 多个组件（登录页、首页、个人中心等）都需要知道用户是否登录
//   2. 用户 token 需要在多个请求中使用
//   3. 需要在页面刷新后保持登录状态（持久化）
// ==========================================

// 从 pinia 库导入 defineStore 函数
// Pinia 是 Vue 3 的官方状态管理库（类似 Vuex），用于在组件间共享数据
import { defineStore } from 'pinia'

// 从 Vue 导入 ref 和 computed
// ref 用于创建响应式变量（值变化时界面自动更新）
// computed 用于创建计算属性（依赖其他变量自动计算）
import { ref, computed } from 'vue'

// 导入认证相关的 API 函数
import { authAPI } from '@/api'

// 定义一个名为 'auth' 的 Store（状态仓库）
// defineStore 的第一个参数 'auth' 是这个 Store 的唯一标识符
// 第二个参数是一个函数，这是 Pinia 的 Setup Store 语法（使用 Vue 3 的组合式 API）
export const useAuthStore = defineStore('auth', () => {
  // ==========================================
  // 状态定义（ref）
  // ref 创建的变量是响应式的：当值变化时，使用这个变量的所有组件会自动更新
  // ==========================================

  // 用户的访问令牌（token）
  // 初始化时从 localStorage 读取，如果 localStorage 中没有则默认为空字符串
  // 为什么从 localStorage 读取：用户刷新页面后，内存中的变量会丢失
  //   但 localStorage 中的数据会保留，这样用户不需要重新登录
  const token = ref(localStorage.getItem('token') || '')

  // 当前登录用户的信息对象
  // 包含 username、student_id、avatar 等用户字段
  // JSON.parse 将 localStorage 中的 JSON 字符串转换为 JavaScript 对象
  // 如果 localStorage 中没有 user 数据，JSON.parse('null') 会返回 null
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // ==========================================
  // 计算属性（computed）
  // computed 的值会自动根据依赖的变量变化而更新
  // ==========================================

  // 判断用户是否已登录
  // !! 是双重否定操作符：将任意值转换为布尔值
  // !!'' 为 false（空字符串表示未登录），!!'abc' 为 true（有 token 表示已登录）
  const isAuthenticated = computed(() => !!token.value)

  // ==========================================
  // 操作方法
  // 这些方法用于修改状态和与后端交互
  // ==========================================

  // 登录方法：接收用户凭证（用户名和密码），向服务器发送登录请求
  // async 关键字表示这个函数是异步函数，内部可以使用 await 等待异步操作完成
  // credentials 是登录表单数据，格式如 { username: 'xxx', password: 'xxx' }
  const login = async (credentials) => {
    // 调用登录 API，await 会等待服务器返回结果
    // 如果登录成功，response 包含 access_token 和 user 信息
    // 如果登录失败，会抛出错误，被调用方的 catch 捕获
    const response = await authAPI.login(credentials)

    // 将服务器返回的 token 保存到状态变量中
    // 响应式变量必须通过 .value 来读写
    token.value = response.access_token

    // 将服务器返回的用户信息保存到状态变量中
    user.value = response.user

    // 同时将 token 和用户信息保存到 localStorage（浏览器本地存储）
    // 为什么保存两份：ref 变量在页面刷新后会丢失，localStorage 会保留
    // 下次刷新页面时，ref 的初始值会从 localStorage 读取，实现持久化
    localStorage.setItem('token', response.access_token)
    // localStorage 只能存储字符串，所以需要用 JSON.stringify 将对象转换为字符串
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  // 注册方法：向服务器提交新用户信息
  // userData 包含 student_id、username、password 等注册字段
  // 注册成功后不自动登录，用户需要手动登录
  const register = async (userData) => {
    // 调用注册 API，只发送数据，不处理返回值
    // 如果注册失败（如用户名已存在），会抛出错误
    await authAPI.register(userData)
  }

  // 登出方法：清除所有登录状态
  // 不需要调用服务器，因为 token 的验证在前端本地清除即可
  const logout = () => {
    // 清空内存中的 token 和用户信息
    token.value = ''
    user.value = null

    // 同时清除 localStorage 中的数据
    // 为什么两边都要清除：确保刷新页面后登录状态也被清除
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 更新用户信息方法：用于修改个人资料后同步状态
  // userData 是新的用户信息字段
  const updateUser = (userData) => {
    // 使用展开运算符 ... 合并旧数据和新数据
    // 例如：旧数据 { username: '张三', avatar: 'old.jpg' }
    //       新数据 { avatar: 'new.jpg' }
    //       结果：{ username: '张三', avatar: 'new.jpg' }
    // 为什么用这种方式：确保只更新传入的字段，保留其他字段不变
    user.value = { ...user.value, ...userData }

    // 同步更新 localStorage，确保刷新页面后新数据也能保留
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  // ==========================================
  // 返回所有需要暴露给外部使用的状态和方法
  // 组件通过 useAuthStore() 获取这些状态和方法
  // ==========================================
  return {
    token,          // token 状态
    user,           // 用户信息状态
    isAuthenticated, // 是否已登录（计算属性）
    login,          // 登录方法
    register,       // 注册方法
    logout,         // 登出方法
    updateUser,     // 更新用户信息方法
  }
})
