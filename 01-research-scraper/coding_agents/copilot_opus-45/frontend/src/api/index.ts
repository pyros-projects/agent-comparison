import { 
  Paper, 
  PaperListResponse, 
  SimilarPaper, 
  RelatedPaper, 
  GraphData,
  SearchResponse,
  TheoryResponse,
  ImportTask,
  ImportTaskCreate,
  DashboardResponse,
  SystemStatus,
  KeywordCount,
  EmbeddingClusterPoint,
  ContraPaper,
} from '../types'

const API_BASE = '/api'

// Utility for logging API calls
function logApiCall(method: string, endpoint: string, data?: unknown) {
  console.log(`[API] ${method} ${endpoint}`, data || '')
}

function logApiResponse(endpoint: string, response: unknown) {
  console.log(`[API] Response from ${endpoint}:`, response)
}

// Papers API
export async function fetchPapers(
  page = 1,
  pageSize = 20,
  status?: string,
  category?: string,
  search?: string
): Promise<PaperListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  })
  if (status) params.set('status', status)
  if (category) params.set('category', category)
  if (search) params.set('search', search)

  const endpoint = `${API_BASE}/papers?${params}`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch papers')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchPaper(id: string): Promise<Paper> {
  const endpoint = `${API_BASE}/papers/${id}`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch paper')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function ingestPaper(arxivUrl: string): Promise<Paper> {
  const endpoint = `${API_BASE}/papers`
  logApiCall('POST', endpoint, { arxiv_url: arxivUrl })

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ arxiv_url: arxivUrl }),
  })
  if (!response.ok) throw new Error('Failed to ingest paper')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function updatePaper(
  id: string,
  updates: { status?: string; notes?: string; manual_tags?: string[] }
): Promise<Paper> {
  const endpoint = `${API_BASE}/papers/${id}`
  logApiCall('PATCH', endpoint, updates)

  const response = await fetch(endpoint, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  })
  if (!response.ok) throw new Error('Failed to update paper')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function deletePaper(id: string): Promise<void> {
  const endpoint = `${API_BASE}/papers/${id}`
  logApiCall('DELETE', endpoint)

  const response = await fetch(endpoint, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete paper')
  
  logApiResponse(endpoint, 'deleted')
}

export async function fetchSimilarPapers(id: string, limit = 10): Promise<SimilarPaper[]> {
  const endpoint = `${API_BASE}/papers/${id}/similar?limit=${limit}`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch similar papers')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchRelatedPapers(id: string): Promise<RelatedPaper[]> {
  const endpoint = `${API_BASE}/papers/${id}/related`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch related papers')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchPaperGraph(id: string): Promise<GraphData> {
  const endpoint = `${API_BASE}/papers/${id}/graph`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch paper graph')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchBibtex(id: string): Promise<string> {
  const endpoint = `${API_BASE}/papers/${id}/bibtex`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch bibtex')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data.bibtex
}

export async function fetchContraPapers(id: string, limit = 10): Promise<ContraPaper[]> {
  const endpoint = `${API_BASE}/papers/${id}/contra?limit=${limit}`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch contra papers')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchCategories(): Promise<Record<string, number>> {
  const endpoint = `${API_BASE}/papers/categories`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch categories')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

// Search API
export async function semanticSearch(query: string, topK = 20): Promise<SearchResponse> {
  const endpoint = `${API_BASE}/search/semantic`
  logApiCall('POST', endpoint, { query, top_k: topK })

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  })
  if (!response.ok) throw new Error('Failed to perform search')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function textSearch(query: string, limit = 20): Promise<SearchResponse> {
  const endpoint = `${API_BASE}/search/text?q=${encodeURIComponent(query)}&limit=${limit}`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to perform text search')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function analyzeTheory(theory: string): Promise<TheoryResponse> {
  const endpoint = `${API_BASE}/search/theory`
  logApiCall('POST', endpoint, { theory })

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theory }),
  })
  if (!response.ok) throw new Error('Failed to analyze theory')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function getTheoryStatus(): Promise<{ available: boolean; message: string }> {
  const endpoint = `${API_BASE}/search/theory/status`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to get theory status')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

// Import tasks API
export async function fetchImportTasks(): Promise<{ tasks: ImportTask[]; active_count: number }> {
  const endpoint = `${API_BASE}/imports`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch import tasks')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function createImportTask(task: ImportTaskCreate): Promise<ImportTask> {
  const endpoint = `${API_BASE}/imports`
  logApiCall('POST', endpoint, task)

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  })
  if (!response.ok) throw new Error('Failed to create import task')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function startImportTask(id: string): Promise<void> {
  const endpoint = `${API_BASE}/imports/${id}/start`
  logApiCall('POST', endpoint)

  const response = await fetch(endpoint, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to start import task')
  
  logApiResponse(endpoint, 'started')
}

export async function stopImportTask(id: string): Promise<void> {
  const endpoint = `${API_BASE}/imports/${id}/stop`
  logApiCall('POST', endpoint)

  const response = await fetch(endpoint, { method: 'POST' })
  if (!response.ok) throw new Error('Failed to stop import task')
  
  logApiResponse(endpoint, 'stopped')
}

export async function deleteImportTask(id: string): Promise<void> {
  const endpoint = `${API_BASE}/imports/${id}`
  logApiCall('DELETE', endpoint)

  const response = await fetch(endpoint, { method: 'DELETE' })
  if (!response.ok) throw new Error('Failed to delete import task')
  
  logApiResponse(endpoint, 'deleted')
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  details: Record<string, unknown>
}

export interface ImportedPaper {
  paper_id: string
  arxiv_id: string
  title: string
  category: string
  imported_at: string
}

export interface ImportTaskDetail extends ImportTask {
  logs: LogEntry[]
  imported_papers: ImportedPaper[]
}

export async function fetchImportTaskDetail(id: string): Promise<ImportTaskDetail> {
  const endpoint = `${API_BASE}/imports/${id}/detail`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch import task detail')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchArxivCategories(): Promise<{ categories: string[] }> {
  const endpoint = `${API_BASE}/imports/categories`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch arXiv categories')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

// Dashboard API
export async function fetchDashboard(): Promise<DashboardResponse> {
  const endpoint = `${API_BASE}/dashboard`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch dashboard')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const endpoint = `${API_BASE}/dashboard/status`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch system status')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchFullGraph(): Promise<GraphData> {
  const endpoint = `${API_BASE}/dashboard/graph`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch full graph')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchKeywords(): Promise<KeywordCount[]> {
  const endpoint = `${API_BASE}/dashboard/keywords`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch keywords')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function fetchEmbeddingClusters(): Promise<EmbeddingClusterPoint[]> {
  const endpoint = `${API_BASE}/dashboard/embedding-clusters`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Failed to fetch embedding clusters')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

// Health check
export async function healthCheck(): Promise<{ status: string; llm_available: boolean; embedding_fallback: boolean }> {
  const endpoint = `${API_BASE}/health`
  logApiCall('GET', endpoint)

  const response = await fetch(endpoint)
  if (!response.ok) throw new Error('Health check failed')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

// Reprocessing API
export interface ReprocessResponse {
  processed: number
  skipped: number
  errors: number
  message: string
}

export async function reprocessQuestionsTheories(paperIds?: string[], force = false): Promise<ReprocessResponse> {
  const endpoint = `${API_BASE}/papers/reprocess/questions-theories?force=${force}`
  logApiCall('POST', endpoint, paperIds)

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: paperIds ? JSON.stringify(paperIds) : 'null',
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || 'Failed to reprocess questions/theories')
  }
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function reprocessKeywords(paperIds?: string[], force = false): Promise<ReprocessResponse> {
  const endpoint = `${API_BASE}/papers/reprocess/keywords?force=${force}`
  logApiCall('POST', endpoint, paperIds)

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: paperIds ? JSON.stringify(paperIds) : 'null',
  })
  if (!response.ok) throw new Error('Failed to reprocess keywords')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function reprocessRelationships(rebuildGraph = true): Promise<ReprocessResponse> {
  const endpoint = `${API_BASE}/papers/reprocess/relationships?rebuild_graph=${rebuildGraph}`
  logApiCall('POST', endpoint)

  const response = await fetch(endpoint, {
    method: 'POST',
  })
  if (!response.ok) throw new Error('Failed to reprocess relationships')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}

export async function reprocessEmbeddings(paperIds?: string[], force = false): Promise<ReprocessResponse> {
  const endpoint = `${API_BASE}/papers/reprocess/embeddings?force=${force}`
  logApiCall('POST', endpoint, paperIds)

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: paperIds ? JSON.stringify(paperIds) : 'null',
  })
  if (!response.ok) throw new Error('Failed to reprocess embeddings')
  
  const data = await response.json()
  logApiResponse(endpoint, data)
  return data
}
