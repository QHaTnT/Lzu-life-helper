<!--
  文件：Login.vue - 登录页面
  作用：用户输入用户名和密码进行登录
  功能：
    1. 表单输入用户名和密码
    2. 调用后端 API 验证身份
    3. 登录成功后跳转到首页
    4. 显示错误信息（如密码错误）
-->
<template>
  <!--
    min-h-screen: 最小高度为整个视口高度（100vh）
    bg-gradient-to-br: 从左上角到右下角的渐变背景
    from-lzu-blue to-blue-900: 渐变颜色从蓝色到深蓝
    flex items-center justify-center: 让内容垂直和水平居中
    p-4: 内边距，防止内容紧贴屏幕边缘
  -->
  <div class="min-h-screen bg-gradient-to-br from-lzu-blue to-blue-900 flex items-center justify-center p-4">
    <!--
      登录表单卡片
      - bg-white: 白色背景
      - rounded-2xl: 大圆角
      - shadow-2xl: 大阴影，增加立体感
      - w-full max-w-md: 宽度占满但最大为 448px（md 断点）
      - p-8: 内边距
    -->
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <!-- 页面标题区域 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-lzu-blue mb-2">兰州大学生活助手</h1>
        <p class="text-gray-600">欢迎登录</p>
      </div>

      <!--
        登录表单
        @submit.prevent="handleLogin": 表单提交事件处理
        - @submit 监听表单提交事件
        - .prevent 是事件修饰符，等同于 event.preventDefault()
        - 为什么需要 prevent：阻止表单的默认提交行为（会刷新页面）
        - Vue 单页应用不需要刷新页面，通过 JavaScript 处理提交
      -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- 用户名输入框 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">用户名/学号</label>
          <!--
            v-model="form.username": 双向数据绑定
            - 什么是双向绑定：输入框的值和 JavaScript 变量 form.username 自动同步
            - 用户输入时，form.username 会自动更新
            - 代码修改 form.username 时，输入框显示也会自动更新
            - 为什么用 v-model：避免手动操作 DOM 元素，更符合 Vue 的声明式编程

            type="text": 普通文本输入
            required: HTML5 原生验证，表示必填
            placeholder: 输入框为空时显示的提示文字
          -->
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入用户名或学号"
          />
        </div>

        <!-- 密码输入框 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <!--
            type="password": 密码输入类型，输入的字符会显示为圆点
            为什么用 password 类型：防止旁人看到密码内容
          -->
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-lzu-blue focus:border-transparent"
            placeholder="请输入密码"
          />
        </div>

        <!--
          提交按钮
          type="submit": 按钮类型为提交，点击会触发表单的 submit 事件
          :disabled="loading": 动态绑定 disabled 属性
            - 当 loading 为 true 时，按钮变为禁用状态（不可点击）
            - 为什么需要禁用：防止用户重复点击提交按钮，避免发送多个登录请求
        -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-lzu-blue text-white py-3 rounded-lg font-medium hover:bg-blue-800 transition-colors disabled:opacity-50"
        >
          <!--
            三元表达式：loading ? '登录中...' : '登录'
            当 loading 为 true 时显示"登录中..."，否则显示"登录"
            为什么：给用户反馈，表示请求正在处理中
          -->
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册链接 -->
      <div class="mt-6 text-center">
        <!--
          router-link: Vue Router 的链接组件
          to="/register": 点击后跳转到注册页面
          为什么用 router-link：实现客户端导航，不刷新页面
        -->
        <router-link to="/register" class="text-lzu-blue hover:underline">
          还没有账号？立即注册
        </router-link>
      </div>

      <!--
        错误提示区域
        v-if="error": 条件渲染，只有 error 变量不为空时才显示
        为什么用 v-if：错误信息只在出现错误时才需要显示
      -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
// 从 vue 导入 ref：用于创建响应式变量
import { ref } from 'vue'
// 从 vue-router 导入 useRouter：用于编程式页面跳转
import { useRouter } from 'vue-router'
// 导入认证 Store：用于调用登录方法
import { useAuthStore } from '@/store/auth'

// 获取路由实例，用于登录成功后跳转页面
const router = useRouter()
// 获取认证 Store 实例
const authStore = useAuthStore()

// 登录表单数据：包含用户名和密码
// ref 创建一个响应式对象，对象内部的属性变化也能被 Vue 检测到
// 初始值为空字符串，用户输入后会自动更新
const form = ref({
  username: '',
  password: '',
})

// 加载状态：表示登录请求是否正在处理中
// 为 true 时按钮显示"登录中..."并禁用，防止重复提交
const loading = ref(false)

// 错误信息：登录失败时显示错误提示
// 为空时不显示错误区域，有值时显示红色错误提示
const error = ref('')

// 登录处理函数：异步函数，处理表单提交
// async 表示函数内部有异步操作（API 请求），需要使用 await 等待结果
const handleLogin = async () => {
  // 开始加载状态：禁用按钮，显示"登录中..."
  loading.value = true
  // 清空之前的错误信息
  error.value = ''

  try {
    // 调用 Store 中的 login 方法，向服务器发送登录请求
    // await 会等待登录请求完成，如果成功返回用户信息，如果失败抛出错误
    await authStore.login(form.value)

    // 登录成功：跳转到首页
    // router.push 会将新页面压入浏览器历史记录，用户可以点击返回按钮回到登录页
    router.push('/home')
  } catch (err) {
    // 登录失败：显示错误信息
    // err.response?.data?.detail: 尝试从服务器响应中获取详细错误信息
    // 为什么用可选链 ?. : 因为网络错误时 err.response 可能不存在
    // || 后面的字符串是兜底错误信息，防止服务器没有返回错误详情
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    // 无论成功还是失败，都结束加载状态
    // finally 块在 try 和 catch 之后都会执行
    loading.value = false
  }
}
</script>
