<!--
  文件：Community.vue - 生活圈页面（社区动态）
  作用：显示社区动态列表，用户可以发布动态、评论、点赞，也可以发布活动
  功能：
    1. 分类筛选：按类型筛选动态（失物招领、吐槽、分享等）
    2. 动态列表：显示用户发布的动态，包含文字、图片、点赞和评论
    3. 发布动态：点击"+"按钮发布新的动态
    4. 发布活动：可以发布校园活动
    5. 评论功能：可以对动态发表评论
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部标题栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <h1 class="text-lg font-bold">生活圈</h1>
    </header>

    <!-- 分类标签栏 -->
    <div class="bg-white p-4 mb-4">
      <div class="flex gap-2 overflow-x-auto">
        <!--
          分类标签：点击切换选中的分类
          选中时蓝色背景，未选中时灰色背景
        -->
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

    <!-- 动态列表 -->
    <div class="container mx-auto px-4 space-y-4">
      <!--
        v-for="post in posts": 循环渲染每条动态
        每条动态包含：用户头像、用户名、发布时间、分类标签、内容、图片、互动数据
      -->
      <div v-for="post in posts" :key="post.id" class="bg-white rounded-lg p-4 shadow-md">
        <!-- 用户信息区域 -->
        <div class="flex items-start mb-3">
          <!-- 用户头像（默认显示👤图标） -->
          <div class="w-10 h-10 bg-gray-300 rounded-full mr-3 flex items-center justify-center flex-shrink-0">
            👤
          </div>
          <div class="flex-1 min-w-0">
            <!-- 用户名：如果作者信息不存在则显示"用户+ID" -->
            <div class="font-semibold">{{ post.author?.username || '用户' + post.author_id }}</div>
            <!-- 发布时间 -->
            <div class="text-xs text-gray-500">{{ formatTime(post.created_at) }}</div>
          </div>
          <!-- 分类标签 -->
          <span class="text-xs bg-lzu-light text-lzu-blue px-2 py-1 rounded whitespace-nowrap">
            {{ getCategoryLabel(post.category) }}
          </span>
        </div>

        <!-- 动态标题（可选） -->
        <h3 v-if="post.title" class="font-semibold mb-2">{{ post.title }}</h3>
        <!-- 动态内容 -->
        <!--
          whitespace-pre-wrap: 保留内容中的换行符和空格
          为什么需要：用户发布时可能输入了换行，需要原样显示
        -->
        <p class="text-gray-700 text-sm mb-3 whitespace-pre-wrap">{{ post.content }}</p>

        <!-- 图片区域 -->
        <div v-if="post.images && post.images.length > 0" class="mb-3">
          <!--
            动态网格布局：根据图片数量自动调整列数
            1 张图片：单列
            2 张图片：两列
            3 张及以上：三列
            为什么动态调整：不同数量的图片有不同的最佳展示方式
          -->
          <div
            :class="[
              'grid gap-2',
              post.images.length === 1 ? 'grid-cols-1' : post.images.length === 2 ? 'grid-cols-2' : 'grid-cols-3',
            ]"
          >
            <!--
              v-for="(img, idx) in post.images.slice(0, 9)": 最多显示 9 张图片
              slice(0, 9) 截取数组前 9 个元素
              为什么限制 9 张：保持界面整洁，太多图片会影响加载速度
              @click="previewImage(post.images, idx)": 点击图片可以预览
            -->
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

        <!-- 互动按钮区域（点赞、评论、浏览） -->
        <div class="flex items-center gap-4 text-sm text-gray-500 border-t pt-3">
          <!-- 点赞按钮 -->
          <button
            @click="toggleLike(post)"
            :class="['flex items-center gap-1', post.is_liked ? 'text-red-500' : '']"
          >
            <!--
              根据 is_liked 状态切换图标：
              已点赞：❤️（红色心形）
              未点赞：🤍（白色心形）
            -->
            <span>{{ post.is_liked ? '❤️' : '🤍' }}</span>
            <span>{{ post.like_count || 0 }}</span>
          </button>
          <!-- 评论按钮 -->
          <button @click="toggleComments(post.id)" class="flex items-center gap-1">
            <span>💬</span>
            <span>{{ post.comment_count || 0 }}</span>
          </button>
          <!-- 浏览次数（只显示，不可点击） -->
          <span class="flex items-center gap-1">
            <span>👁</span>
            <span>{{ post.views || 0 }}</span>
          </span>
        </div>

        <!--
          评论展开区域
          v-if="expandedComments[post.id]": 只有点击了评论按钮才展开
          expandedComments 是一个对象，以 post.id 为键，值为 true/false
          为什么用对象而不是数组：需要根据每个帖子的 ID 单独控制展开状态
        -->
        <div v-if="expandedComments[post.id]" class="mt-3 border-t pt-3">
          <!-- 评论加载中 -->
          <div v-if="loadingComments[post.id]" class="text-center text-gray-400 py-2">加载中...</div>
          <!-- 评论列表 -->
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

          <!-- 评论输入框（已登录才能看到） -->
          <div v-if="isAuthenticated" class="flex gap-2">
            <!--
              评论输入框使用 commentInputs[post.id] 绑定
              为什么用 reactive 对象：每条评论框需要独立的值
              如果用单个 ref，所有评论框会共享同一个值
            -->
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

      <!-- 加载状态和空状态 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
      <div v-if="!loading && posts.length === 0" class="text-center py-8 text-gray-500">暂无动态</div>
    </div>

    <!--
      发布按钮（浮动在右下角）
      点击后弹出发布类型选择弹窗
    -->
    <button
      @click="showPublishDialog = true"
      class="fixed bottom-24 right-6 w-14 h-14 bg-lzu-blue text-white rounded-full shadow-lg flex items-center justify-center text-2xl"
    >
      +
    </button>

    <!--
      发布类型选择弹窗
      v-if="showPublishDialog && !publishType": 只有弹窗打开且未选择类型时显示
      用户需要先选择发布"动态"还是"活动"
    -->
    <div
      v-if="showPublishDialog && !publishType"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50"
      @click.self="showPublishDialog = false"
    >
      <div class="bg-white w-full rounded-t-2xl p-6">
        <h2 class="text-lg font-bold mb-4 text-center">选择发布类型</h2>
        <div class="grid grid-cols-2 gap-4">
          <!-- 选择发布动态 -->
          <button
            @click="publishType = 'post'"
            class="border-2 border-lzu-blue rounded-xl p-4 flex flex-col items-center gap-2"
          >
            <span class="text-3xl">💬</span>
            <span class="font-semibold text-lzu-blue">发布动态</span>
            <span class="text-xs text-gray-500">失物招领、吐槽、分享等</span>
          </button>
          <!-- 选择发布活动 -->
          <button
            @click="publishType = 'activity'"
            class="border-2 border-lzu-blue rounded-xl p-4 flex flex-col items-center gap-2"
          >
            <span class="text-3xl">🎉</span>
            <span class="font-semibold text-lzu-blue">发布活动</span>
            <span class="text-xs text-gray-500">校园活动、社团招募等</span>
          </button>
        </div>
        <button @click="showPublishDialog = false" class="w-full mt-4 py-2 text-gray-500">取消</button>
      </div>
    </div>

    <!--
      发布动态弹窗
      v-if="showPublishDialog && publishType === 'post'": 选择发布动态后显示
    -->
    <div
      v-if="showPublishDialog && publishType === 'post'"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closePublishDialog"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">发布动态</h2>
        <div class="space-y-3">
          <!-- 标题（可选） -->
          <input
            v-model="postForm.title"
            type="text"
            placeholder="标题（可选）"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 内容（必填） -->
          <textarea
            v-model="postForm.content"
            placeholder="分享你的想法..."
            rows="5"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          ></textarea>
          <!-- 分类选择（必填） -->
          <select v-model="postForm.category" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">选择分类</option>
            <option value="lost_found">失物招领</option>
            <option value="complaint">吐槽</option>
            <option value="activity">活动</option>
            <option value="sharing">分享</option>
            <option value="qa">问答互助</option>
            <option value="other">其他</option>
          </select>
          <!-- 图片上传 -->
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
            <!-- 已上传图片预览 -->
            <div v-if="postForm.images.length > 0" class="grid grid-cols-3 gap-2 mt-2">
              <div
                v-for="(img, idx) in postForm.images"
                :key="idx"
                class="relative aspect-square bg-gray-100 rounded overflow-hidden"
              >
                <img :src="img" class="w-full h-full object-cover" />
                <!-- 删除按钮 -->
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
          <button @click="closePublishDialog" class="flex-1 border border-gray-300 py-2 rounded-lg">
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

    <!--
      发布活动弹窗
      v-if="showPublishDialog && publishType === 'activity'": 选择发布活动后显示
    -->
    <div
      v-if="showPublishDialog && publishType === 'activity'"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closePublishDialog"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">发布活动</h2>
        <div class="space-y-3">
          <!-- 活动标题（必填） -->
          <input
            v-model="activityForm.title"
            type="text"
            placeholder="活动标题 *"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 活动描述 -->
          <textarea
            v-model="activityForm.description"
            placeholder="活动描述"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          ></textarea>
          <!-- 主办方/社团 -->
          <input
            v-model="activityForm.organizer"
            type="text"
            placeholder="主办方/社团（可选）"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 活动地点 -->
          <input
            v-model="activityForm.location"
            type="text"
            placeholder="活动地点"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 时间选择 -->
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">开始时间 *</label>
              <!--
                type="datetime-local": 日期时间选择器
                用户可以选择日期和具体时间
              -->
              <input
                v-model="activityForm.start_time"
                type="datetime-local"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">结束时间</label>
              <input
                v-model="activityForm.end_time"
                type="datetime-local"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
          </div>
          <!-- 最大参与人数 -->
          <input
            v-model.number="activityForm.max_participants"
            type="number"
            placeholder="最大参与人数（不填则不限）"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="closePublishDialog" class="flex-1 border border-gray-300 py-2 rounded-lg">
            取消
          </button>
          <button
            @click="handlePublishActivity"
            :disabled="publishingActivity"
            class="flex-1 bg-lzu-blue text-white py-2 rounded-lg disabled:opacity-50"
          >
            {{ publishingActivity ? '发布中...' : '发布活动' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { communityAPI, uploadAPI } from '@/api'
import { useAuthStore } from '@/store/auth'
import BottomNav from '@/components/BottomNav.vue'

const authStore = useAuthStore()

// ==========================================
// 响应式状态（ref）
// ==========================================

// 动态列表
const posts = ref([])
// 加载状态
const loading = ref(false)
// 当前选中的分类筛选
const selectedCategory = ref('')
// 是否显示发布弹窗
const showPublishDialog = ref(false)
// 发布类型：'post'（动态）或 'activity'（活动），null 表示未选择
const publishType = ref(null)
// 发布动态中状态
const publishing = ref(false)
// 发布活动中状态
const publishingActivity = ref(false)
// 图片文件输入框的引用
const postFileInput = ref(null)

// ==========================================
// 响应式状态（reactive）
// 为什么这里用 reactive 而不是 ref：
//   reactive 适合管理对象/数组，不需要 .value 访问属性
//   这些对象的键是帖子 ID，需要动态添加/访问属性
// ==========================================

// 评论展开状态：{ postId: true/false }
const expandedComments = reactive({})
// 评论加载状态：{ postId: true/false }
const loadingComments = reactive({})
// 评论数据：{ postId: [comment1, comment2, ...] }
const postComments = reactive({})
// 评论输入框的值：{ postId: '输入的内容' }
const commentInputs = reactive({})

// 发布动态的表单数据
const postForm = ref({
  title: '',
  content: '',
  category: '',
  images: [],
})

// 发布活动的表单数据
const activityForm = ref({
  title: '',
  description: '',
  organizer: '',
  location: '',
  start_time: '',
  end_time: '',
  max_participants: null,
})

// 用户是否已登录
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 分类选项列表
const categories = [
  { label: '全部', value: '' },
  { label: '失物招领', value: 'lost_found' },
  { label: '吐槽', value: 'complaint' },
  { label: '问答互助', value: 'qa' },
  { label: '分享', value: 'sharing' },
  { label: '活动', value: 'activity' },
  { label: '其他', value: 'other' },
]

// ==========================================
// 数据获取函数
// ==========================================

// 获取动态列表
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

// 点赞/取消点赞
const toggleLike = async (post) => {
  if (!isAuthenticated.value) {
    alert('请先登录')
    return
  }
  try {
    // toggleLike 返回新的点赞状态和点赞数
    const result = await communityAPI.toggleLike(post.id)
    // 直接修改原对象的属性，Vue 能检测到 reactive 对象的变化
    post.is_liked = result.is_liked
    post.like_count = result.like_count
  } catch (error) {
    console.error('点赞失败:', error)
  }
}

// 展开/收起评论区
const toggleComments = async (postId) => {
  // 如果当前是展开状态，则收起
  if (!expandedComments[postId]) {
    expandedComments[postId] = true
    // 如果还没加载过评论，则请求加载
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

// 提交评论
const submitComment = async (postId) => {
  if (!commentInputs[postId]?.trim()) return
  try {
    const newComment = await communityAPI.addComment(postId, { content: commentInputs[postId] })
    // 确保评论数组已初始化（防止第一次评论时报错）
    if (!postComments[postId]) postComments[postId] = []
    postComments[postId].push(newComment)
    // 清空输入框
    commentInputs[postId] = ''
    // 更新评论计数
    const post = posts.value.find((p) => p.id === postId)
    if (post) post.comment_count = (post.comment_count || 0) + 1
  } catch (error) {
    alert(error.message || '评论失败')
  }
}

// 处理动态图片选择
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

// 发布动态
const handlePublishPost = async () => {
  if (!postForm.value.content || !postForm.value.category) {
    alert('请填写内容和分类')
    return
  }
  publishing.value = true
  try {
    await communityAPI.createPost(postForm.value)
    alert('发布成功')
    closePublishDialog()
    // 重新获取列表，显示新发布的动态
    fetchPosts()
  } catch (error) {
    alert(error.message || '发布失败')
  } finally {
    publishing.value = false
  }
}

// 发布活动
const handlePublishActivity = async () => {
  if (!activityForm.value.title || !activityForm.value.start_time) {
    alert('请填写活动标题和开始时间')
    return
  }
  publishingActivity.value = true
  try {
    await communityAPI.createActivity(activityForm.value)
    alert('活动发布成功')
    closePublishDialog()
  } catch (error) {
    alert(error.message || '发布失败')
  } finally {
    publishingActivity.value = false
  }
}

// 关闭发布弹窗并重置表单
const closePublishDialog = () => {
  showPublishDialog.value = false
  publishType.value = null
  // 重置表单为初始值
  postForm.value = { title: '', content: '', category: '', images: [] }
  activityForm.value = { title: '', description: '', organizer: '', location: '', start_time: '', end_time: '', max_participants: null }
}

// 图片预览（当前仅打印到控制台，可扩展为全屏预览）
const previewImage = (images, index) => {
  console.log('预览图片:', images[index])
}

// 根据分类值获取中文标签
const getCategoryLabel = (value) => {
  return categories.find((c) => c.value === value)?.label || '其他'
}

// 时间格式化：将 ISO 时间转换为相对时间
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

// 监听分类变化，自动重新获取动态列表
watch(selectedCategory, () => {
  fetchPosts()
})

// 页面挂载后获取动态列表
onMounted(() => {
  fetchPosts()
})
</script>
