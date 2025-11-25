import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  FlaskConical, 
  Search, 
  AlertCircle, 
  ThumbsUp, 
  ThumbsDown,
  FileText,
  Loader,
} from 'lucide-react'
import { analyzeTheory, getTheoryStatus } from '../api'
import { TheoryResponse } from '../types'
import { useStatus } from '../context/StatusContext'

export default function TheoryMode() {
  const [theory, setTheory] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TheoryResponse | null>(null)
  const [theoryAvailable, setTheoryAvailable] = useState<boolean | null>(null)
  const [statusMessage, setStatusMessage] = useState('')
  
  const { status } = useStatus()

  useEffect(() => {
    console.log('[TheoryMode] Checking availability...')
    getTheoryStatus().then(({ available, message }) => {
      setTheoryAvailable(available)
      setStatusMessage(message)
      console.log('[TheoryMode] Status:', { available, message })
    }).catch((e) => {
      console.error('[TheoryMode] Failed to get status:', e)
      setTheoryAvailable(false)
      setStatusMessage('Failed to check Theory Mode status')
    })
  }, [status])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!theory.trim() || !theoryAvailable) return

    console.log('[TheoryMode] Analyzing theory:', theory)
    setLoading(true)
    setResult(null)

    try {
      const data = await analyzeTheory(theory)
      setResult(data)
      console.log('[TheoryMode] Analysis complete:', data)
    } catch (e) {
      console.error('[TheoryMode] Analysis failed:', e)
      setResult({
        theory,
        pro_arguments: [],
        contra_arguments: [],
        analysis_summary: '',
        llm_available: false,
        error: 'Failed to analyze theory. Please try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <FlaskConical className="text-purple-600" size={32} />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Theory Mode</h1>
          <p className="text-gray-600">
            Enter a hypothesis and discover evidence for and against it from your paper collection.
          </p>
        </div>
      </div>

      {/* Availability warning */}
      {theoryAvailable === false && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="text-yellow-600 mt-0.5" size={20} />
          <div>
            <h3 className="font-medium text-yellow-800">Theory Mode Unavailable</h3>
            <p className="text-yellow-700 text-sm">
              {statusMessage || 'Theory Mode requires an active LLM connection to analyze papers.'}
            </p>
          </div>
        </div>
      )}

      {/* Search form */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter your hypothesis or theory
            </label>
            <textarea
              value={theory}
              onChange={(e) => setTheory(e.target.value)}
              placeholder="e.g., Transformer architectures are more efficient than RNNs for long-sequence modeling..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none"
              disabled={!theoryAvailable || loading}
            />
          </div>
          
          <button
            type="submit"
            disabled={!theory.trim() || !theoryAvailable || loading}
            className="flex items-center justify-center gap-2 w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={20} />
                Analyzing...
              </>
            ) : (
              <>
                <Search size={20} />
                Analyze Theory
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Error */}
          {result.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="text-red-600 mt-0.5" size={20} />
              <div>
                <h3 className="font-medium text-red-800">Analysis Error</h3>
                <p className="text-red-700 text-sm">{result.error}</p>
              </div>
            </div>
          )}

          {/* Analysis summary */}
          {result.analysis_summary && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Analysis Summary</h2>
              <p className="text-gray-700">{result.analysis_summary}</p>
            </div>
          )}

          {/* Pro and Contra columns */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pro arguments */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="bg-green-50 border-b border-green-100 px-6 py-4 flex items-center gap-2">
                <ThumbsUp className="text-green-600" size={20} />
                <h2 className="text-lg font-semibold text-green-800">
                  Supporting Evidence ({result.pro_arguments.length})
                </h2>
              </div>
              <div className="p-6 space-y-4 max-h-[600px] overflow-y-auto">
                {result.pro_arguments.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    No supporting evidence found.
                  </p>
                ) : (
                  result.pro_arguments.map((arg, index) => (
                    <div key={index} className="border border-green-100 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Link
                          to={`/papers/${arg.paper_id}`}
                          className="text-blue-600 hover:underline font-medium flex items-center gap-1"
                        >
                          <FileText size={16} />
                          {arg.paper_title}
                        </Link>
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                          {(arg.relevance_score * 100).toFixed(0)}% relevant
                        </span>
                      </div>
                      <p className="text-gray-700 text-sm mb-2">{arg.summary}</p>
                      {arg.key_quotes && arg.key_quotes.length > 0 && (
                        <div className="bg-green-50 rounded p-3 mt-2">
                          <p className="text-xs font-medium text-green-800 mb-1">Key quotes:</p>
                          {arg.key_quotes.map((quote, qi) => (
                            <p key={qi} className="text-xs text-green-700 italic">
                              "{quote}"
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Contra arguments */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="bg-red-50 border-b border-red-100 px-6 py-4 flex items-center gap-2">
                <ThumbsDown className="text-red-600" size={20} />
                <h2 className="text-lg font-semibold text-red-800">
                  Contradicting Evidence ({result.contra_arguments.length})
                </h2>
              </div>
              <div className="p-6 space-y-4 max-h-[600px] overflow-y-auto">
                {result.contra_arguments.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">
                    No contradicting evidence found.
                  </p>
                ) : (
                  result.contra_arguments.map((arg, index) => (
                    <div key={index} className="border border-red-100 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Link
                          to={`/papers/${arg.paper_id}`}
                          className="text-blue-600 hover:underline font-medium flex items-center gap-1"
                        >
                          <FileText size={16} />
                          {arg.paper_title}
                        </Link>
                        <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                          {(arg.relevance_score * 100).toFixed(0)}% relevant
                        </span>
                      </div>
                      <p className="text-gray-700 text-sm mb-2">{arg.summary}</p>
                      {arg.key_quotes && arg.key_quotes.length > 0 && (
                        <div className="bg-red-50 rounded p-3 mt-2">
                          <p className="text-xs font-medium text-red-800 mb-1">Key quotes:</p>
                          {arg.key_quotes.map((quote, qi) => (
                            <p key={qi} className="text-xs text-red-700 italic">
                              "{quote}"
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && theoryAvailable && (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <FlaskConical className="text-gray-300 mx-auto mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            Start Your Analysis
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Enter a hypothesis above and click "Analyze Theory" to discover supporting and contradicting evidence from your paper collection.
          </p>
        </div>
      )}
    </div>
  )
}
