import type {
  DashboardStats,
  GraphResponse,
  ImportTask,
  Paper,
  PaperStatus,
  SearchResponse,
  SimilarPaper,
  StatusSnapshot,
  TheoryQueryRequest,
  TheoryResponse,
} from './types';

const API_BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  console.info('[api] request', url, init?.method ?? 'GET');
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  });
  if (!response.ok) {
    const errorText = await response.text();
    console.error('[api] error', url, errorText);
    throw new Error(errorText);
  }
  return (await response.json()) as T;
}

export async function listPapers(params: Record<string, string | number | undefined>): Promise<SearchResponse> {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.append(key, String(value));
    }
  });
  return request<SearchResponse>(`/papers?${search.toString()}`);
}

export function fetchPaper(paperId: string): Promise<Paper> {
  return request<Paper>(`/papers/${paperId}`);
}

export function updatePaperStatus(paperId: string, payload: { status?: PaperStatus; starred?: boolean }): Promise<Paper> {
  const params = new URLSearchParams();
  if (payload.status) params.append('status', payload.status);
  if (payload.starred !== undefined) params.append('starred', String(payload.starred));
  return request<Paper>(`/papers/${paperId}?${params.toString()}`, { method: 'PATCH' });
}

export function addNote(paperId: string, text: string): Promise<Paper> {
  return request<Paper>(`/papers/${paperId}/notes`, { method: 'POST', body: JSON.stringify({ text }) });
}

export function manualIngest(arxivUrl: string, tags: string[]): Promise<Paper> {
  return request<Paper>('/ingest', { method: 'POST', body: JSON.stringify({ arxiv_url: arxivUrl, tags }) });
}

export function fetchDashboard(): Promise<DashboardStats> {
  return request<DashboardStats>('/dashboard');
}

export function fetchStatus(): Promise<StatusSnapshot> {
  return request<StatusSnapshot>('/status');
}

export function startTask(task: Partial<ImportTask>): Promise<ImportTask> {
  return request<ImportTask>('/tasks', { method: 'POST', body: JSON.stringify(task) });
}

export function stopTask(taskId: string): Promise<{ status: string }> {
  return request<{ status: string }>(`/tasks/${taskId}`, { method: 'PATCH' });
}

export function runTheory(payload: TheoryQueryRequest): Promise<TheoryResponse> {
  return request<TheoryResponse>('/theory', { method: 'POST', body: JSON.stringify(payload) });
}

export type TheoryQueryRequest = {
  hypothesis: string;
  top_k?: number;
};

export function fetchSimilar(paperId: string): Promise<SimilarPaper[]> {
  return request<SimilarPaper[]>(`/papers/${paperId}/similar`);
}

export function fetchGraph(paperId: string): Promise<GraphResponse> {
  return request<GraphResponse>(`/papers/${paperId}/graph`);
}
