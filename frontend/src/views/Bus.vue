<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">校车服务</h1>
      </div>
    </header>

    <div class="container mx-auto p-4">
      <!-- 路线列表 -->
      <div class="space-y-4">
        <div
          v-for="route in routes"
          :key="route.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 class="font-semibold text-lg">{{ route.name }}</h3>
              <p class="text-sm text-gray-600">
                {{ route.from_campus }} → {{ route.to_campus }}
              </p>
            </div>
            <button
              @click="toggleSchedule(route.id)"
              class="text-lzu-blue"
            >
              {{ expandedRoute === route.id ? '收起' : '查看时刻' }}
            </button>
          </div>

          <!-- 时刻表 -->
          <div v-if="expandedRoute === route.id" class="border-t pt-3">
            <div v-if="loadingSchedules" class="text-center py-4 text-gray-500">
              加载中...
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="schedule in schedules"
                :key="schedule.id"
                class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <div class="font-semibold">{{ schedule.departure_time }}</div>
                  <div class="text-xs text-gray-500">
                    座位: {{ schedule.seats - schedule.booked_seats }}/{{ schedule.seats }}
                  </div>
                </div>
                <div class="text-xs text-gray-500">
                  {{ schedule.weekday_only ? '仅工作日' : '每日' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="routes.length === 0" class="text-center py-8 text-gray-500">
        暂无校车路线
      </div>
    </div>

    <!-- 底部导航 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
      <div class="container mx-auto flex justify-around py-3">
        <router-link to="/home" class="flex flex-col items-center text-gray-500">
          <span class="text-2xl">🏠</span>
          <span class="text-xs mt-1">首页</span>
        </router-link>
        <router-link to="/market" class="flex flex-col items-center text-gray-500">
          <span class="text-2xl">🛒</span>
          <span class="text-xs mt-1">二手</span>
        </router-link>
        <router-link to="/community" class="flex flex-col items-center text-gray-500">
          <span class="text-2xl">💬</span>
          <span class="text-xs mt-1">生活圈</span>
        </router-link>
        <router-link to="/profile" class="flex flex-col items-center text-gray-500">
          <span class="text-2xl">👤</span>
          <span class="text-xs mt-1">我的</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { busAPI } from '@/api'

const routes = ref([])
const schedules = ref([])
const expandedRoute = ref(null)
const loadingSchedules = ref(false)

const fetchRoutes = async () => {
  try {
    routes.value = await busAPI.getRoutes()
  } catch (error) {
    console.error('获取路线失败:', error)
  }
}

const toggleSchedule = async (routeId) => {
  if (expandedRoute.value === routeId) {
    expandedRoute.value = null
    return
  }

  expandedRoute.value = routeId
  loadingSchedules.value = true

  try {
    schedules.value = await busAPI.getSchedules(routeId)
  } catch (error) {
    console.error('获取时刻表失败:', error)
  } finally {
    loadingSchedules.value = false
  }
}

onMounted(() => {
  fetchRoutes()
})
</script>
