<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
    <div class="flex justify-around py-2">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center py-1 px-3 min-w-0"
        :class="isActive(item.path) ? 'text-lzu-blue' : 'text-gray-500'"
      >
        <span class="text-2xl leading-none">{{ item.icon }}</span>
        <span class="text-xs mt-1 whitespace-nowrap">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/home', icon: '🏠', label: '首页' },
  { path: '/market', icon: '🛒', label: '二手' },
  { path: '/bus', icon: '🚌', label: '出行' },
  { path: '/venue', icon: '🏀', label: '预约' },
  { path: '/community', icon: '💬', label: '生活圈' },
  { path: '/profile', icon: '👤', label: '我的' },
]

const isActive = (path) => route.path === path || route.path.startsWith(path + '/')
</script>
