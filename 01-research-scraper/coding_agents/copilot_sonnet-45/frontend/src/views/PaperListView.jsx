import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { papersAPI } from '../api'

export default function PaperListView() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ status: '', category: '', text: '' })
  const [arxivUrl, setArxivUrl] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    console.log('PaperListView: Component mounted')
    loadPapers()
  }, [])

  const loadPapers = async () => {
    try {
      console.log('PaperListView: Loading papers with filters:', filter)
      setLoading(true)
      const params = {}
      if (filter.status) params.status = filter.status
      if (filter.category) params.category = filter.category
      if (filter.text) params.text_query = filter.text
      
      const data = await papersAPI.getAll(params)
      console.log(`PaperListView: Loaded ${data.length} papers`)
      setPapers(data)
    } catch (error) {
      console.error('PaperListView: Error loading papers:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = setTimeout(loadPapers, 500)
    return () => clearTimeout(timeoutId)
  }, [filter])

  const handleIngest = async () => {
    if (!arxivUrl.trim()) return
    
    console.log('PaperListView: Starting ingestion for:', arxivUrl)
    setIngesting(true)
    
    try {
      await papersAPI.ingest(arxivUrl)
      setArxivUrl('')
      setTimeout(loadPapers, 2000)
    } catch (error) {
      console.error('PaperListView: Ingestion error:', error)
      alert('Failed to ingest paper: ' + error.message)
    } finally {
      setIngesting(false)
    }
  }

  const handleStatusChange = async (paperId, newStatus) => {
    console.log(`PaperListView: Updating paper ${paperId} status to ${newStatus}`)
    try {
      await papersAPI.update(paperId, { status: newStatus })
      loadPapers()
    } catch (error) {
      console.error('PaperListView: Status update error:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString()
  }

  return (
    <div>
      <div className="view-header">
        <h2 className="view-title">📚 Paper Catalog</h2>
        <p className="view-subtitle">Browse and manage your research paper collection</p>
      </div>

      <div className="card">
        <h3 className="card-title">Add New Paper</h3>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <input
            type="text"
            className="input"
            placeholder="Enter arXiv URL or ID (e.g., 2103.12345)"
            value={arxivUrl}
            onChange={(e) => setArxivUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleIngest()}
          />
          <button 
            className="btn btn-primary" 
            onClick={handleIngest}
            disabled={ingesting}
          >
            {ingesting ? 'Ingesting...' : '+ Add Paper'}
          </button>
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Filters</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
          <input
            type="text"
            className="input"
            placeholder="Search title/abstract..."
            value={filter.text}
            onChange={(e) => setFilter({ ...filter, text: e.target.value })}
          />
          <select
            className="input"
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="read">Read</option>
            <option value="starred">Starred</option>
          </select>
          <input
            type="text"
            className="input"
            placeholder="Category (e.g., cs.AI)"
            value={filter.category}
            onChange={(e) => setFilter({ ...filter, category: e.target.value })}
          />
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Papers ({papers.length})</h3>
        {loading ? (
          <div className="loading">Loading papers...</div>
        ) : papers.length === 0 ? (
          <div className="empty-state">
            <h3>No papers yet</h3>
            <p>Add your first paper using an arXiv URL above</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Authors</th>
                <th>Date</th>
                <th>Categories</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {papers.map((paper) => (
                <tr key={paper.id}>
                  <td>
                    <a 
                      href="#" 
                      onClick={(e) => { e.preventDefault(); navigate(`/papers/${paper.id}`) }}
                      style={{ color: '#667eea', fontWeight: 500 }}
                    >
                      {paper.title}
                    </a>
                  </td>
                  <td style={{ fontSize: '0.875rem', color: '#718096' }}>
                    {paper.authors.slice(0, 3).map(a => a.name).join(', ')}
                    {paper.authors.length > 3 && ` +${paper.authors.length - 3}`}
                  </td>
                  <td style={{ fontSize: '0.875rem' }}>{formatDate(paper.published)}</td>
                  <td>
                    {paper.categories.slice(0, 2).map(cat => (
                      <span key={cat} style={{ 
                        fontSize: '0.75rem',
                        background: '#edf2f7',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        marginRight: '0.25rem'
                      }}>
                        {cat}
                      </span>
                    ))}
                  </td>
                  <td>
                    <span className={`badge badge-${paper.status}`}>
                      {paper.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                        onClick={() => handleStatusChange(paper.id, 'starred')}
                      >
                        ⭐
                      </button>
                      <button
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                        onClick={() => handleStatusChange(paper.id, 'read')}
                      >
                        ✓
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
