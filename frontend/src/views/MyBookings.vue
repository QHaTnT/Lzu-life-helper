<!--
  文件：MyBookings.vue - 我的预约页面
  作用：显示当前用户的所有场馆预约记录
  功能：
    1. 显示预约列表（场馆名、时段、状态）
    2. 支持取消预约
    3. 按状态筛选（全部/已确认/已取消/已完成）
    4. 空状态提示
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的预约</h1>
      </div>
    </header>

    <!-- 状态筛选标签 -->
    <div class="bg-white p-4 mb-4">
      <div class="flex gap-2 overflow-x-auto">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          @click="activeStatus = tab.value"
          :class="[
            'px-4 py-1 rounded-full text-sm whitespace-nowrap',
            activeStatus === tab.value ? 'bg-lzu-blue text-white' : 'bg-gray-200 text-gray-700',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="container mx-auto px-4 space-y-4">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <!-- 空状态 -->
      <div v-else-if="filteredBookings.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-4">📅</div>
        <p>暂无预约记录</p>
        <button @click="$router.push('/venue')" class="mt-4 text-lzu-blue">去预约</button>
      </div>

      <!-- 预约列表 -->
      <div
        v-for="booking in filteredBookings"
        :key="booking.id"
        class="bg-white rounded-lg p-4 shadow-md"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <!-- 场馆名称 -->
            <h3 class="font-semibold">{{ booking.venue_name || '场馆' + booking.venue_id }}</h3>
            <!-- 日期和时段 -->
            <div class="text-sm text-gray-600 mt-1">
              📅 {{ formatDate(booking.slot_date) }}
            </div>
            <div class="text-sm text-gray-600">
              🕐 {{ booking.start_time }} - {{ booking.end_time }}
            </div>
          </div>
          <!-- 状态标签 -->
          <span
            :class="[
              'text-xs px-2 py-1 rounded',
              statusStyle(booking.status),
            ]"
          >
            {{ statusLabel(booking.status) }}
          </span>
        </div>

        <!-- 取消按钮（仅已确认的预约可取消） -->
        <div v-if="booking.status === 'confirmed' || booking.status === 'pending'" class="mt-3 text-right">
          <button
            @click="handleCancel(booking.id)"
            class="text-sm text-red-400 hover:text-red-600"
          >
            取消预约
          </button>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { venueAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

// 预约列表
const bookings = ref([])
// 加载状态
const loading = ref(true)
// 当前筛选状态
const activeStatus = ref('')

// 状态筛选标签
const statusTabs = [
  { label: '全部', value: '' },
  { label: '已确认', value: 'confirmed' },
  { label: '已取消', value: 'cancelled' },
  { label: '已完成', value: 'completed' },
]

// 根据筛选状态过滤预约列表
const filteredBookings = computed(() => {
  if (!activeStatus.value) return bookings.value
  return bookings.value.filter(b => b.status === activeStatus.value)
})

// 获取我的预约列表
const fetchMyBookings = async () => {
  try {
    bookings.value = await venueAPI.getMyBookings()
  } catch (error) {
    console.error('获取预约记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消预约
const handleCancel = async (id) => {
  if (!confirm('确定取消该预约？')) return
  try {
    await venueAPI.cancelBooking(id)
    // 从列表中移除已取消的预约，或更新状态
    const booking = bookings.value.find(b => b.id === id)
    if (booking) booking.status = 'cancelled'
    alert('已取消预约')
  } catch (error) {
    alert(error.message || '取消失败')
  }
}

// 格式化日期：将 ISO 时间转换为 "X月X日" 格式
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 状态标签文字
const statusLabel = (status) => {
  const map = { pending: '待确认', confirmed: '已确认', cancelled: '已取消', completed: '已完成' }
  return map[status] || status
}

// 状态标签样式
const statusStyle = (status) => {
  const map = {
    pending: 'bg-yellow-100 text-yellow-700',
    confirmed: 'bg-green-100 text-green-700',
    cancelled: 'bg-gray-100 text-gray-500',
    completed: 'bg-blue-100 text-blue-700',
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

onMounted(() => {
  fetchMyBookings()
})
</script>
