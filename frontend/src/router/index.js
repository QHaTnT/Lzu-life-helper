// ==========================================
// 文件：index.js - 路由配置文件
// 作用：定义应用的所有页面路径，以及访问这些页面时的权限控制
// 为什么需要：
//   1. 单页应用（SPA）只有一个 HTML 文件，通过路由切换显示不同的"页面"
//   2. 路由配置告诉浏览器：访问 /home 显示首页，访问 /market 显示二手市场等
//   3. 路由守卫可以拦截未登录用户访问需要登录的页面
// ==========================================

// 从 vue-router 导入创建路由的函数
// vue-router 是 Vue 的官方路由库
// createRouter 用于创建路由实例
// createWebHistory 用于创建 HTML5 History 模式的路由（URL 没有 # 号）
import { createRouter, createWebHistory } from 'vue-router'

// 导入认证 Store，用于在路由守卫中检查用户是否登录
import { useAuthStore } from '@/store/auth'

// ==========================================
// 路由配置数组：定义所有页面路径与组件的对应关系
// 每个路由对象包含：
//   - path: URL 路径
//   - name: 路由名称（用于编程式导航）
//   - component: 该路径对应的 Vue 组件（页面）
//   - meta: 自定义元数据，这里用来标记是否需要登录
// ==========================================
const routes = [
  // 根路径：访问 / 时自动重定向到 /home
  // redirect 属性用于将一个路径重定向到另一个路径
  {
    path: '/',
    redirect: '/home',
  },

  // 登录页面
  // () => import(...) 是动态导入（懒加载）
  // 为什么用懒加载：只在访问这个页面时才加载对应的代码，加快应用启动速度
  // meta.requiresAuth: false 表示这个页面不需要登录即可访问
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },

  // 注册页面
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },

  // 首页
  // meta.requiresAuth: true 表示这个页面需要登录才能访问
  // 未登录用户访问会被路由守卫拦截并跳转到登录页
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
  },

  // 二手市场页面
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue'),
    meta: { requiresAuth: true },
  },

  // 商品详情页面
  // :id 是动态路由参数，表示 URL 中的可变部分
  // 例如：/market/123 表示查看 ID 为 123 的商品
  // 在组件中通过 route.params.id 获取这个参数值
  {
    path: '/market/:id',
    name: 'ProductDetail',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { requiresAuth: true },
  },

  // 场馆预约页面
  {
    path: '/venue',
    name: 'Venue',
    component: () => import('@/views/Venue.vue'),
    meta: { requiresAuth: true },
  },

  // 校车服务页面
  {
    path: '/bus',
    name: 'Bus',
    component: () => import('@/views/Bus.vue'),
    meta: { requiresAuth: true },
  },

  // 生活圈（社区动态）页面
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/Community.vue'),
    meta: { requiresAuth: true },
  },

  // 个人中心页面
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true },
  },

  // 我的商品页面（管理自己发布的商品）
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('@/views/MyProducts.vue'),
    meta: { requiresAuth: true },
  },

  // 我的动态页面（管理自己发布的动态）
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('@/views/MyPosts.vue'),
    meta: { requiresAuth: true },
  },

  // 我的活动页面（管理自己报名或发布的活动）
  {
    path: '/my-activities',
    name: 'MyActivities',
    component: () => import('@/views/MyActivities.vue'),
    meta: { requiresAuth: true },
  },
]

// 创建路由实例
// createWebHistory() 使用 HTML5 History 模式
// 这种模式下 URL 没有 # 号，如 /home 而不是 /#/home
// 后端服务器需要配置支持这种模式（所有路径都返回 index.html）
const router = createRouter({
  history: createWebHistory(),
  routes, // 传入路由配置数组
})

// ==========================================
// 全局前置路由守卫（beforeEach）
// 作用：在每次页面跳转之前执行的拦截函数
// 为什么需要：
//   1. 阻止未登录用户访问需要登录的页面
//   2. 阻止已登录用户访问登录/注册页面（避免重复登录）
// 参数说明：
//   - to: 即将要访问的目标路由对象（包含 path、meta 等信息）
//   - from: 当前页面的路由对象（从哪里来）
//   - next: 一个函数，调用它才能继续页面跳转
// ==========================================
router.beforeEach((to, from, next) => {
  // 获取认证 Store 实例
  // 为什么在这里获取：路由守卫在每次路由跳转时都会执行，需要实时获取最新的登录状态
  const authStore = useAuthStore()

  // 情况1：目标页面需要登录，但用户未登录
  // to.meta.requiresAuth 来自路由配置中的 meta 字段
  // !authStore.isAuthenticated 检查用户是否没有登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 阻止访问目标页面，强制跳转到登录页
    // next('/login') 会中断当前导航，开始新的导航到 /login
    next('/login')
  }
  // 情况2：用户已登录，但想访问登录或注册页面
  // 已登录用户不需要再看登录页，直接跳转到首页
  else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    // 阻止跳转到登录/注册页，强制跳转到首页
    next('/home')
  }
  // 情况3：正常情况，允许跳转
  else {
    // next() 不传参数表示允许继续当前的导航
    // 页面会正常显示目标路由对应的组件
    next()
  }
})

// 导出路由实例，在 main.js 中挂载到 Vue 应用上
export default router
