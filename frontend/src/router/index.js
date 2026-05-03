import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/views/Market.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/market/:id',
    name: 'ProductDetail',
    component: () => import('@/views/ProductDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/venue',
    name: 'Venue',
    component: () => import('@/views/Venue.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/bus',
    name: 'Bus',
    component: () => import('@/views/Bus.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/Community.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('@/views/MyProducts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-posts',
    name: 'MyPosts',
    component: () => import('@/views/MyPosts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-activities',
    name: 'MyActivities',
    component: () => import('@/views/MyActivities.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    next('/home')
  } else {
    next()
  }
})

export default router
