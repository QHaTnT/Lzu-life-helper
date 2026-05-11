<!--
  文件：MyProducts.vue - 我的商品页面
  作用：显示当前用户发布的所有商品，支持删除商品
  功能：
    1. 显示当前用户发布的商品网格
    2. 点击商品跳转到详情页
    3. 删除商品（带确认提示）
    4. 空状态提示（无商品时引导用户去发布）
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的商品</h1>
      </div>
    </header>

    <div class="container mx-auto px-4 py-4">
      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <!--
        空状态：没有商品时显示
        py-16: 上下大量留白，让提示信息更突出
      -->
      <div v-else-if="products.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-4">📦</div>
        <p>还没有发布商品</p>
        <!-- 跳转到市场页面发布商品 -->
        <button @click="$router.push('/market')" class="mt-4 text-lzu-blue">去发布</button>
      </div>

      <!-- 商品网格列表 -->
      <div v-else class="grid grid-cols-2 gap-4">
        <!--
          v-for="product in products": 循环渲染每个商品
          @click: 点击跳转到商品详情页
        -->
        <div
          v-for="product in products"
          :key="product.id"
          @click="$router.push(`/market/${product.id}`)"
          class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
        >
          <!-- 商品图片 -->
          <div class="aspect-square bg-gray-200 flex items-center justify-center overflow-hidden">
            <img
              v-if="product.images && product.images.length > 0"
              :src="product.images[0]"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-4xl">📦</span>
          </div>
          <!-- 商品信息 -->
          <div class="p-3">
            <h3 class="font-semibold text-sm mb-1 truncate">{{ product.title }}</h3>
            <p class="text-red-500 font-bold">¥{{ product.price }}</p>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-gray-500">浏览 {{ product.views || 0 }}</span>
              <!--
                删除按钮
                @click.stop: 阻止事件冒泡
                为什么需要 .stop：如果不阻止，点击删除按钮会同时触发父元素的 click 事件
                  导致既删除了商品又跳转到了详情页
              -->
              <button
                @click.stop="handleDelete(product.id)"
                class="text-xs text-red-400 hover:text-red-600"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

// 商品列表
const products = ref([])
// 加载状态：初始为 true，加载完成后设为 false
const loading = ref(true)

// 获取当前用户发布的商品
const fetchMyProducts = async () => {
  try {
    // 不需要传参数，服务器通过 token 识别用户
    products.value = await productAPI.getMyProducts()
  } catch (error) {
    console.error('获取我的商品失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除商品
const handleDelete = async (id) => {
  // 弹出确认对话框，用户确认后才执行删除
  if (!confirm('确定删除该商品？')) return
  try {
    // 调用删除 API
    await productAPI.deleteProduct(id)
    // 从本地数组中移除已删除的商品
    // filter 方法返回一个新数组，包含所有不满足删除条件的元素
    // p.id !== id 表示保留 id 不等于要删除 id 的商品
    products.value = products.value.filter((p) => p.id !== id)
  } catch (error) {
    alert(error.message || '删除失败')
  }
}

// 页面挂载后获取商品列表
onMounted(() => {
  fetchMyProducts()
})
</script>
