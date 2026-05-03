<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的动态</h1>
      </div>
    </header>

    <div class="container mx-auto px-4 py-4 space-y-4">
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <div v-else-if="posts.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-4">💬</div>
        <p>还没有发布动态</p>
        <button @click="$router.push('/community')" class="mt-4 text-lzu-blue">去发布</button>
      </div>

      <div v-for="post in posts" :key="post.id" class="bg-white rounded-lg p-4 shadow-md">
        <div class="flex justify-between items-start mb-2">
          <span class="text-xs bg-lzu-light text-lzu-blue px-2 py-1 rounded">
            {{ getCategoryLabel(post.category) }}
          </span>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-400">{{ formatTime(post.created_at) }}</span>
            <button @click="handleDelete(post.id)" class="text-xs text-red-400 hover:text-red-600">
              删除
            </button>
          </div>
        </div>
        <h3 v-if="post.title" class="font-semibold mb-1">{{ post.title }}</h3>
        <p class="text-gray-700 text-sm mb-2 line-clamp-3">{{ post.content }}</p>
        <div v-if="post.images && post.images.length > 0" class="grid grid-cols-3 gap-1 mb-2">
          <img
            v-for="(img, idx) in post.images.slice(0, 3)"
            :key="idx"
            :src="img"
            class="w-full aspect-square object-cover rounded"
          />
        </div>
        <div class="flex gap-4 text-xs text-gray-500">
          <span>❤️ {{ post.like_count || 0 }}</span>
          <span>💬 {{ post.comment_count || 0 }}</span>
          <span>👁 {{ post.views || 0 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { communityAPI } from '@/api'

const posts = ref([])
const loading = ref(true)

const categories = [
  { label: '失物招领', value: 'lost_found' },
  { label: '吐槽', value: 'complaint' },
  { label: '活动', value: 'activity' },
  { label: '分享', value: 'sharing' },
  { label: '其他', value: 'other' },
]

const fetchMyPosts = async () => {
  try {
    posts.value = await communityAPI.getMyPosts()
  } catch (error) {
    console.error('获取我的动态失败:', error)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定删除该动态？')) return
  try {
    await communityAPI.deletePost(id)
    posts.value = posts.value.filter((p) => p.id !== id)
  } catch (error) {
    alert(error.message || '删除失败')
  }
}

const getCategoryLabel = (value) => {
  return categories.find((c) => c.value === value)?.label || '其他'
}

const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

onMounted(() => {
  fetchMyPosts()
})
</script>
