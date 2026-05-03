<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">商品详情</h1>
      </div>
    </header>

    <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

    <div v-else-if="product" class="container mx-auto pb-4">
      <div class="bg-white mb-4">
        <div v-if="product.images && product.images.length > 0" class="relative">
          <div class="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
            <img
              :src="product.images[currentImageIndex]"
              :alt="product.title"
              class="w-full h-full object-contain"
            />
          </div>
          <div
            v-if="product.images.length > 1"
            class="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded"
          >
            {{ currentImageIndex + 1 }}/{{ product.images.length }}
          </div>
          <div v-if="product.images.length > 1" class="flex justify-center gap-2 p-2 overflow-x-auto">
            <img
              v-for="(img, idx) in product.images"
              :key="idx"
              :src="img"
              @click="currentImageIndex = idx"
              :class="[
                'w-16 h-16 object-cover rounded cursor-pointer border-2',
                currentImageIndex === idx ? 'border-lzu-blue' : 'border-transparent',
              ]"
            />
          </div>
        </div>
        <div v-else class="aspect-square bg-gray-200 flex items-center justify-center">
          <span class="text-8xl">📦</span>
        </div>
      </div>

      <div class="bg-white p-4 mb-4">
        <h1 class="text-xl font-bold mb-2">{{ product.title }}</h1>
        <div class="text-3xl text-red-500 font-bold mb-3">¥{{ product.price }}</div>
        <div class="flex gap-3 text-sm text-gray-500 mb-3">
          <span>浏览 {{ product.views || 0 }}</span>
          <span>|</span>
          <span>{{ formatTime(product.created_at) }}</span>
        </div>
        <div class="text-gray-700 whitespace-pre-wrap">{{ product.description }}</div>
      </div>

      <div class="bg-white p-4 mb-4">
        <h3 class="font-semibold mb-3">卖家信息</h3>
        <div class="flex items-center">
          <div class="w-12 h-12 bg-gray-300 rounded-full mr-3 flex items-center justify-center text-xl">
            👤
          </div>
          <div>
            <div class="font-semibold">{{ product.seller?.username || '用户' + product.seller_id }}</div>
            <div class="text-sm text-gray-500">{{ product.seller?.student_id || '' }}</div>
          </div>
        </div>
      </div>

      <div class="bg-white p-4 mb-4">
        <h3 class="font-semibold mb-3">留言板 ({{ comments.length }})</h3>

        <div v-if="comments.length === 0" class="text-center text-gray-400 py-4">暂无留言</div>

        <div v-else class="space-y-3 mb-4">
          <div v-for="comment in comments" :key="comment.id" class="flex items-start pb-3 border-b last:border-b-0">
            <div class="w-10 h-10 bg-gray-300 rounded-full mr-3 flex items-center justify-center flex-shrink-0">
              👤
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-semibold">{{ comment.user?.username || '用户' + comment.user_id }}</span>
                <span class="text-xs text-gray-400">{{ formatTime(comment.created_at) }}</span>
              </div>
              <div class="text-sm text-gray-700 break-words">{{ comment.content }}</div>
            </div>
          </div>
        </div>

        <div v-if="isAuthenticated" class="flex gap-2">
          <input
            v-model="commentText"
            @keyup.enter="submitComment"
            type="text"
            placeholder="说点什么..."
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
          />
          <button
            @click="submitComment"
            :disabled="!commentText.trim() || submitting"
            class="bg-lzu-blue text-white px-6 py-2 rounded-lg hover:bg-blue-800 disabled:opacity-50"
          >
            发送
          </button>
        </div>
        <div v-else class="text-center text-gray-500 py-2">
          <router-link to="/login" class="text-lzu-blue">登录后可留言</router-link>
        </div>
      </div>
    </div>

    <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
      <div class="container mx-auto flex gap-3">
        <button
          v-if="product?.seller?.phone"
          @click="contactSeller"
          class="flex-1 border border-lzu-blue text-lzu-blue py-3 rounded-lg font-medium"
        >
          联系卖家
        </button>
        <button class="flex-1 bg-lzu-blue text-white py-3 rounded-lg font-medium">我想要</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { productAPI } from '@/api'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const authStore = useAuthStore()
const product = ref(null)
const comments = ref([])
const loading = ref(true)
const commentText = ref('')
const submitting = ref(false)
const currentImageIndex = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const fetchProduct = async () => {
  try {
    product.value = await productAPI.getProductById(route.params.id)
    comments.value = await productAPI.getComments(route.params.id)
  } catch (error) {
    console.error('获取商品详情失败:', error)
  } finally {
    loading.value = false
  }
}

const submitComment = async () => {
  if (!commentText.value.trim()) return

  submitting.value = true
  try {
    const newComment = await productAPI.addComment(route.params.id, { content: commentText.value })
    comments.value.push(newComment)
    commentText.value = ''
  } catch (error) {
    alert(error.message || '发送失败')
  } finally {
    submitting.value = false
  }
}

const contactSeller = () => {
  if (product.value?.seller?.phone) {
    alert(`卖家联系方式：${product.value.seller.phone}`)
  }
}

const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

onMounted(() => {
  fetchProduct()
})
</script>
