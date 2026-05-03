<template>
  <div class="min-h-screen bg-gradient-to-br from-lzu-blue to-blue-900 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-lzu-blue mb-2">用户注册</h1>
        <p class="text-gray-600">加入兰州大学生活助手</p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">真实姓名</label>
          <input
            v-model="form.real_name"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入真实姓名"
          />
        </div>

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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入邮箱"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-lzu-blue text-white py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors disabled:opacity-50"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <router-link to="/login" class="text-lzu-blue hover:underline">
          已有账号？立即登录
        </router-link>
      </div>

      <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ error }}
      </div>

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

const form = ref({
  student_id: '',
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = false

  try {
    await authStore.register(form.value)
    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请检查输入信息'
  } finally {
    loading.value = false
  }
}
</script>
