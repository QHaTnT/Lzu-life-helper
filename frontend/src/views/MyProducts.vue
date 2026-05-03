<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 text-2xl">←</button>
        <h1 class="text-lg font-bold">我的商品</h1>
      </div>
    </header>

    <div class="container mx-auto px-4 py-4">
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>

      <div v-else-if="products.length === 0" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-4">📦</div>
        <p>还没有发布商品</p>
        <button @click="$router.push('/market')" class="mt-4 text-lzu-blue">去发布</button>
      </div>

      <div v-else class="grid grid-cols-2 gap-4">
        <div
          v-for="product in products"
          :key="product.id"
          @click="$router.push(`/market/${product.id}`)"
          class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
        >
          <div class="aspect-square bg-gray-200 flex items-center justify-center overflow-hidden">
            <img
              v-if="product.images && product.images.length > 0"
              :src="product.images[0]"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-4xl">📦</span>
          </div>
          <div class="p-3">
            <h3 class="font-semibold text-sm mb-1 truncate">{{ product.title }}</h3>
            <p class="text-red-500 font-bold">¥{{ product.price }}</p>
            <div class="flex justify-between items-center mt-2">
              <span class="text-xs text-gray-500">浏览 {{ product.views || 0 }}</span>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { productAPI } from '@/api'

const products = ref([])
const loading = ref(true)

const fetchMyProducts = async () => {
  try {
    products.value = await productAPI.getMyProducts()
  } catch (error) {
    console.error('获取我的商品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定删除该商品？')) return
  try {
    await productAPI.deleteProduct(id)
    products.value = products.value.filter((p) => p.id !== id)
  } catch (error) {
    alert(error.message || '删除失败')
  }
}

onMounted(() => {
  fetchMyProducts()
})
</script>
