<!--
  文件：Profile.vue - 个人中心页面
  作用：显示和管理用户个人信息，提供功能入口和退出登录
  功能：
    1. 显示用户头像和基本信息
    2. 编辑个人资料（真实姓名、手机号、邮箱）
    3. 功能入口：我的预约、我的商品、我的动态、我的活动
    4. 退出登录
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部用户信息区域（蓝色背景） -->
    <header class="bg-lzu-blue text-white p-6">
      <div class="flex items-center">
        <!--
          用户头像区域
          @click="$refs.avatarInput.click()": 点击头像触发文件选择
          为什么用 ref：需要直接操作隐藏的 file input 元素
        -->
        <div
          class="w-16 h-16 bg-white rounded-full mr-4 flex items-center justify-center text-3xl overflow-hidden cursor-pointer"
          @click="$refs.avatarInput.click()"
        >
          <!-- 有头像时显示图片，否则显示默认图标 -->
          <img v-if="user?.avatar" :src="user.avatar" class="w-full h-full object-cover" />
          <span v-else>👤</span>
        </div>
        <div>
          <!-- 用户名 -->
          <h2 class="text-xl font-bold">{{ user?.username || '未登录' }}</h2>
          <!-- 学号 -->
          <p class="text-sm opacity-90">学号：{{ user?.student_id || '未设置' }}</p>
        </div>
        <!-- 隐藏的文件选择器：用于上传头像 -->
        <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarUpload" class="hidden" />
      </div>
    </header>

    <div class="container mx-auto p-4 space-y-4">
      <!-- 个人信息卡片 -->
      <div class="bg-white rounded-lg p-4 shadow-md">
        <div class="flex justify-between items-center mb-3">
          <h3 class="font-semibold">个人信息</h3>
          <!-- 编辑/取消按钮 -->
          <button @click="editMode = !editMode" class="text-lzu-blue text-sm">
            {{ editMode ? '取消' : '编辑' }}
          </button>
        </div>

        <!-- 查看模式：显示个人信息（不可编辑） -->
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

        <!-- 编辑模式：显示可编辑的输入框 -->
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
          <!-- 保存按钮 -->
          <button
            @click="handleSaveProfile"
            :disabled="saving"
            class="w-full bg-lzu-blue text-white py-2 rounded-lg text-sm disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <!-- 功能入口列表 -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <!-- 我的预约 -->
        <!--
          @click="$router.push('/my-bookings')": 点击跳转到我的预约页面
          为什么用 push：保持浏览历史，用户可以点击返回
        -->
        <div
          @click="$router.push('/my-bookings')"
          class="p-4 border-b border-gray-100 flex justify-between items-center cursor-pointer hover:bg-gray-50"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">📅</span>
            <span>我的预约</span>
          </div>
          <span class="text-gray-400">›</span>
        </div>
        <!-- 我的商品 -->
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
        <!-- 我发的动态 -->
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
        <!-- 我的活动 -->
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

      <!-- 退出登录按钮 -->
      <button
        @click="handleLogout"
        class="w-full bg-white text-red-500 py-3 rounded-lg shadow-md hover:bg-red-50 transition-colors font-medium border border-red-200"
      >
        退出登录
      </button>
    </div>

    <!-- 底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { authAPI, uploadAPI } from '@/api'
import BottomNav from '@/components/BottomNav.vue'

const router = useRouter()
const authStore = useAuthStore()

// 当前登录用户信息（计算属性，从 Store 中获取）
const user = computed(() => authStore.user)
// 是否处于编辑模式
const editMode = ref(false)
// 保存中状态
const saving = ref(false)
// 头像文件输入框的引用
const avatarInput = ref(null)

// 编辑表单数据
// 初始值从当前用户信息中读取
// 为什么要单独创建 editForm 而不是直接修改 user：
//   user 是 Store 中的状态，直接修改可能影响其他组件
//   editForm 是局部状态，取消编辑时不需要恢复
const editForm = ref({
  real_name: user.value?.real_name || '',
  phone: user.value?.phone || '',
  email: user.value?.email || '',
})

// 保存个人资料
const handleSaveProfile = async () => {
  saving.value = true
  try {
    // 调用 API 更新个人资料，返回更新后的完整用户对象
    const updated = await authAPI.updateProfile(editForm.value)
    // 同步更新 Store 中的用户信息
    authStore.updateUser(updated)
    // 退出编辑模式
    editMode.value = false
  } catch (error) {
    alert(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 头像上传处理
const handleAvatarUpload = async (event) => {
  // 获取用户选择的文件
  const file = event.target.files[0]
  if (!file) return // 用户取消选择时 file 为空

  try {
    // 上传图片到服务器，获取图片 URL
    const { urls } = await uploadAPI.uploadFiles([file])
    // 使用返回的 URL 更新用户头像
    const updated = await authAPI.updateProfile({ avatar: urls[0] })
    // 同步更新 Store 中的用户信息
    authStore.updateUser(updated)
  } catch (error) {
    alert('头像上传失败')
  }
}

// 退出登录
const handleLogout = () => {
  // confirm() 弹出确认对话框，用户点击"确定"返回 true，点击"取消"返回 false
  if (confirm('确定要退出登录吗？')) {
    // 清除登录状态
    authStore.logout()
    // 跳转到登录页
    router.push('/login')
  }
}
</script>
