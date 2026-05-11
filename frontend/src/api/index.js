// ==========================================
// 文件：index.js - API 接口集中管理文件
// 作用：将所有后端 API 接口按功能模块组织在一起
// 为什么需要这个文件：
//   1. 集中管理所有 API，方便查找和维护
//   2. 统一使用 request.js 中创建的 axios 实例
//   3. 各个组件只需要从这个文件导入需要的 API 函数即可
// ==========================================

// 从 request.js 导入配置好的 axios 实例
// 这个实例已经配置了 baseURL、token 自动注入、错误处理等
import api from './request'

// ==========================================
// 用户认证相关 API
// 作用：处理用户登录、注册、获取当前用户信息、更新个人资料
// ==========================================
export const authAPI = {
  // 登录接口：向服务器发送用户名和密码，获取访问令牌
  // POST 是 HTTP 方法，用于向服务器提交数据
  // /auth/login 是后端定义的登录接口路径
  // data 是登录表单数据，包含 username 和 password
  login: (data) => api.post('/auth/login', data),

  // 注册接口：向服务器提交新用户的注册信息
  // data 包含 student_id、username、password 等注册字段
  register: (data) => api.post('/auth/register', data),

  // 获取当前登录用户信息：需要携带 token 才能获取
  // GET 是 HTTP 方法，用于从服务器获取数据
  // 不需要传参，因为服务器通过请求头中的 token 来识别用户
  getCurrentUser: () => api.get('/auth/me'),

  // 更新用户个人资料：使用 PUT 方法提交修改后的用户信息
  // PUT 是 HTTP 方法，用于更新服务器上的资源
  // data 包含要更新的字段，如 real_name、phone、email 等
  updateProfile: (data) => api.put('/auth/me', data),
}

// ==========================================
// 二手市场相关 API
// 作用：处理商品的增删改查操作
// ==========================================
export const productAPI = {
  // 获取商品列表：支持分页、搜索、分类筛选等查询条件
  // params 是查询参数对象，会自动转换为 URL 查询字符串
  // 例如：{ category: 'electronics', search: '手机' } 会变成 ?category=electronics&search=手机
  getProducts: (params) => api.get('/products/', { params }),

  // 获取当前用户发布的所有商品
  // 不需要参数，服务器通过 token 识别用户身份
  getMyProducts: () => api.get('/products/my'),

  // 根据商品 ID 获取商品详情
  // id 是商品的唯一标识符
  // 模板字符串中 ${id} 会将 id 变量的值插入到 URL 中
  // 例如：getProductById(123) 会请求 /products/123
  getProductById: (id) => api.get(`/products/${id}`),

  // 发布新商品：向服务器提交商品信息
  // data 包含 title、description、price、category、images 等商品字段
  createProduct: (data) => api.post('/products/', data),

  // 更新商品信息：修改已发布的商品
  // id 是要更新的商品 ID，data 是修改后的商品数据
  updateProduct: (id, data) => api.put(`/products/${id}`, data),

  // 删除商品：根据 ID 删除指定商品
  // DELETE 是 HTTP 方法，用于删除服务器上的资源
  deleteProduct: (id) => api.delete(`/products/${id}`),

  // 为商品添加评论
  // id 是商品 ID，data 包含评论内容 { content: '评论内容' }
  addComment: (id, data) => api.post(`/products/${id}/comments`, data),

  // 获取商品的所有评论
  // id 是商品 ID，返回该商品下的所有评论列表
  getComments: (id) => api.get(`/products/${id}/comments`),
}

// ==========================================
// 场馆预约相关 API
// 作用：处理运动场馆的查询和预约操作
// ==========================================
export const venueAPI = {
  // 获取所有可用的场馆列表
  getVenues: () => api.get('/venues/'),

  // 根据场馆 ID 获取场馆详情
  getVenueById: (id) => api.get(`/venues/${id}`),

  // 获取指定场馆的可预约时间段
  // id 是场馆 ID，params 包含查询条件如 days（查询未来几天）
  // 例如：getTimeSlots(1, { days: 3 }) 获取未来 3 天的时段
  getTimeSlots: (id, params) => api.get(`/venues/${id}/time-slots`, { params }),

  // 创建预约：预约指定的时间段
  // data 包含 { time_slot_id: 时段ID }，表示要预约哪个时段
  createBooking: (data) => api.post('/venues/bookings', data),

  // 取消预约：根据预约 ID 取消已有的预约
  cancelBooking: (id) => api.delete(`/venues/bookings/${id}`),

  // 获取当前用户的所有预约记录
  // params 包含筛选条件，如预约状态等
  getMyBookings: (params) => api.get('/venues/bookings/my', { params }),
}

// ==========================================
// 校车服务相关 API
// 作用：查询校车路线和时刻表
// ==========================================
export const busAPI = {
  // 获取所有校车路线
  // 返回值包含路线名称、起点、终点等信息
  getRoutes: () => api.get('/bus/routes'),

  // 获取指定路线的时刻表
  // routeId 是路线 ID，返回该路线的所有发车时间
  getSchedules: (routeId) => api.get(`/bus/routes/${routeId}/schedules`),
}

// ==========================================
// 生活圈相关 API
// 作用：处理社区动态（帖子）和活动的增删改查
// ==========================================
export const communityAPI = {
  // 获取动态列表：支持分类筛选
  // params 包含 { category: '失物招领' } 等筛选条件
  getPosts: (params) => api.get('/community/posts', { params }),

  // 根据 ID 获取动态详情
  getPostById: (id) => api.get(`/community/posts/${id}`),

  // 发布新动态
  // data 包含 title、content、category、images 等动态字段
  createPost: (data) => api.post('/community/posts', data),

  // 删除动态：用户只能删除自己发布的动态
  deletePost: (id) => api.delete(`/community/posts/${id}`),

  // 点赞/取消点赞动态：这是一个切换操作
  // 后端会根据当前状态自动切换：已点赞则取消，未点赞则点赞
  toggleLike: (id) => api.post(`/community/posts/${id}/like`),

  // 为动态添加评论
  addComment: (id, data) => api.post(`/community/posts/${id}/comments`, data),

  // 获取动态的所有评论
  getComments: (id) => api.get(`/community/posts/${id}/comments`),

  // 获取当前用户发布的所有动态
  getMyPosts: () => api.get('/community/posts/my/published'),

  // ========== 活动相关 ==========

  // 获取活动列表：支持分类筛选
  getActivities: (params) => api.get('/community/activities', { params }),

  // 根据 ID 获取活动详情
  getActivityById: (id) => api.get(`/community/activities/${id}`),

  // 发布新活动
  // data 包含 title、description、start_time、location 等活动字段
  createActivity: (data) => api.post('/community/activities', data),

  // 报名参加活动
  // 不需要请求体，服务器通过 token 识别用户，通过 URL 中的 id 识别活动
  registerActivity: (id) => api.post(`/community/activities/${id}/register`),

  // 取消活动报名
  cancelRegistration: (id) => api.delete(`/community/activities/${id}/register`),

  // 获取当前用户发布的所有活动
  getMyPublishedActivities: () => api.get('/community/activities/my/published'),

  // 获取当前用户报名参加的所有活动
  getMyRegisteredActivities: () => api.get('/community/activities/my/registered'),

  // 获取指定活动的报名名单
  // id 是活动 ID，返回所有报名该活动的用户列表
  getActivityRegistrations: (id) => api.get(`/community/activities/${id}/registrations`),
}

// ==========================================
// 文件上传相关 API
// 作用：将本地文件上传到服务器，获取文件的访问 URL
// ==========================================
export const uploadAPI = {
  // 上传文件函数：支持同时上传多个文件
  // files 是一个文件对象数组，来自用户选择的文件
  uploadFiles: (files) => {
    // 创建 FormData 对象
    // FormData 是浏览器提供的 API，用于构造表单数据
    // 为什么要用 FormData：文件上传必须使用 multipart/form-data 格式
    // 普通的 JSON 格式无法传输二进制文件数据
    const formData = new FormData()

    // 遍历所有文件，将每个文件添加到 FormData 中
    // append 方法的参数：
    //   第一个参数 'files' 是后端接收文件的字段名（后端约定）
    //   第二个参数 file 是实际的文件对象
    files.forEach((file) => formData.append('files', file))

    // 发送 POST 请求上传文件
    // 必须手动设置 Content-Type 为 multipart/form-data
    // 为什么：axios 默认使用 JSON 格式，但文件上传必须用 multipart 格式
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
