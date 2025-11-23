import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchAPI, healthAPI } from '../api'

export default function TheoryModeView() {
  const [hypothesis, setHypothesis] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [llmAvailable, setLlmAvailable] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    console.log('TheoryModeView: Component mounted')
    checkLLMAvailability()
  }, [])

  const checkLLMAvailability = async () => {
    try {
      const health = await healthAPI.check()
      console.log('TheoryModeView: LLM availability:', health.llm_available)
      setLlmAvailable(health.llm_available)
    } catch (error) {
      console.error('TheoryModeView: Health check error:', error)
    }
  }

  const handleAnalyze = async () => {
    if (!hypothesis.trim()) return
    
    console.log('TheoryModeView: Analyzing hypothesis:', hypothesis)
    setLoading(true)
    setResults(null)
    
    try {
      const data = await searchAPI.theory(hypothesis, 5)
      console.log('TheoryModeView: Analysis complete:', data)
      setResults(data)
    } catch (error) {
      console.error('TheoryModeView: Analysis error:', error)
      alert('Failed to analyze theory: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const exportDebate = () => {
    if (!results) return
    
    let text = `Theory Analysis: ${hypothesis}\n\n`
    
    text += `=== SUPPORTING ARGUMENTS (${results.pro.length}) ===\n\n`
    results.pro.forEach((arg, i) => {
      text += `${i + 1}. ${arg.paper_title}\n`
      text += `   Relevance: ${(arg.relevance_score * 100).toFixed(1)}%\n`
      text += `   ${arg.summary}\n\n`
    })
    
    text += `\n=== CONTRADICTING ARGUMENTS (${results.contra.length}) ===\n\n`
    results.contra.forEach((arg, i) => {
      text += `${i + 1}. ${arg.paper_title}\n`
      text += `   Relevance: ${(arg.relevance_score * 100).toFixed(1)}%\n`
      text += `   ${arg.summary}\n\n`
    })
    
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'theory-analysis.txt'
    a.click()
    console.log('TheoryModeView: Debate exported')
  }

  return (
    <div>
      <div className="view-header">
        <h2 className="view-title">🔬 Theory Mode</h2>
        <p className="view-subtitle">Validate hypotheses with pro/contra arguments from your paper collection</p>
      </div>

      {!llmAvailable && (
        <div className="card" style={{ background: '#fff5f7', border: '2px solid #fc8181' }}>
          <h3 style={{ color: '#c53030', marginBottom: '0.5rem' }}>⚠️ Theory Mode Unavailable</h3>
          <p style={{ color: '#742a2a' }}>
            Theory mode requires an LLM for argument extraction. Please configure your LLM credentials 
            in the .env file and restart the application.
          </p>
        </div>
      )}

      <div className="card">
        <h3 className="card-title">Enter Your Hypothesis</h3>
        <textarea
          className="input"
          style={{ minHeight: '100px', marginBottom: '1rem' }}
          placeholder="Enter a theory or hypothesis to validate (e.g., 'Transformer models are more efficient than RNNs for long sequences')"
          value={hypothesis}
          onChange={(e) => setHypothesis(e.target.value)}
          disabled={!llmAvailable}
        />
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            className="btn btn-primary" 
            onClick={handleAnalyze}
            disabled={!llmAvailable || loading || !hypothesis.trim()}
          >
            {loading ? 'Analyzing...' : '🔍 Analyze Hypothesis'}
          </button>
          {results && (
            <button className="btn btn-secondary" onClick={exportDebate}>
              📄 Export Analysis
            </button>
          )}
        </div>
      </div>

      {loading && (
        <div className="card">
          <div className="loading">
            Analyzing papers for evidence... This may take a moment.
          </div>
        </div>
      )}

      {results && !loading && (
        <div className="grid grid-2">
          <div className="card" style={{ background: '#f0fff4', borderLeft: '4px solid #48bb78' }}>
            <h3 className="card-title" style={{ color: '#22543d' }}>
              ✅ Supporting Arguments ({results.pro.length})
            </h3>
            {results.pro.length === 0 ? (
              <p style={{ color: '#718096' }}>No supporting arguments found</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.pro.map((arg) => (
                  <div key={arg.paper_id} style={{ 
                    background: 'white', 
                    padding: '1rem', 
                    borderRadius: '8px',
                    border: '1px solid #c6f6d5'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <a
                        href="#"
                        onClick={(e) => { e.preventDefault(); navigate(`/papers/${arg.paper_id}`) }}
                        style={{ color: '#667eea', fontWeight: '600', flex: 1 }}
                      >
                        {arg.paper_title}
                      </a>
                      <span style={{ 
                        fontSize: '0.875rem', 
                        color: '#38a169', 
                        fontWeight: '600',
                        marginLeft: '1rem'
                      }}>
                        {(arg.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#2d3748' }}>
                      {arg.summary}
                    </p>
                    {arg.key_quotes && arg.key_quotes.length > 0 && (
                      <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#718096', marginBottom: '0.25rem' }}>
                          Key quotes:
                        </div>
                        {arg.key_quotes.map((quote, i) => (
                          <div key={i} style={{ 
                            fontSize: '0.75rem', 
                            fontStyle: 'italic', 
                            color: '#4a5568',
                            paddingLeft: '0.5rem',
                            borderLeft: '2px solid #c6f6d5',
                            marginBottom: '0.25rem'
                          }}>
                            "{quote}"
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{ background: '#fffaf0', borderLeft: '4px solid #ed8936' }}>
            <h3 className="card-title" style={{ color: '#7c2d12' }}>
              ❌ Contradicting Arguments ({results.contra.length})
            </h3>
            {results.contra.length === 0 ? (
              <p style={{ color: '#718096' }}>No contradicting arguments found</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.contra.map((arg) => (
                  <div key={arg.paper_id} style={{ 
                    background: 'white', 
                    padding: '1rem', 
                    borderRadius: '8px',
                    border: '1px solid #feebc8'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <a
                        href="#"
                        onClick={(e) => { e.preventDefault(); navigate(`/papers/${arg.paper_id}`) }}
                        style={{ color: '#667eea', fontWeight: '600', flex: 1 }}
                      >
                        {arg.paper_title}
                      </a>
                      <span style={{ 
                        fontSize: '0.875rem', 
                        color: '#c05621', 
                        fontWeight: '600',
                        marginLeft: '1rem'
                      }}>
                        {(arg.relevance_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#2d3748' }}>
                      {arg.summary}
                    </p>
                    {arg.key_quotes && arg.key_quotes.length > 0 && (
                      <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: '0.75rem', color: '#718096', marginBottom: '0.25rem' }}>
                          Key quotes:
                        </div>
                        {arg.key_quotes.map((quote, i) => (
                          <div key={i} style={{ 
                            fontSize: '0.75rem', 
                            fontStyle: 'italic', 
                            color: '#4a5568',
                            paddingLeft: '0.5rem',
                            borderLeft: '2px solid #feebc8',
                            marginBottom: '0.25rem'
                          }}>
                            "{quote}"
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {results && !loading && (
        <div className="card">
          <h3 className="card-title">Analysis Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div style={{ textAlign: 'center', padding: '1rem', background: '#f0fff4', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: '#38a169' }}>
                {results.pro.length}
              </div>
              <div style={{ color: '#22543d', fontSize: '0.875rem' }}>Supporting</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1rem', background: '#fffaf0', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: '#c05621' }}>
                {results.contra.length}
              </div>
              <div style={{ color: '#7c2d12', fontSize: '0.875rem' }}>Contradicting</div>
            </div>
            <div style={{ textAlign: 'center', padding: '1rem', background: '#edf2f7', borderRadius: '8px' }}>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: '#2d3748' }}>
                {results.pro.length + results.contra.length}
              </div>
              <div style={{ color: '#4a5568', fontSize: '0.875rem' }}>Total Evidence</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
