<!--
  文件：Bus.vue - 校车服务页面
  作用：显示校车路线列表，用户可以查看每条路线的发车时刻表
  功能：
    1. 显示所有校车路线（名称、起点、终点）
    2. 展开/收起时刻表
    3. 显示每趟车的发车时间、剩余座位、运行日
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">校车服务</h1>
      </div>
    </header>

    <div class="container mx-auto p-4">
      <!-- 路线列表 -->
      <div class="space-y-4">
        <!--
          v-for="route in routes": 循环渲染每条校车路线
          注意：这里的 route 是循环变量名，和 vue-router 的 route 不同
          为了避免混淆，这里应该叫 busRoute，但原代码用了 route
        -->
        <div
          v-for="route in routes"
          :key="route.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <!-- 路线基本信息 -->
          <div class="flex items-center justify-between mb-3">
            <div>
              <h3 class="font-semibold text-lg">{{ route.name }}</h3>
              <!-- 路线方向：从哪个校区到哪个校区 -->
              <p class="text-sm text-gray-600">
                {{ route.from_campus }} → {{ route.to_campus }}
              </p>
            </div>
            <!--
              展开/收起按钮
              切换逻辑：如果当前已展开则收起，否则展开
              expandedRoute 存储当前展开的路线 ID
            -->
            <button
              @click="toggleSchedule(route.id)"
              class="text-lzu-blue"
            >
              {{ expandedRoute === route.id ? '收起' : '查看时刻' }}
            </button>
          </div>

          <!--
            时刻表展开区域
            v-if="expandedRoute === route.id": 只有当前路线被选中展开时才显示
            border-t: 顶部边框线，与路线信息分隔
          -->
          <div v-if="expandedRoute === route.id" class="border-t pt-3">
            <div v-if="loadingSchedules" class="text-center py-4 text-gray-500">
              加载中...
            </div>
            <div v-else class="space-y-2">
              <!--
                v-for="schedule in schedules": 循环渲染该路线的所有班次
                每个班次显示发车时间、剩余座位、运行日
              -->
              <div
                v-for="schedule in schedules"
                :key="schedule.id"
                class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <!-- 发车时间 -->
                  <div class="font-semibold">{{ schedule.departure_time }}</div>
                  <!-- 剩余座位：总座位数 - 已预订座位数 -->
                  <div class="text-xs text-gray-500">
                    座位: {{ schedule.seats - schedule.booked_seats }}/{{ schedule.seats }}
                  </div>
                </div>
                <!-- 运行日类型：仅工作日还是每日运行 -->
                <div class="text-xs text-gray-500">
                  {{ schedule.weekday_only ? '仅工作日' : '每日' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无路线数据时的空状态 -->
      <div v-if="routes.length === 0" class="text-center py-8 text-gray-500">
        暂无校车路线
      </div>
    </div>

    <!-- 底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { busAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

// 校车路线列表
const routes = ref([])
// 当前路线的时刻表数据
const schedules = ref([])
// 当前展开的路线 ID（为 null 表示没有展开任何路线）
const expandedRoute = ref(null)
// 时刻表加载状态
const loadingSchedules = ref(false)

// 获取所有校车路线
const fetchRoutes = async () => {
  try {
    routes.value = await busAPI.getRoutes()
  } catch (error) {
    console.error('获取路线失败:', error)
  }
}

// 切换路线的时刻表展开/收起状态
// 参数 routeId 是要展开/收起的路线 ID
const toggleSchedule = async (routeId) => {
  // 如果点击的是已展开的路线，则收起（设置为 null）
  if (expandedRoute.value === routeId) {
    expandedRoute.value = null
    return // 提前退出，不加载数据
  }

  // 展开新的路线
  expandedRoute.value = routeId
  loadingSchedules.value = true

  try {
    // 获取该路线的时刻表
    schedules.value = await busAPI.getSchedules(routeId)
  } catch (error) {
    console.error('获取时刻表失败:', error)
  } finally {
    loadingSchedules.value = false
  }
}

// 页面挂载后获取路线列表
onMounted(() => {
  fetchRoutes()
})
</script>
