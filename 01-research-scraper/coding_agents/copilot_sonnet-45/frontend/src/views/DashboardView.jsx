import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { dashboardAPI, tasksAPI } from '../api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function DashboardView() {
  const [stats, setStats] = useState(null)
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [newTaskName, setNewTaskName] = useState('')
  const [newTaskCategory, setNewTaskCategory] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    console.log('DashboardView: Component mounted')
    loadData()
  }, [])

  const loadData = async () => {
    try {
      console.log('DashboardView: Loading dashboard data...')
      setLoading(true)
      const [statsData, tasksData] = await Promise.all([
        dashboardAPI.getStats(),
        tasksAPI.getAll()
      ])
      console.log('DashboardView: Data loaded:', { stats: statsData, tasks: tasksData.length })
      setStats(statsData)
      setTasks(tasksData)
    } catch (error) {
      console.error('DashboardView: Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTask = async () => {
    if (!newTaskName.trim()) return
    
    console.log('DashboardView: Creating task:', newTaskName)
    try {
      const taskData = {
        name: newTaskName,
        filters: newTaskCategory ? { arxiv_categories: [newTaskCategory] } : {},
        check_interval_seconds: 300,
        max_results_per_check: 10,
        start_immediately: true
      }
      
      await tasksAPI.create(taskData)
      setNewTaskName('')
      setNewTaskCategory('')
      loadData()
    } catch (error) {
      console.error('DashboardView: Error creating task:', error)
      alert('Failed to create task: ' + error.message)
    }
  }

  const toggleTask = async (taskId, isActive) => {
    console.log(`DashboardView: ${isActive ? 'Stopping' : 'Starting'} task ${taskId}`)
    try {
      if (isActive) {
        await tasksAPI.stop(taskId)
      } else {
        await tasksAPI.start(taskId)
      }
      loadData()
    } catch (error) {
      console.error('DashboardView: Error toggling task:', error)
    }
  }

  const deleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return
    
    console.log('DashboardView: Deleting task', taskId)
    try {
      await tasksAPI.delete(taskId)
      loadData()
    } catch (error) {
      console.error('DashboardView: Error deleting task:', error)
    }
  }

  if (loading || !stats) {
    return <div className="loading">Loading dashboard...</div>
  }

  // Prepare chart data
  const categoryData = Object.entries(stats.papers_by_category)
    .slice(0, 10)
    .map(([name, count]) => ({ name, count }))

  const statusData = Object.entries(stats.papers_by_status)
    .map(([name, count]) => ({ name, count }))

  const growthData = stats.collection_growth.reverse().map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    papers: item.count
  }))

  return (
    <div>
      <div className="view-header">
        <h2 className="view-title">📊 Dashboard</h2>
        <p className="view-subtitle">Overview of your research paper collection</p>
      </div>

      <div className="grid grid-4">
        <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '700' }}>{stats.total_papers}</div>
          <div style={{ opacity: 0.9 }}>Total Papers</div>
        </div>
        <div className="card" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '700' }}>{stats.papers_imported_today}</div>
          <div style={{ opacity: 0.9 }}>Papers Today</div>
        </div>
        <div className="card" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '700' }}>{stats.papers_imported_week}</div>
          <div style={{ opacity: 0.9 }}>Papers This Week</div>
        </div>
        <div className="card" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '700' }}>{stats.active_import_tasks}</div>
          <div style={{ opacity: 0.9 }}>Active Tasks</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Papers by Category</h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No data yet</div>
          )}
        </div>

        <div className="card">
          <h3 className="card-title">Collection Growth (7 Days)</h3>
          {growthData.some(d => d.papers > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={growthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="papers" stroke="#667eea" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No growth data yet</div>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Recent Papers</h3>
        {stats.recent_papers.length === 0 ? (
          <div className="empty-state">No papers yet</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {stats.recent_papers.map((paper) => (
              <div key={paper.id} style={{ 
                padding: '1rem', 
                background: '#f7fafc', 
                borderRadius: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ flex: 1 }}>
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); navigate(`/papers/${paper.id}`) }}
                    style={{ color: '#667eea', fontWeight: '600' }}
                  >
                    {paper.title}
                  </a>
                  <div style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.25rem' }}>
                    {paper.authors.slice(0, 3).map(a => a.name).join(', ')}
                    {paper.authors.length > 3 && ` +${paper.authors.length - 3}`}
                  </div>
                </div>
                <span className={`badge badge-${paper.status}`}>
                  {paper.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">Continuous Import Tasks</h3>
        
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#f7fafc', borderRadius: '8px' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.75rem' }}>Create New Task</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '0.75rem' }}>
            <input
              type="text"
              className="input"
              placeholder="Task name (e.g., 'CS.AI Papers')"
              value={newTaskName}
              onChange={(e) => setNewTaskName(e.target.value)}
            />
            <input
              type="text"
              className="input"
              placeholder="Category (optional, e.g., cs.AI)"
              value={newTaskCategory}
              onChange={(e) => setNewTaskCategory(e.target.value)}
            />
            <button className="btn btn-primary" onClick={createTask}>
              + Create Task
            </button>
          </div>
        </div>

        {tasks.length === 0 ? (
          <div className="empty-state">
            <h3>No continuous import tasks</h3>
            <p>Create a task to automatically monitor arXiv for new papers</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Papers Imported</th>
                <th>Last Check</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id}>
                  <td>
                    <div style={{ fontWeight: '600' }}>{task.name}</div>
                    {task.filters.arxiv_categories && (
                      <div style={{ fontSize: '0.75rem', color: '#718096' }}>
                        Categories: {task.filters.arxiv_categories.join(', ')}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${task.is_active ? 'badge-read' : 'badge-new'}`}>
                      {task.is_active ? '▶ Running' : '⏸ Stopped'}
                    </span>
                  </td>
                  <td>{task.papers_imported}</td>
                  <td style={{ fontSize: '0.875rem', color: '#718096' }}>
                    {task.last_check ? new Date(task.last_check).toLocaleString() : 'Never'}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className={`btn ${task.is_active ? 'btn-secondary' : 'btn-success'}`}
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                        onClick={() => toggleTask(task.id, task.is_active)}
                      >
                        {task.is_active ? '⏸ Stop' : '▶ Start'}
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                        onClick={() => deleteTask(task.id)}
                      >
                        🗑
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="grid grid-3">
        <div className="card">
          <h3 className="card-title">Storage</h3>
          <div style={{ fontSize: '2rem', fontWeight: '700', color: '#667eea' }}>
            {stats.storage_size_mb.toFixed(2)} MB
          </div>
          <div style={{ color: '#718096', fontSize: '0.875rem' }}>Database size</div>
        </div>
        
        <div className="card">
          <h3 className="card-title">Papers by Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {statusData.map(({ name, count }) => (
              <div key={name} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span className={`badge badge-${name}`}>{name}</span>
                <span style={{ fontWeight: '600' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <button className="btn btn-primary" onClick={() => navigate('/papers')}>
              📚 View All Papers
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/theory')}>
              🔬 Theory Mode
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
