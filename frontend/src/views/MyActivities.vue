<!--
  文件：MyActivities.vue - 我的活动页面
  作用：显示当前用户报名的活动和发布的活动，支持取消报名
  功能：
    1. 两个标签页切换：我报名的活动 / 我发布的活动
    2. 报名的活动显示取消报名按钮
    3. 发布的活动显示报名名单和报名进度
    4. 空状态提示
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的活动</h1>
      </div>
      <!-- 标签页切换按钮 -->
      <!--
        两个按钮分别对应"我报名的"和"我发布的"
        选中时显示蓝色底部边框和蓝色文字
        未选中时显示灰色文字
      -->
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
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <!--
        template 标签：不会渲染成实际的 DOM 元素
        为什么用 template：v-else-if 不能直接放在多个并列的 div 上
        用 template 包裹可以实现条件渲染而不额外添加 DOM 节点
      -->
      <template v-else-if="activeTab === 'registered'">
        <!-- 我报名的活动列表 -->
        <!-- 空状态 -->
        <div v-if="registeredActivities.length === 0" class="text-center py-16 text-gray-400">
          <div class="text-5xl mb-4">🎉</div>
          <p>还没有报名活动</p>
        </div>
        <!-- 活动列表 -->
        <div
          v-for="activity in registeredActivities"
          :key="activity.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold flex-1">{{ activity.title }}</h3>
            <!-- 取消报名按钮 -->
            <button
              @click="handleCancelRegistration(activity.id)"
              class="text-xs text-red-400 hover:text-red-600 ml-2"
            >
              取消报名
            </button>
          </div>
          <div class="text-sm text-gray-600 space-y-1">
            <!-- 活动地点（可选） -->
            <div v-if="activity.location">📍 {{ activity.location }}</div>
            <!-- 活动开始时间 -->
            <div>🕐 {{ formatDateTime(activity.start_time) }}</div>
            <!-- 参与人数限制（可选） -->
            <div v-if="activity.max_participants">
              👥 {{ activity.current_participants }}/{{ activity.max_participants }} 人
            </div>
          </div>
        </div>
      </template>

      <!-- 我发布的活动列表 -->
      <template v-else>
        <!-- 空状态 -->
        <div v-if="publishedActivities.length === 0" class="text-center py-16 text-gray-400">
          <div class="text-5xl mb-4">📋</div>
          <p>还没有发布活动</p>
        </div>
        <!-- 活动列表 -->
        <div
          v-for="activity in publishedActivities"
          :key="activity.id"
          class="bg-white rounded-lg p-4 shadow-md"
        >
          <h3 class="font-semibold mb-2">{{ activity.title }}</h3>
          <div class="text-sm text-gray-600 space-y-1 mb-3">
            <div v-if="activity.location">📍 {{ activity.location }}</div>
            <div>🕐 {{ formatDateTime(activity.start_time) }}</div>
            <!-- 参与人数进度条 -->
            <div v-if="activity.max_participants">
              <div class="flex items-center gap-2">
                <span>👥 {{ activity.current_participants }}/{{ activity.max_participants }}</span>
                <!--
                  进度条
                  外层灰色背景条，内层蓝色填充条
                  width 通过计算百分比动态设置
                  Math.min(100, ...): 确保宽度不超过 100%
                  为什么需要 min：如果报名人数超过限制，进度条不能超出容器
                -->
                <div class="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-lzu-blue h-2 rounded-full"
                    :style="{ width: `${Math.min(100, (activity.current_participants / activity.max_participants) * 100)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <!-- 报名名单（只有发布的活动才能看到） -->
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

// 当前激活的标签页：'registered'（我报名的）或 'published'（我发布的）
const activeTab = ref('registered')
// 我报名的活动列表
const registeredActivities = ref([])
// 我发布的活动列表
const publishedActivities = ref([])
// 加载状态
const loading = ref(true)

// 获取活动数据
// 根据当前标签页加载对应的数据
const fetchData = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'registered') {
      // 获取我报名参加的活动
      registeredActivities.value = await communityAPI.getMyRegisteredActivities()
    } else {
      // 获取我发布的活动
      publishedActivities.value = await communityAPI.getMyPublishedActivities()
    }
  } catch (error) {
    console.error('获取活动失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消报名
const handleCancelRegistration = async (id) => {
  if (!confirm('确定取消报名？')) return
  try {
    await communityAPI.cancelRegistration(id)
    // 从列表中移除已取消的活动
    registeredActivities.value = registeredActivities.value.filter((a) => a.id !== id)
  } catch (error) {
    alert(error.message || '取消失败')
  }
}

// 日期时间格式化：将 ISO 时间转换为 "X月X日 HH:MM" 格式
const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  // padStart(2, '0'): 将数字补零到 2 位
  // 例如：9 → "09"，15 → "15"
  // 为什么需要补零：保持时间格式统一，如 "8:5" 应该显示为 "8:05"
  return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 监听标签页切换，自动加载对应数据
watch(activeTab, () => {
  fetchData()
})

// 页面挂载后获取数据
onMounted(() => {
  fetchData()
})
</script>
