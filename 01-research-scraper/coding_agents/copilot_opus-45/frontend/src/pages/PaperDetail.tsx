import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { 
  ArrowLeft, 
  Star, 
  StarOff, 
  Eye, 
  ExternalLink, 
  Copy,
  Check,
  AlertCircle,
  Network,
} from 'lucide-react'
import { 
  fetchPaper, 
  fetchSimilarPapers, 
  fetchRelatedPapers, 
  fetchPaperGraph,
  fetchBibtex, 
  fetchContraPapers,
  updatePaper 
} from '../api'
import { Paper, SimilarPaper, RelatedPaper, GraphData, ContraPaper } from '../types'
import { useWebSocket } from '../context/WebSocketContext'

export default function PaperDetail() {
  const { id } = useParams<{ id: string }>()
  const [paper, setPaper] = useState<Paper | null>(null)
  const [similarPapers, setSimilarPapers] = useState<SimilarPaper[]>([])
  const [relatedPapers, setRelatedPapers] = useState<RelatedPaper[]>([])
  const [contraPapers, setContraPapers] = useState<ContraPaper[]>([])
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notes, setNotes] = useState('')
  const [savingNotes, setSavingNotes] = useState(false)
  const [copiedBibtex, setCopiedBibtex] = useState(false)
  const [activeTab, setActiveTab] = useState<'summary' | 'similar' | 'contra' | 'graph' | 'full'>('summary')
  
  const { subscribe } = useWebSocket()

  useEffect(() => {
    if (!id) return

    const loadPaper = async () => {
      console.log('[PaperDetail] Loading paper:', id)
      try {
        setLoading(true)
        const [paperData, similar, related, graph, contra] = await Promise.all([
          fetchPaper(id),
          fetchSimilarPapers(id, 10),
          fetchRelatedPapers(id),
          fetchPaperGraph(id),
          fetchContraPapers(id, 10),
        ])
        setPaper(paperData)
        setSimilarPapers(similar)
        setRelatedPapers(related)
        setGraphData(graph)
        setContraPapers(contra)
        setNotes(paperData.notes || '')
        setError(null)
        console.log('[PaperDetail] Paper loaded:', paperData.title)
      } catch (e) {
        console.error('[PaperDetail] Failed to load paper:', e)
        setError('Failed to load paper')
      } finally {
        setLoading(false)
      }
    }

    loadPaper()
    
    // Subscribe to backfill updates
    const unsubscribe = subscribe((message) => {
      if (message.type === 'backfill_complete' && message.paper_id === id) {
        console.log('[PaperDetail] Paper backfilled, refreshing...')
        loadPaper()
      }
    })
    
    return unsubscribe
  }, [id, subscribe])

  const handleStatusChange = async (newStatus: 'starred' | 'read' | 'new') => {
    if (!paper) return
    console.log('[PaperDetail] Updating status:', newStatus)
    try {
      const updated = await updatePaper(paper.id, { status: newStatus })
      setPaper(updated)
    } catch (e) {
      console.error('[PaperDetail] Failed to update status:', e)
    }
  }

  const handleSaveNotes = async () => {
    if (!paper) return
    console.log('[PaperDetail] Saving notes...')
    setSavingNotes(true)
    try {
      const updated = await updatePaper(paper.id, { notes })
      setPaper(updated)
    } catch (e) {
      console.error('[PaperDetail] Failed to save notes:', e)
    } finally {
      setSavingNotes(false)
    }
  }

  const handleCopyBibtex = async () => {
    if (!paper) return
    try {
      const bibtex = await fetchBibtex(paper.id)
      await navigator.clipboard.writeText(bibtex)
      setCopiedBibtex(true)
      setTimeout(() => setCopiedBibtex(false), 2000)
    } catch (e) {
      console.error('[PaperDetail] Failed to copy bibtex:', e)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !paper) {
    return (
      <div className="space-y-4">
        <Link to="/papers" className="flex items-center gap-2 text-blue-600 hover:underline">
          <ArrowLeft size={20} /> Back to papers
        </Link>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'Paper not found'}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <Link to="/papers" className="flex items-center gap-2 text-blue-600 hover:underline">
          <ArrowLeft size={20} /> Back to papers
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleStatusChange(paper.status === 'starred' ? 'new' : 'starred')}
            className={`p-2 rounded-lg transition-colors ${
              paper.status === 'starred' 
                ? 'bg-yellow-100 text-yellow-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={paper.status === 'starred' ? 'Unstar' : 'Star'}
          >
            {paper.status === 'starred' ? <Star size={20} fill="currentColor" /> : <StarOff size={20} />}
          </button>
          <button
            onClick={() => handleStatusChange(paper.status === 'read' ? 'new' : 'read')}
            className={`p-2 rounded-lg transition-colors ${
              paper.status === 'read' 
                ? 'bg-green-100 text-green-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={paper.status === 'read' ? 'Mark unread' : 'Mark read'}
          >
            <Eye size={20} />
          </button>
          <a
            href={paper.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            title="View PDF"
          >
            <ExternalLink size={20} />
          </a>
          <button
            onClick={handleCopyBibtex}
            className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            title="Copy BibTeX"
          >
            {copiedBibtex ? <Check size={20} className="text-green-600" /> : <Copy size={20} />}
          </button>
        </div>
      </div>

      {/* Paper info */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
            {paper.primary_category}
          </span>
          <span className="text-xs text-gray-500 ml-2">
            arXiv:{paper.arxiv_id}
          </span>
          {paper.has_placeholder_summary && (
            <span className="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded flex items-center gap-1 inline-flex">
              <AlertCircle size={12} />
              Placeholder content - will be filled when LLM is available
            </span>
          )}
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-4">{paper.title}</h1>
        
        <p className="text-gray-600 mb-4">
          {paper.authors.join(', ')}
        </p>
        
        <div className="text-sm text-gray-500 mb-4">
          Published: {paper.published ? new Date(paper.published).toLocaleDateString() : 'N/A'}
          {paper.updated && ` • Updated: ${new Date(paper.updated).toLocaleDateString()}`}
        </div>

        {/* Keywords */}
        {paper.keywords.length > 0 && !paper.has_placeholder_keywords && (
          <div className="flex flex-wrap gap-2 mb-4">
            {paper.keywords.map((keyword, i) => (
              <span key={i} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                {keyword}
              </span>
            ))}
          </div>
        )}

        {/* Manual tags */}
        {paper.manual_tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {paper.manual_tags.map((tag, i) => (
              <span key={i} className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Abstract */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">Abstract</h3>
          <p className="text-gray-700 whitespace-pre-line">{paper.abstract}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {[
              { id: 'summary', label: 'Summary' },
              { id: 'similar', label: 'Similar Papers' },
              { id: 'contra', label: 'Contra Papers' },
              { id: 'graph', label: 'Relationship Graph' },
              { id: 'full', label: 'Full Text' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Summary tab */}
          {activeTab === 'summary' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Generated Summary</h3>
                {paper.has_placeholder_summary ? (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-700">
                    <div className="flex items-center gap-2">
                      <AlertCircle size={20} />
                      <span>Summary will be generated when LLM becomes available.</span>
                    </div>
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-li:text-gray-700 prose-strong:text-gray-800">
                    <ReactMarkdown>{paper.summary}</ReactMarkdown>
                  </div>
                )}
              </div>

              {/* Questions Answered */}
              {paper.questions_answered && paper.questions_answered.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Questions This Paper Answers</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {paper.questions_answered.map((question, i) => (
                      <li key={i} className="text-gray-700">{question}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Theories Supported */}
              {paper.theories_supported && paper.theories_supported.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Theories This Paper Supports</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {paper.theories_supported.map((theory, i) => (
                      <li key={i} className="text-gray-700">{theory}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Notes */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Your Notes</h3>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add your notes about this paper..."
                  className="w-full h-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <div className="flex justify-end mt-2">
                  <button
                    onClick={handleSaveNotes}
                    disabled={savingNotes}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {savingNotes ? 'Saving...' : 'Save Notes'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Similar papers tab */}
          {activeTab === 'similar' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Similar Papers (by embedding similarity)</h3>
              {similarPapers.length === 0 ? (
                <p className="text-gray-500">No similar papers found.</p>
              ) : (
                <div className="space-y-3">
                  {similarPapers.map((similar) => (
                    <Link
                      key={similar.paper.id}
                      to={`/papers/${similar.paper.id}`}
                      className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-blue-600 hover:underline">
                            {similar.paper.title}
                          </h4>
                          <p className="text-sm text-gray-500 mt-1">
                            {similar.paper.authors.slice(0, 3).join(', ')}
                          </p>
                        </div>
                        <div className="text-sm text-gray-500">
                          {(similar.score * 100).toFixed(0)}% similar
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}

              {/* Related papers from graph */}
              {relatedPapers.length > 0 && (
                <div className="mt-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Related Papers (from knowledge graph)</h3>
                  <div className="space-y-3">
                    {relatedPapers.map((related) => (
                      <Link
                        key={related.paper_id}
                        to={`/papers/${related.paper_id}`}
                        className="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-blue-600 hover:underline">
                              {related.title}
                            </h4>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                {related.relationship_type}
                              </span>
                              <span className="text-xs text-gray-500">
                                {related.category}
                              </span>
                            </div>
                          </div>
                          <div className="text-sm text-gray-500">
                            {(related.weight * 100).toFixed(0)}% weight
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Contra Papers tab */}
          {activeTab === 'contra' && (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Contra Papers (opposing theories)</h3>
              <p className="text-sm text-gray-600">
                Papers that argue against or present alternative views to the theories supported by this paper.
              </p>
              {contraPapers.length === 0 ? (
                <p className="text-gray-500">No contra papers found. This may be because no opposing theories have been identified yet.</p>
              ) : (
                <div className="space-y-3">
                  {contraPapers.map((contra) => (
                    <Link
                      key={contra.paper.id}
                      to={`/papers/${contra.paper.id}`}
                      className="block p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors border border-red-200"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-red-700 hover:underline">
                            {contra.paper.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            <span className="font-medium">Opposing theory:</span> {contra.theory}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {contra.reason}
                          </p>
                        </div>
                        <div className="text-sm text-red-600 font-medium">
                          {(contra.relevance_score * 100).toFixed(0)}% relevant
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Graph tab */}
          {activeTab === 'graph' && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Network size={20} />
                Knowledge Graph
              </h3>
              {graphData && graphData.nodes.length > 0 ? (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    This paper is connected to {graphData.nodes.length - 1} other papers through {graphData.edges.length} relationships.
                  </p>
                  
                  {/* Simple graph visualization */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <div className="flex flex-wrap gap-4 justify-center">
                      {graphData.nodes.map((node) => (
                        <Link
                          key={node.id}
                          to={`/papers/${node.id}`}
                          className={`
                            p-4 rounded-lg max-w-[200px] text-center transition-colors
                            ${node.is_center 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-white border border-gray-200 hover:border-blue-300'
                            }
                          `}
                        >
                          <div className={`text-sm font-medium line-clamp-2 ${node.is_center ? 'text-white' : 'text-gray-900'}`}>
                            {node.title}
                          </div>
                          <div className={`text-xs mt-1 ${node.is_center ? 'text-blue-200' : 'text-gray-500'}`}>
                            {node.category}
                          </div>
                        </Link>
                      ))}
                    </div>
                    
                    {/* Edge legend */}
                    {graphData.edges.length > 0 && (
                      <div className="mt-6 flex flex-wrap gap-4 justify-center text-sm text-gray-600">
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                          Author connection
                        </span>
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                          Similar topic
                        </span>
                        <span className="flex items-center gap-2">
                          <span className="w-3 h-3 bg-purple-500 rounded-full"></span>
                          Citation
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No graph data available for this paper.</p>
              )}
            </div>
          )}

          {/* Full text tab */}
          {activeTab === 'full' && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Full Text (extracted from PDF)</h3>
              {paper.full_text ? (
                <div className="bg-gray-50 rounded-lg p-4 max-h-[600px] overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                    {paper.full_text}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-500">Full text not available.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
