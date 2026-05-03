<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <h1 class="text-lg font-bold">生活圈</h1>
    </header>

    <div class="bg-white p-4 mb-4">
      <div class="flex gap-2 overflow-x-auto">
        <button
          v-for="cat in categories"
          :key="cat.value"
          @click="selectedCategory = cat.value"
          :class="[
            'px-4 py-1 rounded-full text-sm whitespace-nowrap',
            selectedCategory === cat.value ? 'bg-lzu-blue text-white' : 'bg-gray-200 text-gray-700',
          ]"
        >
          {{ cat.label }}
        </button>
      </div>
    </div>

    <div class="container mx-auto px-4 space-y-4">
      <div v-for="post in posts" :key="post.id" class="bg-white rounded-lg p-4 shadow-md">
        <div class="flex items-start mb-3">
          <div class="w-10 h-10 bg-gray-300 rounded-full mr-3 flex items-center justify-center flex-shrink-0">
            👤
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-semibold">{{ post.author?.username || '用户' + post.author_id }}</div>
            <div class="text-xs text-gray-500">{{ formatTime(post.created_at) }}</div>
          </div>
          <span class="text-xs bg-lzu-light text-lzu-blue px-2 py-1 rounded whitespace-nowrap">
            {{ getCategoryLabel(post.category) }}
          </span>
        </div>

        <h3 v-if="post.title" class="font-semibold mb-2">{{ post.title }}</h3>
        <p class="text-gray-700 text-sm mb-3 whitespace-pre-wrap">{{ post.content }}</p>

        <div v-if="post.images && post.images.length > 0" class="mb-3">
          <div
            :class="[
              'grid gap-2',
              post.images.length === 1 ? 'grid-cols-1' : post.images.length === 2 ? 'grid-cols-2' : 'grid-cols-3',
            ]"
          >
            <img
              v-for="(img, idx) in post.images.slice(0, 9)"
              :key="idx"
              :src="img"
              :alt="`图片${idx + 1}`"
              class="w-full aspect-square object-cover rounded cursor-pointer"
              @click="previewImage(post.images, idx)"
            />
          </div>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500 border-t pt-3">
          <button
            @click="toggleLike(post)"
            :class="['flex items-center gap-1', post.is_liked ? 'text-red-500' : '']"
          >
            <span>{{ post.is_liked ? '❤️' : '🤍' }}</span>
            <span>{{ post.like_count || 0 }}</span>
          </button>
          <button @click="toggleComments(post.id)" class="flex items-center gap-1">
            <span>💬</span>
            <span>{{ post.comment_count || 0 }}</span>
          </button>
          <span class="flex items-center gap-1">
            <span>👁</span>
            <span>{{ post.views || 0 }}</span>
          </span>
        </div>

        <div v-if="expandedComments[post.id]" class="mt-3 border-t pt-3">
          <div v-if="loadingComments[post.id]" class="text-center text-gray-400 py-2">加载中...</div>
          <div v-else-if="postComments[post.id]?.length > 0" class="space-y-2 mb-3">
            <div v-for="comment in postComments[post.id]" :key="comment.id" class="flex items-start text-sm">
              <div class="w-6 h-6 bg-gray-300 rounded-full mr-2 flex items-center justify-center text-xs flex-shrink-0">
                👤
              </div>
              <div class="flex-1 min-w-0">
                <span class="font-semibold">{{ comment.user?.username || '用户' + comment.user_id }}</span>
                <span class="text-gray-600">: {{ comment.content }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center text-gray-400 py-2 text-sm">暂无评论</div>

          <div v-if="isAuthenticated" class="flex gap-2">
            <input
              v-model="commentInputs[post.id]"
              @keyup.enter="submitComment(post.id)"
              type="text"
              placeholder="说点什么..."
              class="flex-1 px-3 py-1 border border-gray-300 rounded text-sm"
            />
            <button
              @click="submitComment(post.id)"
              :disabled="!commentInputs[post.id]?.trim()"
              class="bg-lzu-blue text-white px-4 py-1 rounded text-sm disabled:opacity-50"
            >
              发送
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
      <div v-if="!loading && posts.length === 0" class="text-center py-8 text-gray-500">暂无动态</div>
    </div>

    <button
      @click="showPublishDialog = true"
      class="fixed bottom-24 right-6 w-14 h-14 bg-lzu-blue text-white rounded-full shadow-lg flex items-center justify-center text-2xl"
    >
      +
    </button>

    <div
      v-if="showPublishDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showPublishDialog = false"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">发布动态</h2>
        <div class="space-y-3">
          <input
            v-model="postForm.title"
            type="text"
            placeholder="标题（可选）"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <textarea
            v-model="postForm.content"
            placeholder="分享你的想法..."
            rows="5"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          ></textarea>
          <select v-model="postForm.category" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">选择分类</option>
            <option value="lost_found">失物招领</option>
            <option value="complaint">吐槽</option>
            <option value="activity">活动</option>
            <option value="sharing">分享</option>
            <option value="other">其他</option>
          </select>
          <div>
            <input
              ref="postFileInput"
              type="file"
              accept="image/*"
              multiple
              @change="handlePostImageSelect"
              class="hidden"
            />
            <button
              @click="$refs.postFileInput.click()"
              class="w-full border border-dashed border-gray-400 py-3 rounded-lg text-gray-600"
            >
              上传图片 ({{ postForm.images.length }}/9)
            </button>
            <div v-if="postForm.images.length > 0" class="grid grid-cols-3 gap-2 mt-2">
              <div
                v-for="(img, idx) in postForm.images"
                :key="idx"
                class="relative aspect-square bg-gray-100 rounded overflow-hidden"
              >
                <img :src="img" class="w-full h-full object-cover" />
                <button
                  @click="postForm.images.splice(idx, 1)"
                  class="absolute top-1 right-1 bg-red-500 text-white w-6 h-6 rounded-full text-xs"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showPublishDialog = false" class="flex-1 border border-gray-300 py-2 rounded-lg">
            取消
          </button>
          <button
            @click="handlePublishPost"
            :disabled="publishing"
            class="flex-1 bg-lzu-blue text-white py-2 rounded-lg disabled:opacity-50"
          >
            {{ publishing ? '发布中...' : '发布' }}
          </button>
        </div>
      </div>
    </div>

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
        <router-link to="/community" class="flex flex-col items-center text-lzu-blue">
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { communityAPI, uploadAPI } from '@/api'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const posts = ref([])
const loading = ref(false)
const selectedCategory = ref('')
const showPublishDialog = ref(false)
const publishing = ref(false)
const postFileInput = ref(null)

const expandedComments = reactive({})
const loadingComments = reactive({})
const postComments = reactive({})
const commentInputs = reactive({})

const postForm = ref({
  title: '',
  content: '',
  category: '',
  images: [],
})

const isAuthenticated = computed(() => authStore.isAuthenticated)

const categories = [
  { label: '全部', value: '' },
  { label: '失物招领', value: 'lost_found' },
  { label: '吐槽', value: 'complaint' },
  { label: '活动', value: 'activity' },
  { label: '分享', value: 'sharing' },
  { label: '其他', value: 'other' },
]

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = { category: selectedCategory.value || undefined }
    posts.value = await communityAPI.getPosts(params)
  } catch (error) {
    console.error('获取动态失败:', error)
  } finally {
    loading.value = false
  }
}

const toggleLike = async (post) => {
  if (!isAuthenticated.value) {
    alert('请先登录')
    return
  }
  try {
    const result = await communityAPI.toggleLike(post.id)
    post.is_liked = result.is_liked
    post.like_count = result.like_count
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

const toggleComments = async (postId) => {
  if (!expandedComments[postId]) {
    expandedComments[postId] = true
    if (!postComments[postId]) {
      loadingComments[postId] = true
      try {
        postComments[postId] = await communityAPI.getComments(postId)
      } catch (error) {
        console.error('获取评论失败:', error)
      } finally {
        loadingComments[postId] = false
      }
    }
  } else {
    expandedComments[postId] = false
  }
}

const submitComment = async (postId) => {
  if (!commentInputs[postId]?.trim()) return
  try {
    const newComment = await communityAPI.addComment(postId, { content: commentInputs[postId] })
    if (!postComments[postId]) postComments[postId] = []
    postComments[postId].push(newComment)
    commentInputs[postId] = ''
    const post = posts.value.find((p) => p.id === postId)
    if (post) post.comment_count = (post.comment_count || 0) + 1
  } catch (error) {
    alert(error.message || '评论失败')
  }
}

const handlePostImageSelect = async (event) => {
  const files = Array.from(event.target.files)
  if (postForm.value.images.length + files.length > 9) {
    alert('最多上传9张图片')
    return
  }
  try {
    const { urls } = await uploadAPI.uploadFiles(files)
    postForm.value.images.push(...urls)
  } catch (error) {
    alert('图片上传失败')
  }
}

const handlePublishPost = async () => {
  if (!postForm.value.content || !postForm.value.category) {
    alert('请填写内容和分类')
    return
  }
  publishing.value = true
  try {
    await communityAPI.createPost(postForm.value)
    alert('发布成功')
    showPublishDialog.value = false
    postForm.value = { title: '', content: '', category: '', images: [] }
    fetchPosts()
  } catch (error) {
    alert(error.message || '发布失败')
  } finally {
    publishing.value = false
  }
}

const previewImage = (images, index) => {
  console.log('预览图片:', images[index])
}

const getCategoryLabel = (value) => {
  return categories.find((c) => c.value === value)?.label || '其他'
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

watch(selectedCategory, () => {
  fetchPosts()
})

onMounted(() => {
  fetchPosts()
})
</script>
