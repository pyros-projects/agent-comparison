import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
})

// Papers API
export const papersApi = {
  getAll: (params = {}) => api.get('/papers', { params }),
  getById: (id) => api.get(`/papers/${id}`),
  create: (data) => api.post('/papers', data),
  update: (id, data) => api.put(`/papers/${id}`, data),
  delete: (id) => api.delete(`/papers/${id}`),
  ingest: (url) => api.post('/papers/ingest', { url }),
}

// Search API
export const searchApi = {
  search: (query, params = {}) => api.post('/search', { query, ...params }),
  similar: (paperId, limit = 10) => api.get(`/search/similar/${paperId}?limit=${limit}`),
}

// Theory API
export const theoryApi = {
  analyze: (theory) => api.post('/theory/analyze', { theory }),
}

// Dashboard API
export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getActivity: () => api.get('/dashboard/activity'),
  getCategories: () => api.get('/dashboard/categories'),
}

// Continuous Import API
export const importApi = {
  getTasks: () => api.get('/import/tasks'),
  createTask: (config) => api.post('/import/tasks', config),
  startTask: (taskId) => api.post(`/import/tasks/${taskId}/start`),
  stopTask: (taskId) => api.post(`/import/tasks/${taskId}/stop`),
  deleteTask: (taskId) => api.delete(`/import/tasks/${taskId}`),
}

export default api
