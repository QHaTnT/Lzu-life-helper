<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-lzu-blue text-white p-6">
      <div class="flex items-center">
        <div
          class="w-16 h-16 bg-white rounded-full mr-4 flex items-center justify-center text-3xl overflow-hidden cursor-pointer"
          @click="$refs.avatarInput.click()"
        >
          <img v-if="user?.avatar" :src="user.avatar" class="w-full h-full object-cover" />
          <span v-else>👤</span>
        </div>
        <div>
          <h2 class="text-xl font-bold">{{ user?.username || '未登录' }}</h2>
          <p class="text-sm opacity-90">学号：{{ user?.student_id || '未设置' }}</p>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarUpload" class="hidden" />
      </div>
    </header>

    <div class="container mx-auto p-4 space-y-4">
      <div class="bg-white rounded-lg p-4 shadow-md">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold">个人信息</h3>
          <button @click="editMode = !editMode" class="text-lzu-blue text-sm">
            {{ editMode ? '取消' : '编辑' }}
          </button>
        </div>
        <div v-if="!editMode" class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">真实姓名</span>
            <span>{{ user?.real_name || '未设置' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">手机号</span>
            <span>{{ user?.phone || '未设置' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">邮箱</span>
            <span>{{ user?.email || '未设置' }}</span>
          </div>
        </div>
        <div v-else class="space-y-3">
          <div>
            <label class="text-sm text-gray-600">真实姓名</label>
            <input
              v-model="editForm.real_name"
              type="text"
              class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label class="text-sm text-gray-600">手机号</label>
            <input
              v-model="editForm.phone"
              type="tel"
              class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label class="text-sm text-gray-600">邮箱</label>
            <input
              v-model="editForm.email"
              type="email"
              class="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <button
            @click="handleSaveProfile"
            :disabled="saving"
            class="w-full bg-lzu-blue text-white py-2 rounded-lg text-sm disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div
          @click="$router.push('/venue')"
          class="p-4 border-b border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">📅</span>
            <span>我的预约</span>
          </div>
          <span class="text-gray-400">›</span>
        </div>
        <div
          @click="$router.push('/my-products')"
          class="p-4 border-b border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">📦</span>
            <span>我的商品</span>
          </div>
          <span class="text-gray-400">›</span>
        </div>
        <div
          @click="$router.push('/my-posts')"
          class="p-4 border-b border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">💬</span>
            <span>我发的动态</span>
          </div>
          <span class="text-gray-400">›</span>
        </div>
        <div
          @click="$router.push('/my-activities')"
          class="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">🎉</span>
            <span>我的活动</span>
          </div>
          <span class="text-gray-400">›</span>
        </div>
      </div>

      <button
        @click="handleLogout"
        class="w-full bg-white text-red-500 py-3 rounded-lg shadow-md hover:bg-red-50 transition-colors font-medium border border-red-200"
      >
        退出登录
      </button>
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
        <router-link to="/community" class="flex flex-col items-center text-gray-500">
          <span class="text-2xl">💬</span>
          <span class="text-xs mt-1">生活圈</span>
        </router-link>
        <router-link to="/profile" class="flex flex-col items-center text-lzu-blue">
          <span class="text-2xl">👤</span>
          <span class="text-xs mt-1">我的</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { authAPI, uploadAPI } from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const editMode = ref(false)
const saving = ref(false)
const avatarInput = ref(null)

const editForm = ref({
  real_name: user.value?.real_name || '',
  phone: user.value?.phone || '',
  email: user.value?.email || '',
})

const handleSaveProfile = async () => {
  saving.value = true
  try {
    const updated = await authAPI.updateProfile(editForm.value)
    authStore.updateUser(updated)
    editMode.value = false
  } catch (error) {
    alert(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const { urls } = await uploadAPI.uploadFiles([file])
    const updated = await authAPI.updateProfile({ avatar: urls[0] })
    authStore.updateUser(updated)
  } catch (error) {
    alert('头像上传失败')
  }
}

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>
