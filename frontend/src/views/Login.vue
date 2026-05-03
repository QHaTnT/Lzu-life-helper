<template>
  <div class="min-h-screen bg-gradient-to-br from-lzu-blue to-blue-900 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-lzu-blue mb-2">兰州大学生活助手</h1>
        <p class="text-gray-600">欢迎登录</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">用户名/学号</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入用户名或学号"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入密码"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-lzu-blue text-white py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors disabled:opacity-50"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <router-link to="/register" class="text-lzu-blue hover:underline">
          还没有账号？立即注册
        </router-link>
      </div>

      <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ error }}
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
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.login(form.value)
    router.push('/home')
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
