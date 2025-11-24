import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Star, Eye, Download, Plus } from 'lucide-react'
import { papersApi } from '../services/api'

export function PaperListView() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [sortBy, setSortBy] = useState('date')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchPapers()
  }, [searchQuery, filterStatus, sortBy, currentPage])

  const fetchPapers = async () => {
    try {
      setLoading(true)
      const params = {
        search: searchQuery,
        status: filterStatus,
        sort: sortBy,
        page: currentPage,
        limit: 20
      }
      const response = await papersApi.getAll(params)
      setPapers(response.data.papers)
      setTotalPages(response.data.totalPages)
    } catch (error) {
      console.error('Error fetching papers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleIngest = async (url) => {
    try {
      await papersApi.ingest(url)
      fetchPapers()
    } catch (error) {
      console.error('Error ingesting paper:', error)
    }
  }

  const toggleStar = async (paperId) => {
    try {
      const paper = papers.find(p => p.id === paperId)
      await papersApi.update(paperId, { starred: !paper.starred })
      fetchPapers()
    } catch (error) {
      console.error('Error updating paper:', error)
    }
  }

  const toggleRead = async (paperId) => {
    try {
      const paper = papers.find(p => p.id === paperId)
      await papersApi.update(paperId, { read: !paper.read })
      fetchPapers()
    } catch (error) {
      console.error('Error updating paper:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Research Papers</h1>
        <button
          onClick={() => {
            const url = prompt('Enter arXiv URL:')
            if (url) handleIngest(url)
          }}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          <span>Add Paper</span>
        </button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search papers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Papers</option>
            <option value="read">Read</option>
            <option value="unread">Unread</option>
            <option value="starred">Starred</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">Date</option>
            <option value="title">Title</option>
            <option value="authors">Authors</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="loading-spinner"></div>
        </div>
      ) : (
        <div className="grid gap-4">
          {papers.map((paper) => (
            <div key={paper.id} className="bg-white p-6 rounded-lg shadow paper-card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <Link to={`/paper/${paper.id}`}>
                    <h3 className="text-xl font-semibold text-gray-900 hover:text-blue-600">
                      {paper.title}
                    </h3>
                  </Link>
                  <p className="text-sm text-gray-600 mt-1">
                    {paper.authors?.join(', ')}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    {paper.categories?.join(', ')} • {paper.published_date}
                  </p>
                  <p className="text-gray-700 mt-2 line-clamp-2">
                    {paper.abstract}
                  </p>
                </div>
                
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => toggleStar(paper.id)}
                    className={`p-2 rounded-full ${
                      paper.starred ? 'text-yellow-500' : 'text-gray-400'
                    } hover:bg-gray-100`}
                  >
                    <Star className="w-5 h-5" fill={paper.starred ? 'currentColor' : 'none'} />
                  </button>
                  
                  <button
                    onClick={() => toggleRead(paper.id)}
                    className={`p-2 rounded-full ${
                      paper.read ? 'text-green-500' : 'text-gray-400'
                    } hover:bg-gray-100`}
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center space-x-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => setCurrentPage(page)}
              className={`px-4 py-2 rounded-md ${
                currentPage === page
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {page}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
