import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { 
  Search, 
  Star, 
  StarOff, 
  Eye, 
  Trash2, 
  Plus, 
  ChevronLeft, 
  ChevronRight,
  Filter,
  X,
} from 'lucide-react'
import { fetchPapers, updatePaper, deletePaper, ingestPaper, fetchCategories } from '../api'
import { Paper } from '../types'
import { useWebSocket } from '../context/WebSocketContext'

export default function PaperList() {
  const [papers, setPapers] = useState<Paper[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [categories, setCategories] = useState<Record<string, number>>({})
  
  // Ingestion modal
  const [showIngestModal, setShowIngestModal] = useState(false)
  const [ingestUrl, setIngestUrl] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const [ingestError, setIngestError] = useState<string | null>(null)
  
  const { subscribe } = useWebSocket()

  const loadPapers = useCallback(async () => {
    console.log('[PaperList] Loading papers...')
    try {
      setLoading(true)
      const result = await fetchPapers(page, pageSize, statusFilter || undefined, categoryFilter || undefined, searchQuery || undefined)
      setPapers(result.papers)
      setTotal(result.total)
      setError(null)
      console.log('[PaperList] Loaded', result.papers.length, 'papers')
    } catch (e) {
      console.error('[PaperList] Failed to load papers:', e)
      setError('Failed to load papers')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, statusFilter, categoryFilter, searchQuery])

  useEffect(() => {
    loadPapers()
    
    // Load categories
    fetchCategories().then(setCategories).catch(console.error)
    
    // Subscribe to updates
    const unsubscribe = subscribe((message) => {
      if (message.type === 'paper_imported' || message.type === 'backfill_complete') {
        console.log('[PaperList] Refreshing due to:', message.type)
        loadPapers()
      }
    })
    
    return unsubscribe
  }, [loadPapers, subscribe])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadPapers()
  }

  const handleStatusChange = async (paperId: string, newStatus: 'starred' | 'read' | 'new') => {
    console.log('[PaperList] Updating status:', paperId, newStatus)
    try {
      await updatePaper(paperId, { status: newStatus })
      setPapers(papers.map(p => p.id === paperId ? { ...p, status: newStatus } : p))
    } catch (e) {
      console.error('[PaperList] Failed to update status:', e)
    }
  }

  const handleDelete = async (paperId: string) => {
    if (!confirm('Are you sure you want to delete this paper?')) return
    
    console.log('[PaperList] Deleting paper:', paperId)
    try {
      await deletePaper(paperId)
      setPapers(papers.filter(p => p.id !== paperId))
      setTotal(total - 1)
    } catch (e) {
      console.error('[PaperList] Failed to delete paper:', e)
    }
  }

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ingestUrl) return
    
    console.log('[PaperList] Ingesting paper:', ingestUrl)
    setIngesting(true)
    setIngestError(null)
    
    try {
      await ingestPaper(ingestUrl)
      setShowIngestModal(false)
      setIngestUrl('')
      loadPapers()
    } catch (e) {
      console.error('[PaperList] Failed to ingest paper:', e)
      setIngestError('Failed to ingest paper. Please check the URL and try again.')
    } finally {
      setIngesting(false)
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Papers</h1>
        <button
          onClick={() => setShowIngestModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          Add Paper
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search papers..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Status</option>
            <option value="new">New</option>
            <option value="read">Read</option>
            <option value="starred">Starred</option>
          </select>
          
          <select
            value={categoryFilter}
            onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Categories</option>
            {Object.entries(categories).map(([cat, count]) => (
              <option key={cat} value={cat}>{cat} ({count})</option>
            ))}
          </select>
          
          <button
            type="submit"
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Filter size={20} />
          </button>
          
          {(searchQuery || statusFilter || categoryFilter) && (
            <button
              type="button"
              onClick={() => { setSearchQuery(''); setStatusFilter(''); setCategoryFilter(''); setPage(1); }}
              className="px-4 py-2 text-gray-500 hover:text-gray-700"
            >
              <X size={20} />
            </button>
          )}
        </form>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Papers table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : papers.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No papers found. Add some papers to get started!
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Authors
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {papers.map((paper) => (
                <tr key={paper.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link 
                      to={`/papers/${paper.id}`}
                      className="text-blue-600 hover:underline font-medium line-clamp-2"
                    >
                      {paper.title}
                    </Link>
                    {paper.has_placeholder_summary && (
                      <span className="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
                        Placeholder
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {paper.authors.slice(0, 3).join(', ')}
                    {paper.authors.length > 3 && ` +${paper.authors.length - 3}`}
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                      {paper.primary_category}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {paper.published ? new Date(paper.published).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-xs px-2 py-1 rounded ${
                      paper.status === 'starred' ? 'bg-yellow-100 text-yellow-700' :
                      paper.status === 'read' ? 'bg-green-100 text-green-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {paper.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => handleStatusChange(paper.id, paper.status === 'starred' ? 'new' : 'starred')}
                      className="p-1 text-gray-400 hover:text-yellow-500 transition-colors"
                      title={paper.status === 'starred' ? 'Unstar' : 'Star'}
                    >
                      {paper.status === 'starred' ? <Star size={18} fill="currentColor" className="text-yellow-500" /> : <StarOff size={18} />}
                    </button>
                    <button
                      onClick={() => handleStatusChange(paper.id, paper.status === 'read' ? 'new' : 'read')}
                      className="p-1 text-gray-400 hover:text-green-500 transition-colors"
                      title={paper.status === 'read' ? 'Mark unread' : 'Mark read'}
                    >
                      <Eye size={18} className={paper.status === 'read' ? 'text-green-500' : ''} />
                    </button>
                    <button
                      onClick={() => handleDelete(paper.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} papers
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={20} />
              </button>
              <span className="text-sm text-gray-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Ingest modal */}
      {showIngestModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Add Paper from arXiv</h2>
            <form onSubmit={handleIngest}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  arXiv URL or ID
                </label>
                <input
                  type="text"
                  value={ingestUrl}
                  onChange={(e) => setIngestUrl(e.target.value)}
                  placeholder="e.g., https://arxiv.org/abs/2301.00001 or 2301.00001"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={ingesting}
                />
              </div>
              
              {ingestError && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {ingestError}
                </div>
              )}
              
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => { setShowIngestModal(false); setIngestUrl(''); setIngestError(null); }}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  disabled={ingesting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!ingestUrl || ingesting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {ingesting && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                  {ingesting ? 'Ingesting...' : 'Add Paper'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
