<!--
  文件：MyPosts.vue - 我的动态页面
  作用：显示当前用户发布的所有动态，支持删除动态
  功能：
    1. 显示当前用户发布的动态列表
    2. 显示动态的分类标签、标题、内容、图片和互动数据
    3. 删除动态（带确认提示）
    4. 空状态提示（无动态时引导用户去发布）
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的动态</h1>
      </div>
    </header>

    <!-- 动态列表 -->
    <div class="container mx-auto px-4 py-4 space-y-4">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <!-- 空状态 -->
      <div v-else-if="posts.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-4">💬</div>
        <p>还没有发布动态</p>
        <button @click="$router.push('/community')" class="mt-4 text-lzu-blue">去发布</button>
      </div>

      <!-- 动态列表 -->
      <!--
        v-for="post in posts": 循环渲染每条动态
        每条动态显示分类标签、时间、标题、内容、图片和互动数据
      -->
      <div v-for="post in posts" :key="post.id" class="bg-white rounded-lg p-4 shadow-md">
        <!-- 顶部：分类标签和操作按钮 -->
        <div class="flex justify-between items-start mb-2">
          <!-- 分类标签（蓝色小标签） -->
          <span class="text-xs bg-lzu-light text-lzu-blue px-2 py-1 rounded">
            {{ getCategoryLabel(post.category) }}
          </span>
          <div class="flex items-center gap-2">
            <!-- 发布时间 -->
            <span class="text-xs text-gray-400">{{ formatTime(post.created_at) }}</span>
            <!--
              删除按钮
              text-red-400: 默认红色，hover 时加深为 text-red-600
            -->
            <button @click="handleDelete(post.id)" class="text-xs text-red-400 hover:text-red-600">
              删除
            </button>
          </div>
        </div>

        <!-- 动态标题（可选） -->
        <h3 v-if="post.title" class="font-semibold mb-1">{{ post.title }}</h3>
        <!-- 动态内容：最多显示 3 行，超出部分省略 -->
        <!--
          line-clamp-3: Tailwind CSS 的多行文本截断
          需要 @tailwindcss/line-clamp 插件支持
          为什么限制 3 行：列表页面不需要显示完整内容，保持界面整洁
        -->
        <p class="text-gray-700 text-sm mb-2 line-clamp-3">{{ post.content }}</p>

        <!-- 图片预览：最多显示 3 张 -->
        <div v-if="post.images && post.images.length > 0" class="grid grid-cols-3 gap-1 mb-2">
          <img
            v-for="(img, idx) in post.images.slice(0, 3)"
            :key="idx"
            :src="img"
            class="w-full aspect-square object-cover rounded"
          />
        </div>

        <!-- 互动数据：点赞数、评论数、浏览数 -->
        <div class="flex gap-4 text-xs text-gray-500">
          <span>❤️ {{ post.like_count || 0 }}</span>
          <span>💬 {{ post.comment_count || 0 }}</span>
          <span>👁 {{ post.views || 0 }}</span>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { communityAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

// 动态列表
const posts = ref([])
// 加载状态
const loading = ref(true)

// 分类映射表：将后端的分类值转换为中文显示
const categories = [
  { label: '失物招领', value: 'lost_found' },
  { label: '吐槽', value: 'complaint' },
  { label: '活动', value: 'activity' },
  { label: '分享', value: 'sharing' },
  { label: '问答互助', value: 'qa' },
  { label: '其他', value: 'other' },
]

// 获取当前用户发布的动态
const fetchMyPosts = async () => {
  try {
    posts.value = await communityAPI.getMyPosts()
  } catch (error) {
    console.error('获取我的动态失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除动态
const handleDelete = async (id) => {
  if (!confirm('确定删除该动态？')) return
  try {
    await communityAPI.deletePost(id)
    // 从列表中移除已删除的动态
    posts.value = posts.value.filter((p) => p.id !== id)
  } catch (error) {
    alert(error.message || '删除失败')
  }
}

// 根据分类值获取中文标签
const getCategoryLabel = (value) => {
  // find 方法在数组中查找第一个满足条件的元素
  // 如果找到返回该元素，否则返回 undefined
  // ?.label 使用可选链防止 undefined 报错
  return categories.find((c) => c.value === value)?.label || '其他'
}

// 时间格式化
const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 页面挂载后获取动态列表
onMounted(() => {
  fetchMyPosts()
})
</script>
