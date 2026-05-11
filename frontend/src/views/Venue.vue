<!--
  文件：Venue.vue - 场馆预约页面
  作用：显示可预约的场馆列表，用户可以查看时段并进行预约
  功能：
    1. 显示所有可预约的场馆
    2. 点击场馆查看可预约的时间段
    3. 选择时段进行预约
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md">
      <div class="flex items-center">
        <!-- 返回按钮 -->
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">场馆预约</h1>
      </div>
    </header>

    <div class="container mx-auto p-4">
      <!-- 场馆列表 -->
      <!--
        space-y-4: 子元素之间垂直间距为 1rem
      -->
      <div class="space-y-4">
        <!--
          v-for="venue in venues": 循环渲染场馆列表
          @click="selectVenue(venue)": 点击场馆时调用选择函数
            selectVenue 会加载该场馆的可预约时段
          cursor-pointer: 鼠标悬停时显示手型光标，提示用户可以点击
        -->
        <div
          v-for="venue in venues"
          :key="venue.id"
          @click="selectVenue(venue)"
          class="bg-white rounded-lg p-4 shadow-md cursor-pointer hover:shadow-lg transition-shadow"
        >
          <div class="flex items-center">
            <div class="text-3xl mr-4">🏀</div>
            <div class="flex-1">
              <h3 class="font-semibold text-lg">{{ venue.name }}</h3>
              <p class="text-sm text-gray-500">{{ venue.location }}</p>
            </div>
            <div class="text-lzu-blue">→</div>
          </div>
        </div>
      </div>

      <!--
        时段选择对话框（从底部弹出）
        v-if="selectedVenue": 只有选中了场馆才显示
        fixed inset-0: 全屏遮罩
        flex items-end: 内容从底部弹出（底部对齐）
        @click="selectedVenue = null": 点击遮罩关闭对话框
      -->
      <div
        v-if="selectedVenue"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50"
        @click="selectedVenue = null"
      >
        <!--
          弹窗内容
          @click.stop: 阻止点击事件冒泡到父元素
          为什么需要：点击弹窗内部时不关闭弹窗，只有点击遮罩才关闭
          如果不阻止冒泡，点击弹窗内部也会触发父元素的 click 事件导致关闭
        -->
        <div
          @click.stop
          class="bg-white w-full rounded-t-2xl p-6 max-h-[80vh] overflow-y-auto"
        >
          <h2 class="text-xl font-bold mb-4">{{ selectedVenue.name }} - 可预约时段</h2>

          <!-- 加载中提示 -->
          <div v-if="loadingSlots" class="text-center py-8 text-gray-500">加载中...</div>

          <!-- 时段列表 -->
          <div v-else class="space-y-3">
            <!--
              v-for="slot in timeSlots": 循环渲染每个可预约时段
              每个时段显示日期、时间范围、剩余容量和预约按钮
            -->
            <div
              v-for="slot in timeSlots"
              :key="slot.id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-center">
                <div>
                  <!-- 日期 -->
                  <div class="font-semibold">
                    {{ formatDate(slot.date) }}
                  </div>
                  <!-- 时间范围 -->
                  <div class="text-sm text-gray-600">
                    {{ slot.start_time }} - {{ slot.end_time }}
                  </div>
                  <!-- 剩余容量：总容量 - 已预约数量 = 剩余数量 -->
                  <div class="text-xs text-gray-500 mt-1">
                    剩余: {{ slot.capacity - slot.booked_count }}/{{ slot.capacity }}
                  </div>
                </div>
                <!-- 预约按钮 -->
                <button
                  @click="bookSlot(slot.id)"
                  :disabled="bookingSlot === slot.id"
                  class="bg-lzu-blue text-white px-6 py-2 rounded-lg hover:bg-blue-800 disabled:opacity-50"
                >
                  {{ bookingSlot === slot.id ? '预约中...' : '预约' }}
                </button>
              </div>
            </div>

            <!-- 无可用时段提示 -->
            <div v-if="timeSlots.length === 0" class="text-center py-8 text-gray-500">
              暂无可预约时段
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { venueAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

// 场馆列表
const venues = ref([])
// 当前选中的场馆（为 null 时不显示时段弹窗）
const selectedVenue = ref(null)
// 选中场馆的可预约时段列表
const timeSlots = ref([])
// 时段加载状态
const loadingSlots = ref(false)
// 正在预约的时段 ID（用于禁用对应按钮防止重复点击）
const bookingSlot = ref(null)

// 获取所有场馆列表
const fetchVenues = async () => {
  try {
    venues.value = await venueAPI.getVenues()
  } catch (error) {
    console.error('获取场馆列表失败:', error)
  }
}

// 选择场馆：加载该场馆的可预约时段
// 参数 venue 是用户点击的场馆对象
const selectVenue = async (venue) => {
  // 设置选中的场馆，触发弹窗显示
  selectedVenue.value = venue
  loadingSlots.value = true
  try {
    // 获取该场馆未来 3 天的可预约时段
    // days: 3 表示查询参数，告诉后端只返回未来 3 天的数据
    timeSlots.value = await venueAPI.getTimeSlots(venue.id, { days: 3 })
  } catch (error) {
    console.error('获取时段失败:', error)
  } finally {
    loadingSlots.value = false
  }
}

// 预约某个时段
// 参数 slotId 是要预约的时段 ID
const bookSlot = async (slotId) => {
  // 记录正在预约的时段 ID，用于在界面上显示"预约中..."
  bookingSlot.value = slotId
  try {
    // 发送预约请求
    await venueAPI.createBooking({ time_slot_id: slotId })
    alert('预约成功！')
    // 关闭弹窗
    selectedVenue.value = null
  } catch (error) {
    // 从服务器响应中提取错误信息，或显示默认错误信息
    alert(error.response?.data?.detail || '预约失败')
  } finally {
    // 清除预约中状态
    bookingSlot.value = null
  }
}

// 格式化日期：将 ISO 日期字符串转换为 "X月X日" 格式
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  // getMonth() 返回 0-11（0 代表一月），所以要 +1
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 页面挂载后获取场馆列表
onMounted(() => {
  fetchVenues()
})
</script>
