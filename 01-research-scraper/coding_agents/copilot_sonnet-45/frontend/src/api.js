import axios from 'axios'

const API_BASE = '/api'

console.log('API Client initialized - base URL:', API_BASE)

// Papers API
export const papersAPI = {
  getAll: async (params = {}) => {
    console.log('API: Fetching papers with params:', params)
    const response = await axios.get(`${API_BASE}/papers`, { params })
    console.log(`API: Fetched ${response.data.length} papers`)
    return response.data
  },
  
  getById: async (id) => {
    console.log(`API: Fetching paper ${id}`)
    const response = await axios.get(`${API_BASE}/papers/${id}`)
    console.log(`API: Fetched paper:`, response.data.title)
    return response.data
  },
  
  update: async (id, updates) => {
    console.log(`API: Updating paper ${id}:`, updates)
    const response = await axios.post(`${API_BASE}/papers/${id}`, updates)
    console.log(`API: Paper updated successfully`)
    return response.data
  },
  
  ingest: async (arxivUrl) => {
    console.log(`API: Ingesting paper from ${arxivUrl}`)
    const response = await axios.post(`${API_BASE}/ingest`, { arxiv_url: arxivUrl })
    console.log(`API: Ingestion started for paper ${response.data.paper_id}`)
    return response.data
  },
  
  getSimilar: async (id, limit = 5) => {
    console.log(`API: Fetching similar papers for ${id}`)
    const response = await axios.get(`${API_BASE}/papers/${id}/similar`, { params: { limit } })
    console.log(`API: Found ${response.data.length} similar papers`)
    return response.data
  },
  
  getRelated: async (id, maxResults = 10) => {
    console.log(`API: Fetching related papers for ${id}`)
    const response = await axios.get(`${API_BASE}/papers/${id}/related`, { params: { max_results: maxResults } })
    console.log(`API: Found ${response.data.length} related papers`)
    return response.data
  },
  
  getGraph: async (id, depth = 1) => {
    console.log(`API: Fetching graph for paper ${id} (depth: ${depth})`)
    const response = await axios.get(`${API_BASE}/papers/${id}/graph`, { params: { depth } })
    console.log(`API: Graph has ${response.data.nodes.length} nodes, ${response.data.edges.length} edges`)
    return response.data
  }
}

// Search API
export const searchAPI = {
  semantic: async (query, limit = 10) => {
    console.log(`API: Semantic search for "${query}"`)
    const response = await axios.post(`${API_BASE}/search`, { query, limit })
    console.log(`API: Found ${response.data.length} search results`)
    return response.data
  },
  
  theory: async (hypothesis, limitPerSide = 5) => {
    console.log(`API: Theory analysis for "${hypothesis}"`)
    const response = await axios.post(`${API_BASE}/theory`, { 
      hypothesis, 
      limit_per_side: limitPerSide 
    })
    console.log(`API: Theory analysis complete - ${response.data.pro.length} pro, ${response.data.contra.length} contra`)
    return response.data
  }
}

// Tasks API
export const tasksAPI = {
  getAll: async () => {
    console.log('API: Fetching all tasks')
    const response = await axios.get(`${API_BASE}/tasks`)
    console.log(`API: Fetched ${response.data.length} tasks`)
    return response.data
  },
  
  create: async (taskData) => {
    console.log('API: Creating task:', taskData.name)
    const response = await axios.post(`${API_BASE}/tasks`, taskData)
    console.log(`API: Task created with ID ${response.data.id}`)
    return response.data
  },
  
  start: async (id) => {
    console.log(`API: Starting task ${id}`)
    const response = await axios.post(`${API_BASE}/tasks/${id}/start`)
    console.log(`API: Task started`)
    return response.data
  },
  
  stop: async (id) => {
    console.log(`API: Stopping task ${id}`)
    const response = await axios.post(`${API_BASE}/tasks/${id}/stop`)
    console.log(`API: Task stopped`)
    return response.data
  },
  
  delete: async (id) => {
    console.log(`API: Deleting task ${id}`)
    const response = await axios.delete(`${API_BASE}/tasks/${id}`)
    console.log(`API: Task deleted`)
    return response.data
  }
}

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    console.log('API: Fetching dashboard stats')
    const response = await axios.get(`${API_BASE}/dashboard`)
    console.log(`API: Dashboard stats fetched - ${response.data.total_papers} papers`)
    return response.data
  }
}

// Health check
export const healthAPI = {
  check: async () => {
    console.log('API: Health check')
    const response = await axios.get(`${API_BASE}/health`)
    console.log('API: Health status:', response.data)
    return response.data
  }
}
