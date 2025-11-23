import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { papersAPI } from '../api'

export default function PaperDetailView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [paper, setPaper] = useState(null)
  const [similar, setSimilar] = useState([])
  const [related, setRelated] = useState([])
  const [graph, setGraph] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState('')

  useEffect(() => {
    console.log('PaperDetailView: Loading paper:', id)
    loadPaper()
  }, [id])

  const loadPaper = async () => {
    try {
      setLoading(true)
      console.log('PaperDetailView: Fetching paper data...')
      
      const [paperData, similarData, relatedData, graphData] = await Promise.all([
        papersAPI.getById(id),
        papersAPI.getSimilar(id),
        papersAPI.getRelated(id),
        papersAPI.getGraph(id)
      ])
      
      console.log('PaperDetailView: Paper loaded:', paperData.title)
      setPaper(paperData)
      setNotes(paperData.notes || '')
      setSimilar(similarData)
      setRelated(relatedData)
      setGraph(graphData)
    } catch (error) {
      console.error('PaperDetailView: Error loading paper:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveNotes = async () => {
    console.log('PaperDetailView: Saving notes...')
    try {
      await papersAPI.update(id, { notes })
      alert('Notes saved!')
    } catch (error) {
      console.error('PaperDetailView: Error saving notes:', error)
    }
  }

  const exportBibTeX = () => {
    if (!paper) return
    
    const bibtex = `@article{${paper.arxiv_id},
  title={${paper.title}},
  author={${paper.authors.map(a => a.name).join(' and ')}},
  journal={arXiv preprint arXiv:${paper.arxiv_id}},
  year={${new Date(paper.published).getFullYear()}}
}`
    
    const blob = new Blob([bibtex], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${paper.arxiv_id}.bib`
    a.click()
    console.log('PaperDetailView: BibTeX exported')
  }

  if (loading) {
    return <div className="loading">Loading paper...</div>
  }

  if (!paper) {
    return <div className="error">Paper not found</div>
  }

  return (
    <div>
      <div className="view-header">
        <button className="btn btn-secondary" onClick={() => navigate('/papers')}>
          ← Back to Papers
        </button>
      </div>

      <div className="card">
        <div style={{ marginBottom: '1rem' }}>
          <span className={`badge badge-${paper.status}`}>{paper.status}</span>
          {paper.needs_llm_processing && (
            <span className="badge" style={{ background: '#feebc8', color: '#7c2d12', marginLeft: '0.5rem' }}>
              ⏳ Pending LLM Processing
            </span>
          )}
        </div>
        
        <h2 style={{ fontSize: '1.75rem', fontWeight: '700', marginBottom: '1rem', lineHeight: '1.3' }}>
          {paper.title}
        </h2>
        
        <div style={{ color: '#718096', marginBottom: '1rem' }}>
          <strong>Authors:</strong> {paper.authors.map(a => a.name).join(', ')}
        </div>
        
        <div style={{ color: '#718096', marginBottom: '1rem', display: 'flex', gap: '2rem' }}>
          <div><strong>Published:</strong> {new Date(paper.published).toLocaleDateString()}</div>
          <div><strong>arXiv ID:</strong> {paper.arxiv_id}</div>
          <div>
            <strong>Categories:</strong> {paper.categories.join(', ')}
          </div>
        </div>
        
        <div style={{ marginBottom: '1rem' }}>
          <a href={paper.arxiv_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ marginRight: '0.5rem' }}>
            View on arXiv
          </a>
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
            Download PDF
          </a>
          <button className="btn btn-secondary" onClick={exportBibTeX}>
            Export BibTeX
          </button>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Abstract</h3>
          <p style={{ lineHeight: '1.6', color: '#4a5568' }}>{paper.abstract}</p>
        </div>

        <div className="card">
          <h3 className="card-title">AI Summary</h3>
          {paper.summary === '<summary>' ? (
            <p style={{ color: '#a0aec0', fontStyle: 'italic' }}>
              Summary will be generated when LLM becomes available
            </p>
          ) : (
            <>
              <p style={{ lineHeight: '1.6', marginBottom: '1rem' }}>{paper.summary}</p>
              
              {paper.key_contributions && (
                <>
                  <h4 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Key Contributions:</h4>
                  <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                    {paper.key_contributions.map((contrib, i) => (
                      <li key={i} style={{ marginBottom: '0.25rem' }}>{contrib}</li>
                    ))}
                  </ul>
                </>
              )}
              
              {paper.keywords && (
                <div>
                  <strong>Keywords:</strong> {paper.keywords.map((kw, i) => (
                    <span key={i} style={{
                      background: '#edf2f7',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      marginLeft: '0.5rem',
                      fontSize: '0.875rem'
                    }}>
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="card-title">Similar Papers</h3>
        {similar.length === 0 ? (
          <p style={{ color: '#a0aec0' }}>No similar papers found</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {similar.map(({ paper: p, similarity_score }) => (
              <div key={p.id} style={{ padding: '1rem', background: '#f7fafc', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); navigate(`/papers/${p.id}`) }}
                    style={{ color: '#667eea', fontWeight: '600' }}
                  >
                    {p.title}
                  </a>
                  <span style={{ fontSize: '0.875rem', color: '#48bb78', fontWeight: '600' }}>
                    {(similarity_score * 100).toFixed(1)}% match
                  </span>
                </div>
                <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                  {p.authors.slice(0, 3).map(a => a.name).join(', ')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">Related Papers (Graph)</h3>
        {related.length === 0 ? (
          <p style={{ color: '#a0aec0' }}>No related papers found</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {related.map(({ paper: p, relationship_type, weight }) => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <a
                    href="#"
                    onClick={(e) => { e.preventDefault(); navigate(`/papers/${p.id}`) }}
                    style={{ color: '#667eea', fontWeight: '500' }}
                  >
                    {p.title}
                  </a>
                  <div style={{ fontSize: '0.75rem', color: '#a0aec0', marginTop: '0.25rem' }}>
                    Relationship: {relationship_type.replace('_', ' ')}
                  </div>
                </div>
                <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                  {(weight * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">Notes</h3>
        <textarea
          className="input"
          style={{ minHeight: '150px', fontFamily: 'inherit' }}
          placeholder="Add your notes about this paper..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button className="btn btn-primary" onClick={saveNotes} style={{ marginTop: '1rem' }}>
          Save Notes
        </button>
      </div>
    </div>
  )
}
