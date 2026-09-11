import axios from 'axios'

// Production: VITE_BACKEND_URL=https://your-app.railway.app
// Development: proxy via vite.config.js ke localhost:8000 (VITE_BACKEND_URL tidak perlu diset)
const baseURL = import.meta.env.VITE_BACKEND_URL
  ? `${import.meta.env.VITE_BACKEND_URL}/api`
  : '/api'

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  },
  timeout: 30000,
})

// Request interceptor - support both local auth (Token) and SSO tokens (Bearer)
api.interceptors.request.use(
  (config) => {
    const ssoToken = localStorage.getItem('access_token')
    const localToken = localStorage.getItem('authToken')
    if (ssoToken) {
      // SSO / Keycloak JWT — uses Bearer scheme
      config.headers.Authorization = `Bearer ${ssoToken}`
    } else if (localToken) {
      // Django local Token auth — uses Token scheme
      config.headers.Authorization = `Token ${localToken}`
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
  getJogjaCameras: () => api.get('/etle-camera/cameras/jogja/'),
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

// Camera Management API (local Django backend)
export const cameraApi = {
  list: () => api.get('/cameras/'),
  create: (data) => api.post('/cameras/', data),
  update: (id, data) => api.put(`/cameras/${id}/`, data),
  delete: (id) => api.delete(`/cameras/${id}/`),
}

// CCTV AI-CCTV API (external Jogja Smart Province)
const cctvApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

cctvApi.interceptors.request.use((config) => {
  const ssoToken = localStorage.getItem('access_token')
  if (ssoToken) config.headers.Authorization = `Bearer ${ssoToken}`
  return config
})

export const cctvService = {
  getDevices: (params) => cctvApi.get('/api/devices/', { params }),
  getDevice: (id) => cctvApi.get(`/api/devices/${id}/`),
  getCounting: (params) => cctvApi.get('/api/counting/', { params }),
  getEmbedUrl: (id) => `${import.meta.env.VITE_API_URL || ''}/embed?device=${id}`,
}

// Settings: Role & User Permissions API
export const settingsApi = {
  // Roles (Django Groups)
  getRoles: () => api.get('/roles/'),
  createRole: (data) => api.post('/roles/', data),
  getRole: (id) => api.get(`/roles/${id}/`),
  updateRole: (id, data) => api.put(`/roles/${id}/`, data),
  deleteRole: (id) => api.delete(`/roles/${id}/`),

  // Permissions
  getPermissions: () => api.get('/permissions/'),

  // Users
  getUsers: (params) => api.get('/users/', { params }),
  createUser: (data) => api.post('/users/', data),
  getUser: (id) => api.get(`/users/${id}/`),
  updateUser: (id, data) => api.put(`/users/${id}/`, data),
  deleteUser: (id) => api.delete(`/users/${id}/`),
  toggleUserActive: (id) => api.post(`/users/${id}/toggle-active/`),
}

export default api