<!--
  文件：Register.vue - 用户注册页面
  作用：新用户填写注册信息，创建账号
  功能：
    1. 表单输入学号、用户名、密码、真实姓名、手机号、邮箱
    2. 调用后端 API 创建新用户
    3. 注册成功后自动跳转到登录页
    4. 表单验证（必填项、手机号格式、密码长度）
-->
<template>
  <!-- 与登录页相同的渐变背景和居中布局 -->
  <div class="min-h-screen bg-gradient-to-br from-lzu-blue to-blue-900 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <!-- 页面标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-lzu-blue mb-2">用户注册</h1>
        <p class="text-gray-600">加入兰州大学生活助手</p>
      </div>

      <!--
        注册表单
        @submit.prevent="handleRegister": 阻止默认提交行为，使用自定义的处理函数
      -->
      <form @submit.prevent="handleRegister" class="space-y-4">
        <!-- 学号/工号（必填） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">学号/工号 *</label>
          <input
            v-model="form.student_id"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入学号或工号"
          />
        </div>

        <!-- 用户名（必填） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">用户名 *</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入用户名"
          />
        </div>

        <!-- 密码（必填，至少6位） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码 *</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="6"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="至少6位密码"
          />
        </div>

        <!-- 真实姓名（选填） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">真实姓名</label>
          <input
            v-model="form.real_name"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入真实姓名"
          />
        </div>

        <!-- 手机号（选填，有格式验证） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">手机号</label>
          <input
            v-model="form.phone"
            type="tel"
            pattern="^1[3-9]\d{9}$"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入手机号"
          />
        </div>

        <!-- 邮箱（选填） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入邮箱"
          />
        </div>

        <!-- 注册按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-lzu-blue text-white py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <!-- 登录链接 -->
      <div class="mt-6 text-center">
        <router-link to="/login" class="text-lzu-blue hover:underline">
          已有账号？立即登录
        </router-link>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ error }}
      </div>

      <!-- 成功提示 -->
      <!--
        v-if="success": 注册成功后显示绿色提示
        为什么同时有 error 和 success：它们不会同时显示
        注册成功时 error 为空，注册失败时 success 为 false
      -->
      <div v-if="success" class="mt-4 p-3 bg-green-50 text-green-600 rounded-lg text-sm">
        注册成功！即将跳转到登录页面...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

// 注册表单数据
// 包含所有注册字段，初始值为空字符串
const form = ref({
  student_id: '',
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
})

// 加载状态：注册请求处理中时为 true
const loading = ref(false)
// 错误信息：注册失败时显示
const error = ref('')
// 成功状态：注册成功时为 true
const success = ref(false)

// 注册处理函数
const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = false

  try {
    // 调用注册 API
    await authStore.register(form.value)
    // 注册成功
    success.value = true
    // 2 秒后自动跳转到登录页
    // 为什么要延迟：让用户看到"注册成功"的提示信息
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    // 注册失败：显示错误信息
    error.value = err.response?.data?.detail || '注册失败，请检查输入信息'
  } finally {
    loading.value = false
  }
}
</script>
