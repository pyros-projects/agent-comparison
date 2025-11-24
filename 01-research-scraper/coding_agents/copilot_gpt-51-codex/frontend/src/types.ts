export type PaperStatus = 'new' | 'read' | 'starred';

export interface Note {
  id: string;
  created_at: string;
  text: string;
}

export interface Paper {
  id: string;
  arxiv_id: string;
  title: string;
  authors: string[];
  abstract: string;
  categories: string[];
  pdf_url: string;
  published_at: string;
  status: PaperStatus;
  starred: boolean;
  tags: string[];
  keywords: string[];
  summary: string;
  methodology: string;
  results: string;
  further_work: string;
  notes: Note[];
  content: string;
  related_ids: string[];
}

export interface ImportTask {
  id: string;
  category_filter?: string;
  text_filter?: string;
  semantic_filter?: string;
  interval_seconds: number;
  status: 'running' | 'stopped';
  total_imported: number;
  total_attempted: number;
  last_run_at?: string;
}

export interface DashboardStats {
  total_papers: number;
  starred: number;
  read: number;
  categories: Record<string, number>;
  recent_activity: Array<{ ts: string; title: string; paper_id: string; type: string }>;
  tasks: ImportTask[];
}

export interface TheoryArgument {
  paper_id: string;
  title: string;
  relevance: number;
  argument: string;
  quotes: string[];
}

export interface TheoryResponse {
  hypothesis: string;
  llm_available: boolean;
  message?: string;
  pro: TheoryArgument[];
  contra: TheoryArgument[];
}

export interface StatusSnapshot {
  llm_available: boolean;
  embedding_provider?: string;
  tasks: ImportTask[];
}

export interface SearchResponse {
  items: Paper[];
  total: number;
}

export interface SimilarPaper {
  paper_id: string;
  title: string;
  score: number;
}

export interface GraphNode {
  id: string;
  label: string;
  category: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  reason: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
