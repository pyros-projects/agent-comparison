import { useState, useEffect } from 'react'
import { 
  Download, 
  Play, 
  Square, 
  Trash2, 
  Plus,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader,
  ChevronDown,
  ChevronUp,
  FileText,
} from 'lucide-react'
import { 
  fetchImportTasks, 
  createImportTask, 
  startImportTask, 
  stopImportTask, 
  deleteImportTask,
  fetchArxivCategories,
  fetchImportTaskDetail,
  ImportTaskDetail,
} from '../api'
import { ImportTask, ImportTaskCreate } from '../types'
import { useWebSocket } from '../context/WebSocketContext'

export default function ImportTasks() {
  const [tasks, setTasks] = useState<ImportTask[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  
  // Expanded task details
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null)
  const [taskDetail, setTaskDetail] = useState<ImportTaskDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  
  // Create task modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newTask, setNewTask] = useState<ImportTaskCreate>({
    name: '',
    category: '',
    semantic_query: '',
    text_search: '',
    check_interval: 60,
  })
  const [creating, setCreating] = useState(false)
  
  // Task status from WebSocket
  const [taskStatuses, setTaskStatuses] = useState<Record<string, string>>({})
  
  const { subscribe } = useWebSocket()

  const loadTasks = async () => {
    console.log('[ImportTasks] Loading tasks...')
    try {
      const { tasks: taskList } = await fetchImportTasks()
      setTasks(taskList)
      setError(null)
      console.log('[ImportTasks] Loaded', taskList.length, 'tasks')
    } catch (e) {
      console.error('[ImportTasks] Failed to load tasks:', e)
      setError('Failed to load import tasks')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTasks()
    
    // Load categories
    fetchArxivCategories().then(data => setCategories(data.categories)).catch(console.error)
    
    // Subscribe to WebSocket updates
    const unsubscribe = subscribe((message) => {
      if (message.type === 'import_status') {
        const taskId = message.task_id as string
        const status = message.status as string
        console.log('[ImportTasks] Status update:', taskId, status)
        setTaskStatuses(prev => ({ ...prev, [taskId]: status }))
      }
      if (message.type === 'paper_imported') {
        console.log('[ImportTasks] Paper imported, refreshing...')
        loadTasks()
        // Also refresh expanded detail if relevant
        if (expandedTaskId) {
          loadTaskDetail(expandedTaskId)
        }
      }
      if (message.type === 'import_log') {
        // Refresh detail if viewing the task
        const taskId = message.task_id as string
        if (expandedTaskId === taskId) {
          loadTaskDetail(taskId)
        }
      }
    })
    
    return unsubscribe
  }, [subscribe, expandedTaskId])

  const loadTaskDetail = async (taskId: string) => {
    setLoadingDetail(true)
    try {
      const detail = await fetchImportTaskDetail(taskId)
      setTaskDetail(detail)
    } catch (e) {
      console.error('[ImportTasks] Failed to load task detail:', e)
    } finally {
      setLoadingDetail(false)
    }
  }

  const toggleTaskExpansion = async (taskId: string) => {
    if (expandedTaskId === taskId) {
      // Collapse
      setExpandedTaskId(null)
      setTaskDetail(null)
    } else {
      // Expand and load detail
      setExpandedTaskId(taskId)
      await loadTaskDetail(taskId)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTask.name) return
    
    console.log('[ImportTasks] Creating task:', newTask)
    setCreating(true)
    
    try {
      const task = await createImportTask(newTask)
      setTasks([task, ...tasks])
      setShowCreateModal(false)
      setNewTask({
        name: '',
        category: '',
        semantic_query: '',
        text_search: '',
        check_interval: 60,
      })
    } catch (e) {
      console.error('[ImportTasks] Failed to create task:', e)
    } finally {
      setCreating(false)
    }
  }

  const handleStart = async (taskId: string) => {
    console.log('[ImportTasks] Starting task:', taskId)
    try {
      await startImportTask(taskId)
      setTasks(tasks.map(t => t.id === taskId ? { ...t, is_active: true } : t))
    } catch (e) {
      console.error('[ImportTasks] Failed to start task:', e)
    }
  }

  const handleStop = async (taskId: string) => {
    console.log('[ImportTasks] Stopping task:', taskId)
    try {
      await stopImportTask(taskId)
      setTasks(tasks.map(t => t.id === taskId ? { ...t, is_active: false } : t))
    } catch (e) {
      console.error('[ImportTasks] Failed to stop task:', e)
    }
  }

  const handleDelete = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this import task?')) return
    
    console.log('[ImportTasks] Deleting task:', taskId)
    try {
      await deleteImportTask(taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (e) {
      console.error('[ImportTasks] Failed to delete task:', e)
    }
  }

  const getStatusDisplay = (task: ImportTask) => {
    const status = taskStatuses[task.id]
    
    if (!task.is_active) {
      return (
        <span className="flex items-center gap-1 text-gray-500">
          <Square size={14} />
          Stopped
        </span>
      )
    }
    
    if (status?.startsWith('importing:')) {
      const paperId = status.split(':')[1]
      return (
        <span className="flex items-center gap-1 text-blue-600">
          <Loader size={14} className="animate-spin" />
          Importing {paperId}...
        </span>
      )
    }
    
    if (status === 'checking') {
      return (
        <span className="flex items-center gap-1 text-blue-600">
          <Loader size={14} className="animate-spin" />
          Checking for new papers...
        </span>
      )
    }
    
    return (
      <span className="flex items-center gap-1 text-green-600">
        <CheckCircle size={14} />
        Running
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Download className="text-orange-600" size={32} />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Continuous Imports</h1>
            <p className="text-gray-600">
              Configure automatic paper discovery from arXiv.
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          New Import Task
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Task list */}
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-12 text-center">
            <Download className="text-gray-300 mx-auto mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-700 mb-2">
              No Import Tasks
            </h3>
            <p className="text-gray-500 max-w-md mx-auto mb-4">
              Create an import task to automatically discover and ingest papers from arXiv.
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create First Task
            </button>
          </div>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="bg-white rounded-lg shadow overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{task.name}</h3>
                      {getStatusDisplay(task)}
                    </div>
                    
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {task.category && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Category:</span>
                          <span className="bg-gray-100 px-2 py-0.5 rounded">{task.category}</span>
                        </span>
                      )}
                      {task.semantic_query && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Semantic:</span>
                          <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded truncate max-w-[200px]">
                            {task.semantic_query}
                          </span>
                        </span>
                      )}
                      {task.text_search && (
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Text:</span>
                          <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                            {task.text_search}
                          </span>
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        Every {task.check_interval}s
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-6 mt-3 text-sm">
                      <span className="text-gray-600">
                        <span className="font-medium text-green-600">{task.papers_imported}</span> papers imported
                      </span>
                      {task.errors > 0 && (
                        <span className="text-red-600 flex items-center gap-1">
                          <AlertCircle size={14} />
                          {task.errors} errors
                        </span>
                      )}
                      {task.last_run && (
                        <span className="text-gray-500">
                          Last run: {new Date(task.last_run).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toggleTaskExpansion(task.id)}
                      className={`p-2 rounded-lg transition-colors ${
                        expandedTaskId === task.id 
                          ? 'bg-blue-100 text-blue-700' 
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                      title={expandedTaskId === task.id ? 'Collapse' : 'View logs'}
                    >
                      {expandedTaskId === task.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                    </button>
                    {task.is_active ? (
                      <button
                        onClick={() => handleStop(task.id)}
                        className="p-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-colors"
                        title="Stop"
                      >
                        <Square size={20} />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleStart(task.id)}
                        className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                        title="Start"
                      >
                        <Play size={20} />
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(task.id)}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Expanded detail section */}
              {expandedTaskId === task.id && (
                <div className="border-t border-gray-200 bg-gray-50 p-6">
                  {loadingDetail ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader className="animate-spin text-blue-600" size={24} />
                    </div>
                  ) : taskDetail ? (
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Logs section */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                          <FileText size={16} />
                          Task Logs ({taskDetail.logs.length})
                        </h4>
                        <div className="bg-gray-900 rounded-lg p-4 max-h-80 overflow-y-auto font-mono text-sm">
                          {taskDetail.logs.length === 0 ? (
                            <p className="text-gray-500 italic">No logs yet. Start the task to see activity.</p>
                          ) : (
                            taskDetail.logs.slice().reverse().map((log, idx) => (
                              <div key={idx} className="mb-2 last:mb-0">
                                <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                {' '}
                                <span className={`uppercase font-bold ${
                                  log.level === 'error' ? 'text-red-400' :
                                  log.level === 'warning' ? 'text-yellow-400' :
                                  log.level === 'info' ? 'text-blue-400' :
                                  'text-gray-400'
                                }`}>
                                  [{log.level}]
                                </span>
                                {' '}
                                <span className="text-gray-200">{log.message}</span>
                                {log.details && Object.keys(log.details).length > 0 && (
                                  <pre className="text-gray-500 text-xs mt-1 ml-4 overflow-x-auto">
                                    {JSON.stringify(log.details, null, 2)}
                                  </pre>
                                )}
                              </div>
                            ))
                          )}
                        </div>
                      </div>
                      
                      {/* Imported papers section */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                          <Download size={16} />
                          Recently Imported Papers ({taskDetail.imported_papers.length})
                        </h4>
                        <div className="bg-white rounded-lg border border-gray-200 max-h-80 overflow-y-auto">
                          {taskDetail.imported_papers.length === 0 ? (
                            <p className="text-gray-500 italic p-4">No papers imported by this task yet.</p>
                          ) : (
                            <ul className="divide-y divide-gray-100">
                              {taskDetail.imported_papers.slice().reverse().map((paper, idx) => (
                                <li key={idx} className="p-3 hover:bg-gray-50">
                                  <a 
                                    href={`/papers/${paper.paper_id}`}
                                    className="text-blue-600 hover:text-blue-800 font-medium text-sm line-clamp-2"
                                  >
                                    {paper.title}
                                  </a>
                                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                    <span className="bg-gray-100 px-1.5 py-0.5 rounded">{paper.arxiv_id}</span>
                                    <span className="bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded">{paper.category}</span>
                                    <span>{new Date(paper.imported_at).toLocaleString()}</span>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">Failed to load task details.</p>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Create modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Create Import Task</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task Name *
                </label>
                <input
                  type="text"
                  value={newTask.name}
                  onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                  placeholder="e.g., AI/ML Papers"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  arXiv Category
                </label>
                <select
                  value={newTask.category || ''}
                  onChange={(e) => setNewTask({ ...newTask, category: e.target.value || undefined })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Semantic Query (optional)
                </label>
                <input
                  type="text"
                  value={newTask.semantic_query || ''}
                  onChange={(e) => setNewTask({ ...newTask, semantic_query: e.target.value || undefined })}
                  placeholder="e.g., transformer architectures for NLP"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Papers will be filtered by semantic similarity to this query.
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Text Search (optional)
                </label>
                <input
                  type="text"
                  value={newTask.text_search || ''}
                  onChange={(e) => setNewTask({ ...newTask, text_search: e.target.value || undefined })}
                  placeholder="e.g., GPT language model"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Check Interval (seconds)
                </label>
                <input
                  type="number"
                  value={newTask.check_interval}
                  onChange={(e) => setNewTask({ ...newTask, check_interval: parseInt(e.target.value) || 60 })}
                  min={30}
                  max={3600}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  How often to check for new papers (30-3600 seconds).
                </p>
              </div>
              
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newTask.name || creating}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {creating && <Loader className="animate-spin" size={16} />}
                  {creating ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
