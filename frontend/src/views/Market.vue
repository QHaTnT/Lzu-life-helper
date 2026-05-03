<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <h1 class="text-lg font-bold">二手市场</h1>
    </header>

    <div class="bg-white p-4 mb-4">
      <input
        v-model="searchQuery"
        @keyup.enter="fetchProducts"
        type="text"
        placeholder="搜索商品..."
        class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-3"
      />
      <div class="flex gap-2 mb-3 overflow-x-auto">
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
      <div class="flex gap-2 text-sm">
        <input
          v-model.number="minPrice"
          type="number"
          placeholder="最低价"
          class="flex-1 px-3 py-1 border border-gray-300 rounded"
        />
        <span class="self-center">-</span>
        <input
          v-model.number="maxPrice"
          type="number"
          placeholder="最高价"
          class="flex-1 px-3 py-1 border border-gray-300 rounded"
        />
        <button @click="fetchProducts" class="bg-lzu-blue text-white px-4 py-1 rounded">筛选</button>
      </div>
    </div>

    <div class="container mx-auto px-4">
      <div class="grid grid-cols-2 gap-4">
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
              :alt="product.title"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-4xl">📦</span>
          </div>
          <div class="p-3">
            <h3 class="font-semibold text-sm mb-1 truncate">{{ product.title }}</h3>
            <p class="text-red-500 font-bold text-lg">¥{{ product.price }}</p>
            <p class="text-xs text-gray-500 mt-1">浏览 {{ product.views || 0 }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
      <div v-if="!loading && products.length === 0" class="text-center py-8 text-gray-500">暂无商品</div>
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
        <h2 class="text-xl font-bold mb-4">发布商品</h2>
        <div class="space-y-3">
          <input
            v-model="form.title"
            type="text"
            placeholder="商品标题"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <textarea
            v-model="form.description"
            placeholder="商品描述"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          ></textarea>
          <input
            v-model.number="form.price"
            type="number"
            placeholder="价格"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <select v-model="form.category" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">选择分类</option>
            <option value="electronics">电子产品</option>
            <option value="books">图书</option>
            <option value="daily">日用品</option>
            <option value="other">其他</option>
          </select>
          <div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              @change="handleFileSelect"
              class="hidden"
            />
            <button
              @click="$refs.fileInput.click()"
              class="w-full border border-dashed border-gray-400 py-3 rounded-lg text-gray-600"
            >
              上传图片 ({{ form.images.length }}/9)
            </button>
            <div v-if="form.images.length > 0" class="grid grid-cols-3 gap-2 mt-2">
              <div
                v-for="(img, idx) in form.images"
                :key="idx"
                class="relative aspect-square bg-gray-100 rounded overflow-hidden"
              >
                <img :src="img" class="w-full h-full object-cover" />
                <button
                  @click="form.images.splice(idx, 1)"
                  class="absolute top-1 right-1 bg-red-500 text-white w-6 h-6 rounded-full text-xs"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button
            @click="showPublishDialog = false"
            class="flex-1 border border-gray-300 py-2 rounded-lg"
          >
            取消
          </button>
          <button
            @click="handlePublish"
            :disabled="publishing"
            class="flex-1 bg-lzu-blue text-white py-2 rounded-lg disabled:opacity-50"
          >
            {{ publishing ? '发布中...' : '发布' }}
          </button>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { productAPI, uploadAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const products = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const minPrice = ref(null)
const maxPrice = ref(null)
const showPublishDialog = ref(false)
const publishing = ref(false)
const fileInput = ref(null)

const form = ref({
  title: '',
  description: '',
  price: null,
  category: '',
  images: [],
})

const categories = [
  { label: '全部', value: '' },
  { label: '电子产品', value: 'electronics' },
  { label: '图书', value: 'books' },
  { label: '日用品', value: 'daily' },
  { label: '其他', value: 'other' },
]

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      category: selectedCategory.value || undefined,
      search: searchQuery.value || undefined,
      min_price: minPrice.value || undefined,
      max_price: maxPrice.value || undefined,
    }
    products.value = await productAPI.getProducts(params)
  } catch (error) {
    console.error('获取商品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files)
  if (form.value.images.length + files.length > 9) {
    alert('最多上传9张图片')
    return
  }
  try {
    const { urls } = await uploadAPI.uploadFiles(files)
    form.value.images.push(...urls)
  } catch (error) {
    alert('图片上传失败')
  }
}

const handlePublish = async () => {
  if (!form.value.title || !form.value.price || !form.value.category) {
    alert('请填写完整信息')
    return
  }
  publishing.value = true
  try {
    await productAPI.createProduct(form.value)
    alert('发布成功')
    showPublishDialog.value = false
    form.value = { title: '', description: '', price: null, category: '', images: [] }
    fetchProducts()
  } catch (error) {
    alert(error.message || '发布失败')
  } finally {
    publishing.value = false
  }
}

watch(selectedCategory, () => {
  fetchProducts()
})

onMounted(() => {
  fetchProducts()
})
</script>
