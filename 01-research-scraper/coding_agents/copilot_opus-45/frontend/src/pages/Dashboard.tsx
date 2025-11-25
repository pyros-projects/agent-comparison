import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  ZAxis,
} from 'recharts'
import { 
  FileText, 
  HardDrive, 
  Calendar, 
  Download, 
  AlertCircle,
  TrendingUp,
  Clock,
  Cloud,
  Network,
  RefreshCw,
  Settings,
  Loader,
} from 'lucide-react'
import { 
  fetchDashboard, 
  fetchKeywords, 
  fetchEmbeddingClusters,
  reprocessQuestionsTheories,
  reprocessKeywords,
  reprocessRelationships,
  reprocessEmbeddings,
  ReprocessResponse,
} from '../api'
import { DashboardResponse, KeywordCount, EmbeddingClusterPoint } from '../types'
import { useWebSocket } from '../context/WebSocketContext'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

// Category to color mapping for scatter plot
const CATEGORY_COLORS: Record<string, string> = {
  'cs.AI': '#3B82F6',
  'cs.CL': '#10B981',
  'cs.CV': '#F59E0B',
  'cs.LG': '#EF4444',
  'cs.NE': '#8B5CF6',
  'cs.RO': '#EC4899',
  'stat.ML': '#06B6D4',
  'cs.IR': '#84CC16',
  'cs.SE': '#F97316',
  'cs.DB': '#14B8A6',
  'q-bio.QM': '#A855F7',
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [keywords, setKeywords] = useState<KeywordCount[]>([])
  const [embeddingClusters, setEmbeddingClusters] = useState<EmbeddingClusterPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reprocessing, setReprocessing] = useState<string | null>(null)
  const [reprocessResult, setReprocessResult] = useState<ReprocessResponse | null>(null)
  const { subscribe } = useWebSocket()

  const loadData = async () => {
    console.log('[Dashboard] Loading data...')
    try {
      const [result, kw, clusters] = await Promise.all([
        fetchDashboard(),
        fetchKeywords(),
        fetchEmbeddingClusters(),
      ])
      setData(result)
      setKeywords(kw)
      setEmbeddingClusters(clusters)
      setError(null)
      console.log('[Dashboard] Data loaded:', result)
    } catch (e) {
      console.error('[Dashboard] Failed to load data:', e)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    
    // Subscribe to WebSocket updates
    const unsubscribe = subscribe((message) => {
      if (message.type === 'paper_imported' || message.type === 'backfill_complete') {
        console.log('[Dashboard] Refreshing due to:', message.type)
        loadData()
      }
    })
    
    return unsubscribe
  }, [subscribe])

  const handleReprocess = async (type: string) => {
    setReprocessing(type)
    setReprocessResult(null)
    try {
      let result: ReprocessResponse
      switch (type) {
        case 'questions':
          result = await reprocessQuestionsTheories(undefined, false)
          break
        case 'keywords':
          result = await reprocessKeywords(undefined, false)
          break
        case 'relationships':
          result = await reprocessRelationships(true)
          break
        case 'embeddings':
          result = await reprocessEmbeddings(undefined, false)
          break
        default:
          throw new Error('Unknown reprocess type')
      }
      setReprocessResult(result)
      // Reload data after reprocessing
      await loadData()
    } catch (e) {
      console.error('[Dashboard] Reprocess error:', e)
      setReprocessResult({
        processed: 0,
        skipped: 0,
        errors: 1,
        message: e instanceof Error ? e.message : 'Unknown error',
      })
    } finally {
      setReprocessing(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error || 'No data available'}
      </div>
    )
  }

  const categoryData = Object.entries(data.stats.papers_by_category).map(([name, value]) => ({
    name,
    value,
  }))

  // Prepare embedding cluster data for scatter plot
  const clusterData = embeddingClusters.map(p => ({
    ...p,
    x: p.x * 100,
    y: p.y * 100,
    z: 10,
    color: CATEGORY_COLORS[p.category] || '#6B7280',
  }))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Status alerts */}
      {!data.stats.llm_available && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-yellow-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-medium text-yellow-800">LLM Unavailable</h3>
            <p className="text-yellow-700 text-sm">
              Papers will be ingested with placeholders. Theory Mode is disabled.
              {data.stats.papers_with_placeholders > 0 && (
                <span className="block mt-1">
                  {data.stats.papers_with_placeholders} papers have placeholder content waiting for backfill.
                </span>
              )}
            </p>
          </div>
        </div>
      )}

      {data.stats.embedding_using_fallback && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-blue-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-medium text-blue-800">Using Fallback Embeddings</h3>
            <p className="text-blue-700 text-sm">
              Using sentence-transformers for embeddings. Search functionality is fully available.
            </p>
          </div>
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Papers</p>
              <p className="text-3xl font-bold text-gray-900">{data.stats.total_papers}</p>
            </div>
            <FileText className="text-blue-500" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Storage Size</p>
              <p className="text-3xl font-bold text-gray-900">{data.stats.storage_size_mb} MB</p>
            </div>
            <HardDrive className="text-green-500" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Papers This Week</p>
              <p className="text-3xl font-bold text-gray-900">{data.stats.papers_this_week}</p>
              <p className="text-sm text-gray-400">{data.stats.papers_today} today</p>
            </div>
            <Calendar className="text-purple-500" size={40} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Active Imports</p>
              <p className="text-3xl font-bold text-gray-900">{data.stats.active_import_tasks}</p>
            </div>
            <Download className="text-orange-500" size={40} />
          </div>
        </div>
      </div>

      {/* Word Cloud and Category Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Word Cloud */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Cloud size={20} />
            Keyword Cloud
          </h2>
          {keywords.length > 0 ? (
            <div className="h-[300px] flex flex-wrap items-center justify-center gap-2 overflow-hidden">
              {keywords.slice(0, 50).map((kw, index) => {
                // Scale font size based on count
                const maxCount = keywords[0]?.count || 1
                const scale = Math.max(0.6, Math.min(2.5, (kw.count / maxCount) * 2 + 0.5))
                const color = COLORS[index % COLORS.length]
                
                return (
                  <span
                    key={kw.keyword}
                    className="cursor-default hover:opacity-80 transition-opacity px-1"
                    style={{
                      fontSize: `${scale}rem`,
                      color: color,
                      fontWeight: scale > 1.2 ? 600 : 400,
                    }}
                    title={`${kw.keyword}: ${kw.count} papers`}
                  >
                    {kw.keyword}
                  </span>
                )
              })}
            </div>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No keywords yet
            </div>
          )}
        </div>

        {/* Category distribution pie chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Category Distribution</h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[entry.name] || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[300px] flex items-center justify-center text-gray-500">
              No papers yet
            </div>
          )}
        </div>
      </div>

      {/* Embedding Clusters Visualization */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Network size={20} />
          Semantic Paper Clusters
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Papers positioned by semantic similarity - closer papers share similar topics
        </p>
        {clusterData.length > 0 ? (
          <div>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" dataKey="x" name="x" hide />
                <YAxis type="number" dataKey="y" name="y" hide />
                <ZAxis type="number" dataKey="z" range={[60, 200]} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload as EmbeddingClusterPoint
                      return (
                        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 max-w-xs">
                          <p className="font-medium text-gray-900 text-sm line-clamp-2">{data.title}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            <span className="bg-gray-100 px-1.5 py-0.5 rounded">{data.category}</span>
                          </p>
                          {data.keywords.length > 0 && (
                            <p className="text-xs text-gray-400 mt-1">
                              {data.keywords.slice(0, 3).join(', ')}
                            </p>
                          )}
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Scatter
                  data={clusterData}
                  fill="#8884d8"
                  shape={(props: any) => {
                    const { cx, cy, payload } = props
                    return (
                      <Link to={`/papers/${payload.paper_id}`}>
                        <circle
                          cx={cx}
                          cy={cy}
                          r={8}
                          fill={payload.color}
                          fillOpacity={0.7}
                          stroke={payload.color}
                          strokeWidth={2}
                          className="cursor-pointer hover:fill-opacity-100 transition-all"
                        />
                      </Link>
                    )
                  }}
                />
              </ScatterChart>
            </ResponsiveContainer>
            {/* Legend */}
            <div className="flex flex-wrap justify-center gap-4 mt-4">
              {Object.entries(CATEGORY_COLORS).slice(0, 8).map(([cat, color]) => (
                <div key={cat} className="flex items-center gap-1.5 text-xs">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-gray-600">{cat}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="h-[400px] flex items-center justify-center text-gray-500">
            Need at least 2 papers for cluster visualization
          </div>
        )}
      </div>

      {/* Growth chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp size={20} />
          Collection Growth (Last 7 Days)
        </h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data.growth_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Maintenance & Reprocessing */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Settings size={20} />
          Data Maintenance
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Retroactively process existing papers to update features that were added after import.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Questions & Theories */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Questions & Theories</h3>
            <p className="text-sm text-gray-500 mb-3">
              Extract "Questions Answered" and "Theories Supported" from papers using LLM analysis.
            </p>
            <button
              onClick={() => handleReprocess('questions')}
              disabled={reprocessing !== null}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {reprocessing === 'questions' ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Extract Q&T
                </>
              )}
            </button>
          </div>

          {/* Keyword Normalization */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Keyword Normalization</h3>
            <p className="text-sm text-gray-500 mb-3">
              Normalize keywords across papers to merge similar terms (e.g., "LLM" vs "Large Language Model").
            </p>
            <button
              onClick={() => handleReprocess('keywords')}
              disabled={reprocessing !== null}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {reprocessing === 'keywords' ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Normalize Keywords
                </>
              )}
            </button>
          </div>

          {/* Relationship Graph */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Relationship Graph</h3>
            <p className="text-sm text-gray-500 mb-3">
              Rebuild knowledge graph connections based on shared keywords between papers.
            </p>
            <button
              onClick={() => handleReprocess('relationships')}
              disabled={reprocessing !== null}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {reprocessing === 'relationships' ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Rebuild Graph
                </>
              )}
            </button>
          </div>

          {/* Embeddings */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Embeddings</h3>
            <p className="text-sm text-gray-500 mb-3">
              Regenerate embeddings for papers missing them. Affects cluster visualization and similarity search.
            </p>
            <button
              onClick={() => handleReprocess('embeddings')}
              disabled={reprocessing !== null}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {reprocessing === 'embeddings' ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Generate Embeddings
                </>
              )}
            </button>
          </div>
        </div>

        {/* Reprocess result */}
        {reprocessResult && (
          <div className={`mt-4 p-4 rounded-lg ${
            reprocessResult.errors > 0 
              ? 'bg-yellow-50 border border-yellow-200' 
              : 'bg-green-50 border border-green-200'
          }`}>
            <p className={reprocessResult.errors > 0 ? 'text-yellow-700' : 'text-green-700'}>
              {reprocessResult.message}
            </p>
            <div className="flex gap-4 mt-2 text-sm">
              <span className="text-green-600">Processed: {reprocessResult.processed}</span>
              <span className="text-gray-500">Skipped: {reprocessResult.skipped}</span>
              {reprocessResult.errors > 0 && (
                <span className="text-red-600">Errors: {reprocessResult.errors}</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Clock size={20} />
          Recent Activity
        </h2>
        {data.recent_activity.length > 0 ? (
          <div className="space-y-3 max-h-[400px] overflow-y-auto">
            {data.recent_activity.map((activity, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <Link 
                    to={`/papers/${activity.paper_id}`}
                    className="text-blue-600 hover:underline font-medium truncate block"
                  >
                    {activity.paper_title}
                  </Link>
                  <p className="text-sm text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                  {activity.action}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No recent activity
          </div>
        )}
      </div>
    </div>
  )
}
