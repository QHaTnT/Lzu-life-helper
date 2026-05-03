<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的活动</h1>
      </div>
      <div class="flex gap-4 mt-3">
        <button
          @click="activeTab = 'registered'"
          :class="['text-sm pb-1', activeTab === 'registered' ? 'text-lzu-blue border-b-2 border-lzu-blue' : 'text-gray-500']"
        >
          我报名的
        </button>
        <button
          @click="activeTab = 'published'"
          :class="['text-sm pb-1', activeTab === 'published' ? 'text-lzu-blue border-b-2 border-lzu-blue' : 'text-gray-500']"
        >
          我发布的
        </button>
      </div>
    </header>

    <div class="container mx-auto px-4 py-4 space-y-4">
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <template v-else-if="activeTab === 'registered'">
        <div v-if="registeredActivities.length === 0" class="text-center py-16 text-gray-400">
          <div class="text-5xl mb-4">🎉</div>
          <p>还没有报名活动</p>
        </div>
        <div
          v-for="activity in registeredActivities"
          :key="activity.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold flex-1">{{ activity.title }}</h3>
            <button
              @click="handleCancelRegistration(activity.id)"
              class="text-xs text-red-400 hover:text-red-600 ml-2"
            >
              取消报名
            </button>
          </div>
          <div class="text-sm text-gray-600 space-y-1">
            <div v-if="activity.location">📍 {{ activity.location }}</div>
            <div>🕐 {{ formatDateTime(activity.start_time) }}</div>
            <div v-if="activity.max_participants">
              👥 {{ activity.current_participants }}/{{ activity.max_participants }} 人
            </div>
          </div>
        </div>
      </template>

      <template v-else>
        <div v-if="publishedActivities.length === 0" class="text-center py-16 text-gray-400">
          <div class="text-5xl mb-4">📋</div>
          <p>还没有发布活动</p>
        </div>
        <div
          v-for="activity in publishedActivities"
          :key="activity.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <h3 class="font-semibold mb-2">{{ activity.title }}</h3>
          <div class="text-sm text-gray-600 space-y-1 mb-3">
            <div v-if="activity.location">📍 {{ activity.location }}</div>
            <div>🕐 {{ formatDateTime(activity.start_time) }}</div>
            <div v-if="activity.max_participants">
              <div class="flex items-center gap-2">
                <span>👥 {{ activity.current_participants }}/{{ activity.max_participants }}</span>
                <div class="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-lzu-blue h-2 rounded-full"
                    :style="{ width: `${Math.min(100, (activity.current_participants / activity.max_participants) * 100)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="activity.registrations && activity.registrations.length > 0">
            <div class="text-sm font-medium text-gray-700 mb-2">报名名单：</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="reg in activity.registrations"
                :key="reg.id"
                class="text-xs bg-gray-100 px-2 py-1 rounded"
              >
                {{ reg.user?.username || '用户' + reg.user_id }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { communityAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const activeTab = ref('registered')
const registeredActivities = ref([])
const publishedActivities = ref([])
const loading = ref(true)

const fetchData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'registered') {
      registeredActivities.value = await communityAPI.getMyRegisteredActivities()
    } else {
      publishedActivities.value = await communityAPI.getMyPublishedActivities()
    }
  } catch (error) {
    console.error('获取活动失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCancelRegistration = async (id) => {
  if (!confirm('确定取消报名？')) return
  try {
    await communityAPI.cancelRegistration(id)
    registeredActivities.value = registeredActivities.value.filter((a) => a.id !== id)
  } catch (error) {
    alert(error.message || '取消失败')
  }
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

watch(activeTab, () => {
  fetchData()
})

onMounted(() => {
  fetchData()
})
</script>
