<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">场馆预约</h1>
      </div>
    </header>

    <div class="container mx-auto p-4">
      <!-- 场馆列表 -->
      <div class="space-y-4">
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

      <!-- 时段选择对话框 -->
      <div
        v-if="selectedVenue"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50"
        @click="selectedVenue = null"
      >
        <div
          @click.stop
          class="bg-white w-full rounded-t-2xl p-6 max-h-[80vh] overflow-y-auto"
        >
          <h2 class="text-xl font-bold mb-4">{{ selectedVenue.name }} - 可预约时段</h2>

          <div v-if="loadingSlots" class="text-center py-8 text-gray-500">加载中...</div>

          <div v-else class="space-y-3">
            <div
              v-for="slot in timeSlots"
              :key="slot.id"
              class="border border-gray-200 rounded-lg p-4"
            >
              <div class="flex justify-between items-center">
                <div>
                  <div class="font-semibold">
                    {{ formatDate(slot.date) }}
                  </div>
                  <div class="text-sm text-gray-600">
                    {{ slot.start_time }} - {{ slot.end_time }}
                  </div>
                  <div class="text-xs text-gray-500 mt-1">
                    剩余: {{ slot.capacity - slot.booked_count }}/{{ slot.capacity }}
                  </div>
                </div>
                <button
                  @click="bookSlot(slot.id)"
                  :disabled="bookingSlot === slot.id"
                  class="bg-lzu-blue text-white px-6 py-2 rounded-lg hover:bg-blue-800 disabled:opacity-50"
                >
                  {{ bookingSlot === slot.id ? '预约中...' : '预约' }}
                </button>
              </div>
            </div>

            <div v-if="timeSlots.length === 0" class="text-center py-8 text-gray-500">
              暂无可预约时段
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { venueAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const venues = ref([])
const selectedVenue = ref(null)
const timeSlots = ref([])
const loadingSlots = ref(false)
const bookingSlot = ref(null)

const fetchVenues = async () => {
  try {
    venues.value = await venueAPI.getVenues()
  } catch (error) {
    console.error('获取场馆列表失败:', error)
  }
}

const selectVenue = async (venue) => {
  selectedVenue.value = venue
  loadingSlots.value = true
  try {
    timeSlots.value = await venueAPI.getTimeSlots(venue.id, { days: 3 })
  } catch (error) {
    console.error('获取时段失败:', error)
  } finally {
    loadingSlots.value = false
  }
}

const bookSlot = async (slotId) => {
  bookingSlot.value = slotId
  try {
    await venueAPI.createBooking({ time_slot_id: slotId })
    alert('预约成功！')
    selectedVenue.value = null
  } catch (error) {
    alert(error.response?.data?.detail || '预约失败')
  } finally {
    bookingSlot.value = null
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

onMounted(() => {
  fetchVenues()
})
</script>
