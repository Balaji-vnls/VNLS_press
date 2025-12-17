import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { newsService } from '../services/newsService'
import NewsCard from '../components/NewsCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Tag, TrendingUp } from 'lucide-react'
import toast from 'react-hot-toast'

const CategoryPage = () => {
  const { category } = useParams()
  const { isAuthenticated, getAuthHeaders } = useAuth()
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [categoryInfo, setCategoryInfo] = useState(null)

  useEffect(() => {
    loadCategoryData()
  }, [category])

  const loadCategoryData = async () => {
    try {
      setLoading(true)
      
      // Get category articles
      const articlesData = await newsService.getNewsByCategory(
        category, 
        50, 
        isAuthenticated() ? getAuthHeaders() : {}
      )
      setArticles(articlesData.articles || [])
      
      // Get category info
      const categoriesData = await newsService.getCategories()
      const categoryData = categoriesData.categories?.find(c => c.id === category)
      setCategoryInfo(categoryData)
      
    } catch (error) {
      console.error('Error loading category data:', error)
      toast.error('Failed to load category articles')
    } finally {
      setLoading(false)
    }
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

  const getCategoryIcon = (categoryId) => {
    const icons = {
      technology: '💻',
      business: '💼',
      health: '🏥',
      science: '🔬',
      general: '📰',
      sports: '⚽',
      entertainment: '🎬'
    }
    return icons[categoryId] || '📰'
  }

  const getCategoryColor = (categoryId) => {
    const colors = {
      technology: 'from-blue-500 to-blue-600',
      business: 'from-green-500 to-green-600',
      health: 'from-red-500 to-red-600',
      science: 'from-purple-500 to-purple-600',
      general: 'from-gray-500 to-gray-600',
      sports: 'from-orange-500 to-orange-600',
      entertainment: 'from-pink-500 to-pink-600'
    }
    return colors[categoryId] || 'from-gray-500 to-gray-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Category Header */}
      <div className={`bg-gradient-to-r ${getCategoryColor(category)} text-white`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="text-6xl mb-4">
              {getCategoryIcon(category)}
            </div>
            <h1 className="text-4xl font-bold mb-4">
              {categoryInfo?.name || category?.charAt(0).toUpperCase() + category?.slice(1)} News
            </h1>
            <p className="text-xl text-white/90 max-w-2xl mx-auto">
              {categoryInfo?.description || `Latest news and updates in ${category}`}
            </p>
            
            {articles.length > 0 && (
              <div className="mt-6 flex items-center justify-center space-x-6 text-white/80">
                <div className="flex items-center space-x-2">
                  <Tag className="h-5 w-5" />
                  <span>{articles.length} articles</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Updated recently</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Articles Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {articles.length > 0 ? (
          <>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Latest {categoryInfo?.name || category} Articles
              </h2>
              <p className="text-gray-600 mt-1">
                {isAuthenticated() 
                  ? 'Personalized recommendations based on your interests'
                  : 'Popular articles in this category'
                }
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article, index) => (
                <NewsCard
                  key={`${article.id}-${index}`}
                  article={article}
                  showRecommendationScore={isAuthenticated()}
                  onInteraction={handleNewsInteraction}
                  className="animate-fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                />
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="text-6xl mb-4">
                {getCategoryIcon(category)}
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No articles found
              </h3>
              <p className="text-gray-600 mb-4">
                We couldn't find any articles in the {categoryInfo?.name || category} category right now.
              </p>
              <button
                onClick={loadCategoryData}
                className="btn-primary"
              >
                Refresh Articles
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CategoryPage