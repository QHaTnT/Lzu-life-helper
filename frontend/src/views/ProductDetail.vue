<!--
  文件：ProductDetail.vue - 商品详情页面
  作用：展示单个商品的详细信息，包括图片、价格、描述、卖家信息和评论
  功能：
    1. 图片轮播：多张图片可切换查看
    2. 商品信息：标题、价格、浏览次数、发布时间
    3. 卖家信息：头像、用户名、联系方式
    4. 评论区：查看和发布评论
    5. 底部操作栏：联系卖家、我想要（跳转到评论区）
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <!-- 返回按钮 -->
        <!--
          @click="$router.back()": 点击时调用路由的 back 方法
          $router.back() 等同于浏览器的后退按钮
          为什么用 back 而不是 push('/market')：用户可能是从收藏夹或其他地方直接打开的
            用 back 可以正确返回用户之前的页面
        -->
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">商品详情</h1>
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

    <!--
      v-else-if="product": 只有 loading 为 false 且 product 不为 null 时才显示
      为什么用 v-else-if：避免在加载时显示空内容，也避免 product 不存在时报错
    -->
    <div v-else-if="product" class="container mx-auto pb-4">
      <!-- 图片区域 -->
      <div class="bg-white mb-4">
        <!-- 有图片时显示 -->
        <div v-if="product.images && product.images.length > 0" class="relative">
          <!-- 主图显示 -->
          <div class="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
            <!--
              :src="product.images[currentImageIndex]": 动态绑定图片源
              currentImageIndex 是当前显示的图片索引
              点击缩略图时会改变这个值，从而切换显示的图片
            -->
            <img
              :src="product.images[currentImageIndex]"
              :alt="product.title"
              class="w-full h-full object-contain"
            />
          </div>
          <!-- 图片计数指示器 -->
          <!--
            绝对定位在图片右下角
            显示当前图片序号，如 "1/3"
          -->
          <div
            v-if="product.images.length > 1"
            class="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded"
          >
            {{ currentImageIndex + 1 }}/{{ product.images.length }}
          </div>
          <!-- 缩略图列表 -->
          <div v-if="product.images.length > 1" class="flex justify-center gap-2 p-2 overflow-x-auto">
            <img
              v-for="(img, idx) in product.images"
              :key="idx"
              :src="img"
              @click="currentImageIndex = idx"
              :class="[
                'w-16 h-16 object-cover rounded cursor-pointer border-2',
                // 当前选中的缩略图添加蓝色边框
                currentImageIndex === idx ? 'border-lzu-blue' : 'border-transparent',
              ]"
            />
          </div>
        </div>
        <!-- 无图片时显示默认图标 -->
        <div v-else class="aspect-square bg-gray-200 flex items-center justify-center">
          <span class="text-8xl">📦</span>
        </div>
      </div>

      <!-- 商品基本信息 -->
      <div class="bg-white p-4 mb-4">
        <h1 class="text-xl font-bold mb-2">{{ product.title }}</h1>
        <div class="text-3xl text-red-500 font-bold mb-3">¥{{ product.price }}</div>
        <div class="flex gap-3 text-sm text-gray-500 mb-3">
          <span>浏览 {{ product.views || 0 }}</span>
          <span>|</span>
          <!-- formatTime 是自定义的时间格式化函数 -->
          <span>{{ formatTime(product.created_at) }}</span>
        </div>
        <!--
          whitespace-pre-wrap: 保留文本中的换行符和空格
          为什么需要：用户输入的商品描述可能包含换行，需要原样显示
        -->
        <div class="text-gray-700 whitespace-pre-wrap">{{ product.description }}</div>
      </div>

      <!-- 卖家信息 -->
      <div class="bg-white p-4 mb-4">
        <h3 class="font-semibold mb-3">卖家信息</h3>
        <div class="flex items-center">
          <!-- 卖家头像 -->
          <div class="w-12 h-12 bg-gray-300 rounded-full mr-3 flex items-center justify-center text-xl overflow-hidden">
            <!-- 有头像时显示图片，否则显示默认图标 -->
            <img v-if="product.seller?.avatar" :src="product.seller.avatar" class="w-full h-full object-cover" />
            <span v-else>👤</span>
          </div>
          <div>
            <!-- 卖家用户名：如果用户名不存在则显示"用户+ID"作为备用 -->
            <div class="font-semibold">{{ product.seller?.username || '用户' + product.seller_id }}</div>
            <!-- 卖家手机号：只有设置了手机号才显示 -->
            <div v-if="product.seller?.phone" class="text-sm text-gray-500">📱 {{ product.seller.phone }}</div>
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <!--
        id="comment-section": 为元素设置 ID
        为什么需要 ID：底部的"我想要"按钮会通过这个 ID 滚动页面到评论区
      -->
      <div id="comment-section" class="bg-white p-4 mb-4">
        <h3 class="font-semibold mb-3">留言板 ({{ comments.length }})</h3>

        <!-- 无评论时显示 -->
        <div v-if="comments.length === 0" class="text-center text-gray-400 py-4">暂无留言</div>

        <!-- 评论列表 -->
        <div v-else class="space-y-3 mb-4">
          <!--
            v-for="comment in comments": 循环渲染每条评论
            border-b: 底部边框线，分隔每条评论
            last:border-b-0: 最后一条评论不要底部边框
          -->
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

        <!-- 评论输入框：已登录用户才能看到 -->
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
        <!-- 未登录用户看到的提示 -->
        <div v-else class="text-center text-gray-500 py-2">
          <router-link to="/login" class="text-lzu-blue">登录后可留言</router-link>
        </div>
      </div>
    </div>

    <!-- 底部固定操作栏 -->
    <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
      <div class="container mx-auto flex gap-3">
        <button
          @click="contactSeller"
          class="flex-1 border border-lzu-blue text-lzu-blue py-3 rounded-lg font-medium"
        >
          联系卖家
        </button>
        <!-- "我想要"按钮：滚动到评论区并聚焦输入框 -->
        <button @click="scrollToComment" class="flex-1 bg-lzu-blue text-white py-3 rounded-lg font-medium">我想要</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
// useRoute: 获取当前路由信息（如 URL 参数）
import { useRoute } from 'vue-router'
import { productAPI } from '@/api'
import { useAuthStore } from '@/store/auth'

// 获取当前路由对象
const route = useRoute()
const authStore = useAuthStore()

// 商品详情数据
const product = ref(null)
// 评论列表
const comments = ref([])
// 加载状态
const loading = ref(true)
// 评论输入框的值
const commentText = ref('')
// 评论提交状态（防止重复提交）
const submitting = ref(false)
// 当前显示的图片索引（用于图片切换）
const currentImageIndex = ref(0)

// 计算属性：用户是否已登录
// 为什么用 computed：当 authStore.isAuthenticated 变化时会自动更新
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 获取商品详情和评论
const fetchProduct = async () => {
  try {
    // route.params.id 获取 URL 中的动态参数
    // 例如 URL 是 /market/123，则 route.params.id 的值是 '123'
    // 同时获取商品详情和评论，使用 Promise.all 可以并行请求提高效率
    // 这里是顺序请求，因为评论依赖商品存在
    product.value = await productAPI.getProductById(route.params.id)
    comments.value = await productAPI.getComments(route.params.id)
  } catch (error) {
    console.error('获取商品详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 提交评论
const submitComment = async () => {
  // trim() 去除字符串首尾空格，防止用户只输入空格
  if (!commentText.value.trim()) return

  submitting.value = true
  try {
    // 发送评论，服务器返回新创建的评论对象（包含 id、用户名、时间等）
    const newComment = await productAPI.addComment(route.params.id, { content: commentText.value })
    // 将新评论添加到评论列表末尾
    // push 方法会修改数组，Vue 检测到变化后会自动更新界面
    comments.value.push(newComment)
    // 清空输入框
    commentText.value = ''
  } catch (error) {
    alert(error.message || '发送失败')
  } finally {
    submitting.value = false
  }
}

// 联系卖家：显示卖家手机号
const contactSeller = () => {
  if (product.value?.seller?.phone) {
    alert(`卖家联系方式：${product.value.seller.phone}`)
  } else {
    alert('卖家未设置联系方式，请在留言板留言')
    scrollToComment()
  }
}

// 滚动到评论区并聚焦输入框
const scrollToComment = () => {
  if (!isAuthenticated.value) {
    alert('请先登录后再留言')
    return
  }
  // scrollIntoView: 原生 DOM 方法，将元素滚动到可视区域
  // behavior: 'smooth' 表示平滑滚动（有动画效果）
  document.getElementById('comment-section')?.scrollIntoView({ behavior: 'smooth' })
  // setTimeout: 延迟 400 毫秒后执行
  // 为什么要延迟：等待滚动动画完成后，再聚焦输入框，否则输入框可能还没滚动到可视区域
  setTimeout(() => {
    document.querySelector('#comment-section input')?.focus()
  }, 400)
}

// 时间格式化函数：将 ISO 时间字符串转换为相对时间
// 例如："3 分钟前"、"2 小时前"、"5 天前"、"3月15日"
const formatTime = (dateStr) => {
  const date = new Date(dateStr) // 将字符串转换为 Date 对象
  const now = new Date() // 获取当前时间
  // 计算时间差（毫秒）
  const diff = now - date
  // 将毫秒转换为分钟、小时、天数（取整数部分）
  const minutes = Math.floor(diff / 60000) // 1 分钟 = 60000 毫秒
  const hours = Math.floor(diff / 3600000) // 1 小时 = 3600000 毫秒
  const days = Math.floor(diff / 86400000) // 1 天 = 86400000 毫秒

  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  // 超过 7 天显示具体日期
  // getMonth() 返回 0-11，所以要 +1
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 组件挂载完成后获取商品详情
onMounted(() => {
  fetchProduct()
})
</script>
