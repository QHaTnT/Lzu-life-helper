<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <header class="bg-lzu-blue text-white p-4 shadow-lg">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">兰州大学生活助手</h1>
        <div class="text-sm">{{ user?.username }}</div>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto p-4 pb-20">
      <div class="grid grid-cols-2 gap-4 mb-6">
        <!-- 功能卡片 -->
        <router-link
          to="/market"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🛒</div>
          <div class="font-semibold text-gray-800">二手市场</div>
          <div class="text-xs text-gray-500 mt-1">买卖闲置物品</div>
        </router-link>

        <router-link
          to="/venue"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🏀</div>
          <div class="font-semibold text-gray-800">场馆预约</div>
          <div class="text-xs text-gray-500 mt-1">预约运动场馆</div>
        </router-link>

        <router-link
          to="/bus"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🚌</div>
          <div class="font-semibold text-gray-800">校车服务</div>
          <div class="text-xs text-gray-500 mt-1">查看校车时刻</div>
        </router-link>

        <router-link
          to="/community"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">💬</div>
          <div class="font-semibold text-gray-800">生活圈</div>
          <div class="text-xs text-gray-500 mt-1">校园动态分享</div>
        </router-link>
      </div>

      <!-- 快捷信息 -->
      <div class="bg-white rounded-xl p-4 shadow-md">
        <h2 class="font-semibold text-gray-800 mb-3">快捷信息</h2>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex justify-between">
            <span>今日天气</span>
            <span class="text-lzu-blue">晴 15°C</span>
          </div>
          <div class="flex justify-between">
            <span>图书馆开放</span>
            <span class="text-lzu-blue">8:00 - 22:00</span>
          </div>
          <div class="flex justify-between">
            <span>食堂营业</span>
            <span class="text-lzu-blue">正常营业</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部导航 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import BottomNav from '@/components/BottomNav.vue'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
</script>
