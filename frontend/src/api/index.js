import api from './request'

// 用户认证
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/me', data),
}

// 二手市场
export const productAPI = {
  getProducts: (params) => api.get('/products/', { params }),
  getMyProducts: () => api.get('/products/my'),
  getProductById: (id) => api.get(`/products/${id}`),
  createProduct: (data) => api.post('/products/', data),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),
  addComment: (id, data) => api.post(`/products/${id}/comments`, data),
  getComments: (id) => api.get(`/products/${id}/comments`),
}

// 场馆预约
export const venueAPI = {
  getVenues: () => api.get('/venues/'),
  getVenueById: (id) => api.get(`/venues/${id}`),
  getTimeSlots: (id, params) => api.get(`/venues/${id}/time-slots`, { params }),
  createBooking: (data) => api.post('/venues/bookings', data),
  cancelBooking: (id) => api.delete(`/venues/bookings/${id}`),
  getMyBookings: (params) => api.get('/venues/bookings/my', { params }),
}

// 校车服务
export const busAPI = {
  getRoutes: () => api.get('/bus/routes'),
  getSchedules: (routeId) => api.get(`/bus/routes/${routeId}/schedules`),
}

// 生活圈
export const communityAPI = {
  getPosts: (params) => api.get('/community/posts', { params }),
  getPostById: (id) => api.get(`/community/posts/${id}`),
  createPost: (data) => api.post('/community/posts', data),
  deletePost: (id) => api.delete(`/community/posts/${id}`),
  toggleLike: (id) => api.post(`/community/posts/${id}/like`),
  addComment: (id, data) => api.post(`/community/posts/${id}/comments`, data),
  getComments: (id) => api.get(`/community/posts/${id}/comments`),
  getMyPosts: () => api.get('/community/posts/my/published'),

  getActivities: (params) => api.get('/community/activities', { params }),
  getActivityById: (id) => api.get(`/community/activities/${id}`),
  createActivity: (data) => api.post('/community/activities', data),
  registerActivity: (id) => api.post(`/community/activities/${id}/register`),
  cancelRegistration: (id) => api.delete(`/community/activities/${id}/register`),
  getMyPublishedActivities: () => api.get('/community/activities/my/published'),
  getMyRegisteredActivities: () => api.get('/community/activities/my/registered'),
  getActivityRegistrations: (id) => api.get(`/community/activities/${id}/registrations`),
}

// 文件上传
export const uploadAPI = {
  uploadFiles: (files) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
