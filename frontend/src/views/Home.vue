<!--
  文件：Home.vue - 首页
  作用：应用的主入口页面，显示功能入口和快捷信息
  功能：
    1. 顶部显示应用名称和用户名
    2. 四个功能入口卡片（二手市场、场馆预约、校车服务、生活圈）
    3. 快捷信息区域（天气、图书馆开放时间等）
    4. 底部导航栏
-->
<template>
  <!-- 最小高度为整个视口，灰色背景，底部留出导航栏的空间（pb-20） -->
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <!--
      sticky top-0: 粘性定位，滚动时固定在顶部
      z-10: 层级 10，确保在普通内容之上但在弹出层之下
    -->
    <header class="bg-lzu-blue text-white p-4 shadow-lg">
      <div class="container mx-auto flex justify-between items-center">
        <!-- 应用名称 -->
        <h1 class="text-xl font-bold">兰州大学生活助手</h1>
        <!--
          显示当前登录用户的用户名
          user?.username: 使用可选链操作符
          为什么用 ?. : 防止 user 为 null 时报错（如未登录时）
          如果 user 是 null，表达式会返回 undefined，不会报错
        -->
        <div class="text-sm">{{ user?.username }}</div>
      </div>
    </header>

    <!--
      主要内容区域
      container: 限制最大宽度为 1280px，居中显示
      pb-20: 底部内边距，防止内容被底部导航栏遮挡
    -->
    <main class="container mx-auto p-4 pb-20">
      <!--
        功能入口网格
        grid: CSS Grid 布局
        grid-cols-2: 两列布局
        gap-4: 网格项之间的间距
        mb-6: 下方外边距，与快捷信息区域分隔
      -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <!-- 二手市场入口 -->
        <!--
          router-link: 点击后跳转到对应页面
          to="/market": 目标路径
          整个卡片是一个可点击的链接
        -->
        <router-link
          to="/market"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🛒</div>
          <div class="font-semibold text-gray-800">二手市场</div>
          <div class="text-xs text-gray-500 mt-1">买卖闲置物品</div>
        </router-link>

        <!-- 场馆预约入口 -->
        <router-link
          to="/venue"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🏀</div>
          <div class="font-semibold text-gray-800">场馆预约</div>
          <div class="text-xs text-gray-500 mt-1">预约运动场馆</div>
        </router-link>

        <!-- 校车服务入口 -->
        <router-link
          to="/bus"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">🚌</div>
          <div class="font-semibold text-gray-800">校车服务</div>
          <div class="text-xs text-gray-500 mt-1">查看校车时刻</div>
        </router-link>

        <!-- 生活圈入口 -->
        <router-link
          to="/community"
          class="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow"
        >
          <div class="text-4xl mb-2">💬</div>
          <div class="font-semibold text-gray-800">生活圈</div>
          <div class="text-xs text-gray-500 mt-1">校园动态分享</div>
        </router-link>
      </div>

      <!--
        快捷信息区域
        space-y-2: 子元素之间垂直间距
      -->
      <div class="bg-white rounded-xl p-4 shadow-md">
        <h2 class="font-semibold text-gray-800 mb-3">快捷信息</h2>
        <div class="space-y-2 text-sm text-gray-600">
          <!-- 天气信息 -->
          <div class="flex justify-between">
            <span>今日天气</span>
            <span class="text-lzu-blue">晴 15°C</span>
          </div>
          <!-- 图书馆开放时间 -->
          <div class="flex justify-between">
            <span>图书馆开放</span>
            <span class="text-lzu-blue">8:00 - 22:00</span>
          </div>
          <!-- 食堂营业状态 -->
          <div class="flex justify-between">
            <span>食堂营业</span>
            <span class="text-lzu-blue">正常营业</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部导航栏组件 -->
    <BottomNav />
  </div>
</template>

<script setup>
// 从 Vue 导入 computed：用于创建计算属性
import { computed } from 'vue'
// 导入认证 Store：用于获取当前登录用户信息
import { useAuthStore } from '@/store/auth'
// 导入底部导航栏组件
import BottomNav from '@/components/BottomNav.vue'

// 获取认证 Store 实例
const authStore = useAuthStore()

// 创建计算属性 user，从 Store 中获取用户信息
// computed 的特点：当 authStore.user 变化时，user 会自动更新
// 为什么用 computed 而不是直接用 authStore.user：
//   计算属性有缓存功能，只有依赖变化时才重新计算，性能更好
//   同时在模板中使用 computed 比直接使用 Store 更简洁
const user = computed(() => authStore.user)
</script>
