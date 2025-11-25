// Paper types
export interface Paper {
  id: string
  arxiv_id: string
  title: string
  authors: string[]
  abstract: string
  summary: string
  keywords: string[]
  questions_answered: string[]
  theories_supported: string[]
  categories: string[]
  primary_category: string
  published: string | null
  updated: string | null
  pdf_url: string
  full_text: string
  status: 'new' | 'read' | 'starred'
  notes: string
  manual_tags: string[]
  created_at: string
  updated_at: string
  has_placeholder_summary: boolean
  has_placeholder_keywords: boolean
  has_placeholder_questions: boolean
  has_placeholder_theories: boolean
  has_embedding: boolean
}

export interface PaperListResponse {
  papers: Paper[]
  total: number
  page: number
  page_size: number
}

export interface SimilarPaper {
  paper: Paper
  score: number
}

export interface RelatedPaper {
  paper_id: string
  title: string
  relationship_type: string
  weight: number
  category: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export interface GraphNode {
  id: string
  title: string
  category: string
  is_center?: boolean
}

export interface GraphEdge {
  source: string
  target: string
  type: string
  weight: number
}

// Search types
export interface SearchResult {
  paper_id: string
  title: string
  abstract: string
  score: number
  primary_category: string
  authors: string[]
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
}

// Theory mode types
export interface TheoryArgument {
  paper_id: string
  paper_title: string
  relevance_score: number
  summary: string
  key_quotes: string[]
}

export interface TheoryResponse {
  theory: string
  pro_arguments: TheoryArgument[]
  contra_arguments: TheoryArgument[]
  analysis_summary: string
  llm_available: boolean
  error?: string
}

// Import task types
export interface ImportTask {
  id: string
  name: string
  category: string | null
  semantic_query: string | null
  text_search: string | null
  check_interval: number
  is_active: boolean
  papers_imported: number
  errors: number
  last_run: string | null
}

export interface ImportTaskCreate {
  name: string
  category?: string
  semantic_query?: string
  text_search?: string
  check_interval: number
}

// Dashboard types
export interface DashboardStats {
  total_papers: number
  storage_size_mb: number
  papers_by_category: Record<string, number>
  papers_today: number
  papers_this_week: number
  active_import_tasks: number
  papers_with_placeholders: number
  llm_available: boolean
  embedding_using_fallback: boolean
}

export interface ActivityItem {
  timestamp: string
  action: string
  paper_id: string
  paper_title: string
}

export interface TopicCluster {
  id: number
  main_category: string
  paper_count: number
  papers: { id: string; title: string }[]
}

export interface DashboardResponse {
  stats: DashboardStats
  recent_activity: ActivityItem[]
  topic_clusters: TopicCluster[]
  growth_data: { date: string; count: number }[]
}

// WebSocket message types
export interface WSMessage {
  type: string
  [key: string]: unknown
}

// System status
export interface SystemStatus {
  llm: {
    available: boolean
    model: string | null
  }
  embedding: {
    using_fallback: boolean
    model: string
  }
  import_tasks: {
    active_count: number
    active_ids: string[]
  }
}

// Word cloud
export interface KeywordCount {
  keyword: string
  count: number
}

// Embedding cluster
export interface EmbeddingClusterPoint {
  paper_id: string
  title: string
  category: string
  x: number
  y: number
  keywords: string[]
}

// Contra papers
export interface ContraPaper {
  paper: Paper
  theory: string
  relevance_score: number
  reason: string
}
