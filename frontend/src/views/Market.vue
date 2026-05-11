<!--
  文件：Market.vue - 二手市场页面
  作用：展示二手商品列表，支持搜索、分类筛选、价格筛选，并可发布新商品
  功能：
    1. 搜索框：按关键词搜索商品
    2. 分类标签：按商品类型筛选
    3. 价格区间：按价格范围筛选
    4. 商品网格：显示符合条件的商品
    5. 发布对话框：点击"+"按钮发布新商品
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部标题栏 -->
    <header class="bg-white p-4 shadow-md sticky top-0 z-10">
      <h1 class="text-lg font-bold">二手市场</h1>
    </header>

    <!-- 筛选区域 -->
    <div class="bg-white p-4 mb-4">
      <!--
        搜索框
        v-model="searchQuery": 双向绑定搜索关键词
        @keyup.enter="fetchProducts": 监听键盘事件
          - @keyup.enter 表示按回车键时触发
          - 为什么用 enter 而不是 change：搜索框不需要失焦才触发，按回车更符合用户习惯
      -->
      <input
        v-model="searchQuery"
        @keyup.enter="fetchProducts"
        type="text"
        placeholder="搜索商品..."
        class="w-full px-4 py-2 border border-gray-300 rounded-lg mb-3"
      />

      <!--
        分类标签栏
        overflow-x-auto: 水平方向内容超出时可以滚动
        为什么需要这个：分类标签可能很多，一行放不下，需要水平滚动
      -->
      <div class="flex gap-2 mb-3 overflow-x-auto">
        <!--
          v-for="cat in categories": 循环渲染分类数组
          :key="cat.value": 唯一标识
          @click="selectedCategory = cat.value": 点击时更新选中的分类
          :class 动态类名：根据是否选中切换样式
            选中时：蓝色背景白色文字
            未选中时：灰色背景深灰文字
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

      <!-- 价格区间筛选 -->
      <div class="flex gap-2 text-sm">
        <!--
          v-model.number: 双向绑定并自动转换为数字类型
          为什么用 .number：输入框的值默认是字符串，但价格需要是数字才能比较
          如果用户输入非数字，.number 修饰符会保留原始字符串值
        -->
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

    <!-- 商品列表网格 -->
    <div class="container mx-auto px-4">
      <!--
        grid-cols-2: 两列网格布局
        gap-4: 网格项间距
      -->
      <div class="grid grid-cols-2 gap-4">
        <!--
          v-for="product in products": 循环渲染商品列表
          @click: 点击商品卡片跳转到详情页
          $router.push(): 编程式导航，使用 JavaScript 代码跳转页面
            为什么不用 router-link：因为需要动态拼接 URL 路径
        -->
        <div
          v-for="product in products"
          :key="product.id"
          @click="$router.push(`/market/${product.id}`)"
          class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
        >
          <!-- 商品图片区域 -->
          <div class="aspect-square bg-gray-200 flex items-center justify-center overflow-hidden">
            <!--
              v-if="product.images && product.images.length > 0": 条件渲染
              只有商品有图片时才显示 img 标签
              为什么需要这个检查：有些商品可能没有上传图片
              product.images[0]: 显示第一张图片
            -->
            <img
              v-if="product.images && product.images.length > 0"
              :src="product.images[0]"
              :alt="product.title"
              class="w-full h-full object-cover"
            />
            <!--
              v-else: 当 v-if 条件不满足时显示（没有图片时）
              显示一个默认的📦图标
            -->
            <span v-else class="text-4xl">📦</span>
          </div>
          <!-- 商品信息区域 -->
          <div class="p-3">
            <!-- 商品标题：truncate 表示文字超出时显示省略号 -->
            <h3 class="font-semibold text-sm mb-1 truncate">{{ product.title }}</h3>
            <!-- 商品价格：红色加粗显示 -->
            <p class="text-red-500 font-bold text-lg">¥{{ product.price }}</p>
            <!-- 浏览次数：如果 views 不存在则显示 0 -->
            <p class="text-xs text-gray-500 mt-1">浏览 {{ product.views || 0 }}</p>
          </div>
        </div>
      </div>

      <!-- 加载状态提示 -->
      <div v-if="loading" class="text-center py-8 text-gray-500">加载中...</div>
      <!-- 空状态提示：加载完成但没有商品 -->
      <div v-if="!loading && products.length === 0" class="text-center py-8 text-gray-500">暂无商品</div>
    </div>

    <!--
      发布商品浮动按钮
      fixed: 固定定位
      bottom-24 right-6: 距离底部 6rem，距离右边 1.5rem
      w-14 h-14: 宽高都是 3.5rem
      rounded-full: 圆形
    -->
    <button
      @click="showPublishDialog = true"
      class="fixed bottom-24 right-6 w-14 h-14 bg-lzu-blue text-white rounded-full shadow-lg flex items-center justify-center text-2xl"
    >
      +
    </button>

    <!--
      发布商品对话框（弹窗）
      v-if="showPublishDialog": 只有 showPublishDialog 为 true 时才渲染
      fixed inset-0: 固定定位，占满整个视口（全屏遮罩）
      bg-black bg-opacity-50: 半透明黑色背景遮罩
      @click.self="showPublishDialog = false": 点击遮罩关闭弹窗
        .self 修饰符：只在点击元素本身时触发，不包括子元素
        为什么需要：用户点击弹窗外部区域时关闭弹窗，但点击弹窗内部时不关闭
    -->
    <div
      v-if="showPublishDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showPublishDialog = false"
    >
      <!-- 弹窗内容 -->
      <div class="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 class="text-xl font-bold mb-4">发布商品</h2>
        <div class="space-y-3">
          <!-- 商品标题输入框 -->
          <input
            v-model="form.title"
            type="text"
            placeholder="商品标题"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 商品描述输入框 -->
          <!--
            textarea: 多行文本输入框
            rows="4": 默认显示 4 行高度
          -->
          <textarea
            v-model="form.description"
            placeholder="商品描述"
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          ></textarea>
          <!-- 价格输入框 -->
          <input
            v-model.number="form.price"
            type="number"
            placeholder="价格"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <!-- 分类下拉选择框 -->
          <!--
            select + v-model: 下拉选择框
            v-model 绑定选中的值，与 option 的 value 对应
          -->
          <select v-model="form.category" class="w-full px-4 py-2 border border-gray-300 rounded-lg">
            <option value="">选择分类</option>
            <option value="electronics">电子产品</option>
            <option value="books">图书</option>
            <option value="daily">日用品</option>
            <option value="sports">运动</option>
            <option value="clothing">服装</option>
            <option value="other">其他</option>
          </select>
          <!-- 图片上传区域 -->
          <div>
            <!--
              隐藏的文件选择输入框
              ref="fileInput": 为元素添加引用，可以通过 $refs.fileInput 访问
              accept="image/*": 只允许选择图片文件
              multiple: 允许选择多个文件
              @change="handleFileSelect": 选择文件后触发的事件处理函数
              class="hidden": 隐藏输入框（用户不需要看到它）
            -->
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              @change="handleFileSelect"
              class="hidden"
            />
            <!--
              点击触发文件选择的按钮
              $refs.fileInput.click(): 通过引用调用隐藏输入框的 click() 方法
              为什么不直接用 file input：浏览器原生的文件选择框样式不好看，用按钮触发更好看
            -->
            <button
              @click="$refs.fileInput.click()"
              class="w-full border border-dashed border-gray-400 py-3 rounded-lg text-gray-600"
            >
              <!-- 显示已选图片数量 -->
              上传图片 ({{ form.images.length }}/9)
            </button>
            <!-- 已选图片预览网格 -->
            <div v-if="form.images.length > 0" class="grid grid-cols-3 gap-2 mt-2">
              <div
                v-for="(img, idx) in form.images"
                :key="idx"
                class="relative aspect-square bg-gray-100 rounded overflow-hidden"
              >
                <img :src="img" class="w-full h-full object-cover" />
                <!--
                  删除图片按钮
                  form.images.splice(idx, 1): 从数组中删除指定位置的元素
                  splice(索引, 删除个数): 第一个参数是要删除的位置，第二个参数是删除的个数
                  为什么用 splice：它会直接修改数组，Vue 检测到数组变化后会自动更新界面
                -->
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
        <!-- 弹窗底部按钮 -->
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

    <!-- 底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
// 从 Vue 导入需要的函数
// ref: 创建响应式变量
// onMounted: 组件挂载完成后执行的生命周期钩子
// watch: 监听响应式变量变化
import { ref, onMounted, watch } from 'vue'
// 导入商品和上传相关的 API 函数
import { productAPI, uploadAPI } from '@/api'
// 导入底部导航栏组件
import BottomNav from '@/components/BottomNav.vue'

// ==========================================
// 响应式状态定义
// 为什么用 ref：每个状态变化时，界面会自动更新
// ==========================================

// 商品列表数组
const products = ref([])
// 加载状态：为 true 时显示"加载中..."
const loading = ref(false)
// 搜索关键词
const searchQuery = ref('')
// 当前选中的分类
const selectedCategory = ref('')
// 最低价格
const minPrice = ref(null)
// 最高价格
const maxPrice = ref(null)
// 是否显示发布商品弹窗
const showPublishDialog = ref(false)
// 发布中状态：为 true 时按钮显示"发布中..."并禁用
const publishing = ref(false)
// 文件输入框的引用（用于触发文件选择）
const fileInput = ref(null)

// 发布商品的表单数据
// 为什么用 ref 包裹对象：确保对象的属性变化也能被 Vue 检测到
const form = ref({
  title: '',
  description: '',
  price: null,
  category: '',
  images: [], // 已上传的图片 URL 数组
})

// 分类选项数组
// 为什么用数组存储：方便 v-for 循环渲染分类标签
const categories = [
  { label: '全部', value: '' },
  { label: '电子产品', value: 'electronics' },
  { label: '图书', value: 'books' },
  { label: '日用品', value: 'daily' },
  { label: '运动', value: 'sports' },
  { label: '服装', value: 'clothing' },
  { label: '其他', value: 'other' },
]

// ==========================================
// 数据获取函数
// ==========================================

// 获取商品列表
// async/await 的作用：
//   async 标记函数为异步函数，内部可以使用 await
//   await 会暂停函数执行，等待 Promise 完成后继续
//   这样写的好处：异步代码看起来像同步代码，更易读
const fetchProducts = async () => {
  // 设置加载状态为 true，显示加载提示
  loading.value = true
  try {
    // 构建查询参数对象
    // undefined 值的属性会被 axios 自动忽略，不会添加到 URL 查询字符串中
    // 例如：如果 selectedCategory 是空字符串，category 参数不会出现在 URL 中
    const params = {
      category: selectedCategory.value || undefined,
      search: searchQuery.value || undefined,
      min_price: minPrice.value || undefined,
      max_price: maxPrice.value || undefined,
    }
    // 调用 API 获取商品列表，await 等待服务器返回数据
    products.value = await productAPI.getProducts(params)
  } catch (error) {
    // 获取失败时打印错误信息到控制台（开发者工具中查看）
    console.error('获取商品列表失败:', error)
  } finally {
    // 无论成功或失败，都关闭加载状态
    loading.value = false
  }
}

// 处理文件选择事件
// event 是原生 DOM 事件对象，event.target.files 包含用户选择的文件列表
const handleFileSelect = async (event) => {
  // 将文件列表转换为数组（FileList 是类数组对象，不是真正的数组）
  const files = Array.from(event.target.files)
  // 检查图片数量是否超过限制（最多 9 张）
  if (form.value.images.length + files.length > 9) {
    alert('最多上传9张图片')
    return // 提前退出函数，不执行后续代码
  }
  try {
    // 调用上传 API，await 等待上传完成
    // 服务器返回 { urls: ['http://...', 'http://...'] }
    const { urls } = await uploadAPI.uploadFiles(files)
    // 将上传成功后的图片 URL 添加到表单的图片数组中
    // ... 是展开运算符，将 urls 数组中的每个元素逐个添加到 images 数组
    form.value.images.push(...urls)
  } catch (error) {
    alert('图片上传失败')
  }
}

// 发布商品
const handlePublish = async () => {
  // 前端验证：检查必填字段是否已填写
  if (!form.value.title || !form.value.price || !form.value.category) {
    alert('请填写完整信息')
    return
  }
  publishing.value = true
  try {
    // 调用发布商品 API
    await productAPI.createProduct(form.value)
    alert('发布成功')
    // 关闭弹窗
    showPublishDialog.value = false
    // 重置表单数据
    form.value = { title: '', description: '', price: null, category: '', images: [] }
    // 重新获取商品列表，刷新页面显示新发布的商品
    fetchProducts()
  } catch (error) {
    alert(error.message || '发布失败')
  } finally {
    publishing.value = false
  }
}

// ==========================================
// 监听器和生命周期钩子
// ==========================================

// 监听 selectedCategory 的变化
// 当用户点击不同的分类标签时，自动重新获取商品列表
// watch 的第一个参数是要监听的变量，第二个参数是变化时执行的函数
watch(selectedCategory, () => {
  fetchProducts()
})

// 组件挂载完成后执行
// onMounted 是 Vue 的生命周期钩子，组件第一次渲染到页面后会自动调用
// 为什么在这里获取数据：页面一打开就需要显示商品列表
// 如果在 setup 中直接调用 fetchProducts，此时组件可能还没渲染完成
onMounted(() => {
  fetchProducts()
})
</script>
