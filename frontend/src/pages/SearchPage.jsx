import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { newsService } from '../services/newsService'
import NewsCard from '../components/NewsCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Search, Filter, X } from 'lucide-react'
import toast from 'react-hot-toast'

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const { isAuthenticated, getAuthHeaders } = useAuth()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('')
  const [categories, setCategories] = useState([])

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    const searchQuery = searchParams.get('q')
    if (searchQuery) {
      setQuery(searchQuery)
      performSearch(searchQuery)
    }
  }, [searchParams])

  const loadCategories = async () => {
    try {
      const data = await newsService.getCategories()
      setCategories(data.categories || [])
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  const performSearch = async (searchQuery = query, category = selectedCategory) => {
    if (!searchQuery.trim()) return

    try {
      setLoading(true)
      const data = await newsService.searchNews(
        searchQuery.trim(),
        50,
        category || null
      )
      setResults(data.articles || [])
    } catch (error) {
      console.error('Error searching news:', error)
      toast.error('Failed to search news')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (query.trim()) {
      setSearchParams({ q: query.trim() })
      performSearch(query.trim())
    }
  }

  const handleCategoryChange = (category) => {
    setSelectedCategory(category)
    if (query.trim()) {
      performSearch(query, category)
    }
  }

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setSearchParams({})
  }

  const handleNewsInteraction = async (articleId, interactionType) => {
    if (isAuthenticated()) {
      try {
        await newsService.logInteraction(articleId, interactionType, null, getAuthHeaders())
      } catch (error) {
        console.error('Error logging interaction:', error)
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Search News</h1>
          
          {/* Search Form */}
          <form onSubmit={handleSearch} className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search for news articles..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
              />
              {query && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          </form>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filter by category:</span>
            </div>
            
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleCategoryChange('')}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedCategory === ''
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryChange(category.id)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Search Results */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : results.length > 0 ? (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Search Results
              </h2>
              <p className="text-gray-600">
                Found {results.length} articles for "{query}"
                {selectedCategory && ` in ${categories.find(c => c.id === selectedCategory)?.name}`}
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((article, index) => (
                <NewsCard
                  key={`${article.id}-${index}`}
                  article={article}
                  onInteraction={handleNewsInteraction}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                />
              ))}
            </div>
          </>
        ) : query ? (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No results found
              </h3>
              <p className="text-gray-600 mb-4">
                We couldn't find any articles matching "{query}"
                {selectedCategory && ` in ${categories.find(c => c.id === selectedCategory)?.name}`}.
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <p>Try:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Using different keywords</li>
                  <li>Checking your spelling</li>
                  <li>Removing category filters</li>
                  <li>Using more general terms</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Search for News
              </h3>
              <p className="text-gray-600">
                Enter keywords to search through thousands of news articles from trusted sources.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchPage