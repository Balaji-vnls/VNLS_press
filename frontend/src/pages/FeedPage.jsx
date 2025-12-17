import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { recommendationService } from '../services/recommendationService'
import { newsService } from '../services/newsService'
import NewsCard from '../components/NewsCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { RefreshCw, Filter, TrendingUp } from 'lucide-react'
import toast from 'react-hot-toast'

const FeedPage = () => {
  const { getAuthHeaders } = useAuth()
  const [feed, setFeed] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [categories, setCategories] = useState([])

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (selectedCategory !== 'all') {
      loadCategoryFeed()
    } else {
      loadPersonalizedFeed()
    }
  }, [selectedCategory])

  const loadInitialData = async () => {
    try {
      // Load categories
      const categoriesData = await newsService.getCategories()
      setCategories([
        { id: 'all', name: 'All' },
        ...(categoriesData.categories || [])
      ])

      // Load personalized feed
      await loadPersonalizedFeed()
    } catch (error) {
      console.error('Error loading initial data:', error)
      toast.error('Failed to load feed')
    }
  }

  const loadPersonalizedFeed = async () => {
    try {
      setLoading(true)
      const data = await recommendationService.getForYouFeed(50, getAuthHeaders())
      setFeed(data.feed || [])
    } catch (error) {
      console.error('Error loading personalized feed:', error)
      toast.error('Failed to load personalized feed')
    } finally {
      setLoading(false)
    }
  }

  const loadCategoryFeed = async () => {
    try {
      setLoading(true)
      const data = await recommendationService.getCategoryRecommendations(
        selectedCategory, 
        50, 
        getAuthHeaders()
      )
      setFeed(data.recommendations || [])
    } catch (error) {
      console.error('Error loading category feed:', error)
      toast.error('Failed to load category feed')
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      
      // Trigger news refresh
      await newsService.refreshNews()
      
      // Reload feed
      if (selectedCategory === 'all') {
        await loadPersonalizedFeed()
      } else {
        await loadCategoryFeed()
      }
      
      toast.success('Feed refreshed!')
    } catch (error) {
      console.error('Error refreshing feed:', error)
      toast.error('Failed to refresh feed')
    } finally {
      setRefreshing(false)
    }
  }

  const handleNewsInteraction = async (articleId, interactionType) => {
    try {
      await newsService.logInteraction(articleId, interactionType, null, getAuthHeaders())
      
      // If it's a read interaction, we might want to update the feed
      if (interactionType === 'read') {
        // Optionally refresh recommendations after reading
      }
    } catch (error) {
      console.error('Error logging interaction:', error)
    }
  }

  if (loading && feed.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Personalized Feed</h1>
            <p className="mt-2 text-gray-600">
              AI-curated news based on your interests and reading history
            </p>
          </div>
          
          <div className="mt-4 sm:mt-0 flex items-center space-x-4">
            {/* Category Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Feed Stats */}
        {feed.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900">
                    {feed.length} personalized articles
                  </span>
                </div>
                {selectedCategory !== 'all' && (
                  <div className="text-sm text-gray-500">
                    Filtered by: {categories.find(c => c.id === selectedCategory)?.name}
                  </div>
                )}
              </div>
              
              <div className="text-sm text-gray-500">
                Updated {new Date().toLocaleTimeString()}
              </div>
            </div>
          </div>
        )}

        {/* News Feed */}
        {feed.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {feed.map((article, index) => (
              <NewsCard
                key={`${article.id}-${index}`}
                article={article}
                showRecommendationScore={true}
                onInteraction={handleNewsInteraction}
                className="animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No articles found
              </h3>
              <p className="text-gray-600 mb-4">
                {selectedCategory === 'all' 
                  ? "We're building your personalized feed. Try refreshing or check back later."
                  : `No articles found in the ${categories.find(c => c.id === selectedCategory)?.name} category.`
                }
              </p>
              <button
                onClick={handleRefresh}
                className="btn-primary"
              >
                Refresh Feed
              </button>
            </div>
          </div>
        )}

        {/* Loading More */}
        {loading && feed.length > 0 && (
          <div className="text-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        )}
      </div>
    </div>
  )
}

export default FeedPage