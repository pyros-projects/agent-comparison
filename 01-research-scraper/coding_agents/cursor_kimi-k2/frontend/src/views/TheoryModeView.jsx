import React, { useState } from 'react'
import { Search, Lightbulb, AlertTriangle } from 'lucide-react'
import { theoryApi } from '../services/api'

export function TheoryModeView() {
  const [theory, setTheory] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const analyzeTheory = async () => {
    if (!theory.trim()) return

    try {
      setLoading(true)
      setError(null)
      const response = await theoryApi.analyze(theory)
      setResults(response.data)
    } catch (error) {
      console.error('Error analyzing theory:', error)
      setError(error.response?.data?.detail || 'Failed to analyze theory')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Theory Mode</h1>
        <p className="text-gray-600">
          Enter a hypothesis or theory to find supporting and contradicting evidence from your paper collection.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Theory or Hypothesis
            </label>
            <textarea
              value={theory}
              onChange={(e) => setTheory(e.target.value)}
              placeholder="Enter your theory here..."
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              rows={4}
            />
          </div>
          
          <button
            onClick={analyzeTheory}
            disabled={!theory.trim() || loading}
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <Search className="w-4 h-4" />
            <span>{loading ? 'Analyzing...' : 'Analyze Theory'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {results && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <Lightbulb className="w-5 h-5 text-green-500 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Supporting Evidence</h2>
            </div>
            
            {results.supporting.length === 0 ? (
              <p className="text-gray-500">No supporting evidence found.</p>
            ) : (
              <div className="space-y-4">
                {results.supporting.map((item, index) => (
                  <div key={index} className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-semibold text-gray-900">{item.paper_title}</h3>
                    <p className="text-sm text-gray-600 mb-2">Relevance: {(item.relevance_score * 100).toFixed(1)}%</p>
                    <p className="text-gray-700 text-sm">{item.argument_summary}</p>
                    {item.key_quotes.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-gray-600">Key quotes:</p>
                        {item.key_quotes.map((quote, qIndex) => (
                          <p key={qIndex} className="text-xs text-gray-500 italic mt-1">"{quote}"</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <AlertTriangle className="w-5 h-5 text-red-500 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Contradicting Evidence</h2>
            </div>
            
            {results.contradicting.length === 0 ? (
              <p className="text-gray-500">No contradicting evidence found.</p>
            ) : (
              <div className="space-y-4">
                {results.contradicting.map((item, index) => (
                  <div key={index} className="border-l-4 border-red-500 pl-4">
                    <h3 className="font-semibold text-gray-900">{item.paper_title}</h3>
                    <p className="text-sm text-gray-600 mb-2">Relevance: {(item.relevance_score * 100).toFixed(1)}%</p>
                    <p className="text-gray-700 text-sm">{item.argument_summary}</p>
                    {item.key_quotes.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs font-medium text-gray-600">Key quotes:</p>
                        {item.key_quotes.map((quote, qIndex) => (
                          <p key={qIndex} className="text-xs text-gray-500 italic mt-1">"{quote}"</p>
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
    </div>
  )
}
