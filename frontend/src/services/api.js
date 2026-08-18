import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor - support both local auth and SSO tokens
api.interceptors.request.use(
  (config) => {
    const ssoToken = localStorage.getItem('access_token')
    const localToken = localStorage.getItem('authToken')
    const token = ssoToken || localToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('expires_at')
      localStorage.removeItem('refresh_expires_at')
      localStorage.removeItem('token_response')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Face Comparison API
export const faceComparisonApi = {
  compare: (formData) => api.post('/face-compare/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getHistory: (params) => api.get('/face-comparison/history/', { params }),
  getDetail: (id) => api.get(`/face-comparison/${id}/`),
  delete: (id) => api.delete(`/face-comparison/${id}/`),
}

// Person API
export const personApi = {
  list: (params) => api.get('/people/', { params }),
  get: (id) => api.get(`/people/${id}/`),
  create: (data) => api.post('/people/', data),
  update: (id, data) => api.put(`/people/${id}/`, data),
  delete: (id) => api.delete(`/people/${id}/`),
  register: (formData) => api.post('/people/register/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  uploadPhotos: (id, formData) => api.post(`/people/${id}/upload-photos/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getPhotos: (id) => api.get(`/people/${id}/photos/`),
  deletePhoto: (id, photoId) => api.delete(`/people/${id}/photos/${photoId}/`),
}

// Identify API
export const identifyApi = {
  identify: (formData) => api.post('/identify/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getModels: () => api.get('/identify/models/'),
}

// History API
export const historyApi = {
  list: (params) => api.get('/history/', { params }),
  get: (id) => api.get(`/history/${id}/`),
  delete: (id) => api.delete(`/history/${id}/`),
  clear: () => api.delete('/history/clear/'),
}

// Model Settings API
export const modelSettingsApi = {
  get: () => api.get('/model-settings/'),
  update: (data) => api.put('/model-settings/', data),
  getAvailableModels: () => api.get('/model-settings/available/'),
  testModel: (data) => api.post('/model-settings/test/', data),
}

// Live Camera API
export const liveCameraApi = {
  saveSnapshot: (data) => api.post('/live-camera/snapshot/', data),
  getSnapshots: (params) => api.get('/live-camera/snapshots/', { params }),
  deleteSnapshot: (id) => api.delete(`/live-camera/snapshots/${id}/`),
}

// Pose Estimation API
export const poseEstimationApi = {
  estimate: (formData) => api.post('/pose-estimation/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getHistory: (params) => api.get('/pose-estimation/history/', { params }),
}

// ETLE Camera API
export const etleCameraApi = {
  getCameras: () => api.get('/etle-camera/cameras/'),
  getCameraStream: (id) => api.get(`/etle-camera/cameras/${id}/stream/`),
  detectViolation: (formData) => api.post('/etle-camera/detect/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
}

// Violation Logs API
export const violationLogsApi = {
  list: (params) => api.get('/violation-logs/', { params }),
  get: (id) => api.get(`/violation-logs/${id}/`),
  delete: (id) => api.delete(`/violation-logs/${id}/`),
  getStats: () => api.get('/violation-logs/stats/'),
}

// Auth API
export const authApi = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (data) => api.post('/auth/register/', data),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.put('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
}

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats/'),
  getRecentActivity: (params) => api.get('/dashboard/recent-activity/', { params }),
  getChartData: (params) => api.get('/dashboard/charts/', { params }),
}

// Forensic Analysis API
export const forensicApi = {
  analyze: (formData) => api.post('/forensic/ela/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getHistory: (params) => api.get('/forensic/ela/', { params }),
}

export default api