<!--
  文件：BottomNav.vue - 底部导航栏组件
  作用：在页面底部显示固定的导航菜单，用户可以点击切换不同功能页面
  为什么需要：
    1. 所有主要页面都需要底部导航，做成组件可以避免重复代码
    2. 导航栏固定在底部，用户随时可以切换功能
    3. 自动高亮当前所在的页面
-->
<template>
  <!--
    底部导航栏容器
    - fixed: 固定定位，不随页面滚动而移动
    - bottom-0: 固定在页面最底部
    - left-0 right-0: 横向占满整个页面宽度
    - bg-white: 白色背景
    - border-t: 顶部边框线，与页面内容分隔
    - shadow-lg: 阴影效果，增加层次感
    - z-50: 层级设置为 50，确保导航栏在其他内容之上
  -->
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
    <!--
      flex: 使用弹性布局
      justify-around: 在导航项之间均匀分布空间
      py-2: 上下内边距
    -->
    <div class="flex justify-around py-2">
      <!--
        v-for="item in navItems": 循环渲染导航项数组
        为什么用 v-for：避免重复编写每个导航项的 HTML 代码
        :key="item.path": 每个循环项必须有唯一标识，帮助 Vue 高效更新 DOM

        router-link: Vue Router 提供的链接组件
        为什么用 router-link 而不是 a 标签：
          router-link 会在点击时使用 JavaScript 切换页面，不会触发浏览器的整页刷新
          a 标签会导致浏览器重新加载整个页面，用户体验差

        :to="item.path": 绑定跳转路径
        :class 动态类名：根据当前路径是否匹配来切换样式
          isActive(item.path) 返回 true 时，使用 'text-lzu-blue'（蓝色）
          返回 false 时，使用 'text-gray-500'（灰色）
      -->
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center py-1 px-3 min-w-0"
        :class="isActive(item.path) ? 'text-lzu-blue' : 'text-gray-500'"
      >
        <!-- 显示图标（使用 emoji 作为图标） -->
        <span class="text-2xl leading-none">{{ item.icon }}</span>
        <!-- 显示导航项文字标签 -->
        <span class="text-xs mt-1 whitespace-nowrap">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
// 从 vue-router 导入 useRoute 函数
// useRoute 用于获取当前路由的信息（如当前路径、参数等）
import { useRoute } from 'vue-router'

// 获取当前路由对象
// route.path 可以获取当前页面的路径，如 '/home'、'/market' 等
// 用于判断高亮哪个导航项
const route = useRoute()

// 导航项配置数组
// 每个对象包含：
//   - path: 路由路径（点击后跳转到这个路径）
//   - icon: 显示的图标（使用 emoji）
//   - label: 文字标签
// 为什么用数组存储：方便用 v-for 循环渲染，新增或修改导航项只需修改数组
const navItems = [
  { path: '/home', icon: '🏠', label: '首页' },
  { path: '/market', icon: '🛒', label: '二手' },
  { path: '/bus', icon: '🚌', label: '出行' },
  { path: '/venue', icon: '🏀', label: '预约' },
  { path: '/community', icon: '💬', label: '生活圈' },
  { path: '/profile', icon: '👤', label: '我的' },
]

// 判断某个导航项是否处于激活（选中）状态
// path 参数是要检查的导航路径
// route.path === path：精确匹配，如当前是 /market，传入 /market 返回 true
// route.path.startsWith(path + '/')：匹配子路径
//   例如：当前是 /market/123，传入 /market 时，/market/123.startsWith('/market/') 为 true
//   为什么需要这个：商品详情页 /market/123 也应该高亮"二手"导航项
const isActive = (path) => route.path === path || route.path.startsWith(path + '/')
</script>
