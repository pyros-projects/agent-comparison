import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Star, Eye, Download, Tag, Users, Calendar } from 'lucide-react'
import { papersApi, searchApi } from '../services/api'

export function PaperDetailView() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [similarPapers, setSimilarPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState('')

  useEffect(() => {
    fetchPaper()
    fetchSimilarPapers()
  }, [id])

  const fetchPaper = async () => {
    try {
      const response = await papersApi.getById(id)
      setPaper(response.data)
      setNotes(response.data.notes || '')
    } catch (error) {
      console.error('Error fetching paper:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSimilarPapers = async () => {
    try {
      const response = await searchApi.similar(id, 5)
      setSimilarPapers(response.data)
    } catch (error) {
      console.error('Error fetching similar papers:', error)
    }
  }

  const updatePaper = async (updates) => {
    try {
      await papersApi.update(id, updates)
      fetchPaper()
    } catch (error) {
      console.error('Error updating paper:', error)
    }
  }

  const saveNotes = async () => {
    await updatePaper({ notes })
  }

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  if (!paper) {
    return <div className="text-center py-8">Paper not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link to="/" className="flex items-center text-blue-600 hover:text-blue-800">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Papers
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{paper.title}</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span className="flex items-center">
                <Users className="w-4 h-4 mr-1" />
                {paper.authors?.join(', ')}
              </span>
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {paper.published_date}
              </span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => updatePaper({ starred: !paper.starred })}
              className={`p-2 rounded-full ${
                paper.starred ? 'text-yellow-500' : 'text-gray-400'
              } hover:bg-gray-100`}
            >
              <Star className="w-5 h-5" fill={paper.starred ? 'currentColor' : 'none'} />
            </button>
            
            <button
              onClick={() => updatePaper({ read: !paper.read })}
              className={`p-2 rounded-full ${
                paper.read ? 'text-green-500' : 'text-gray-400'
              } hover:bg-gray-100`}
            >
              <Eye className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Abstract</h2>
              <p className="text-gray-700">{paper.abstract}</p>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-2">AI Summary</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                {paper.summary === '<summary>' ? (
                  <p className="text-gray-500 italic">
                    Summary generation pending (LLM unavailable)
                  </p>
                ) : (
                  <p className="text-gray-700">{paper.summary}</p>
                )}
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-2">Keywords</h2>
              <div className="flex flex-wrap gap-2">
                {paper.keywords?.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-2">Notes</h2>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                onBlur={saveNotes}
                placeholder="Add your notes here..."
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                rows={4}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Metadata</h3>
              <div className="space-y-2 text-sm">
                <div><strong>arXiv ID:</strong> {paper.arxiv_id}</div>
                <div><strong>Categories:</strong> {paper.categories?.join(', ')}</div>
                <div><strong>PDF:</strong> 
                  <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" 
                     className="text-blue-600 hover:underline">
                    Download PDF
                  </a>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Similar Papers</h3>
              <div className="space-y-2">
                {similarPapers.map((similar) => (
                  <Link
                    key={similar.paper_id}
                    to={`/paper/${similar.paper_id}`}
                    className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
                  >
                    <div className="font-medium text-sm">{similar.title}</div>
                    <div className="text-xs text-gray-600">
                      Similarity: {(similar.similarity * 100).toFixed(1)}%
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
