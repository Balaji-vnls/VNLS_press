import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { newsService } from '../services/newsService'
import LoadingSpinner from '../components/LoadingSpinner'
import { 
  Clock, 
  ExternalLink, 
  User, 
  ArrowLeft, 
  Share2, 
  Bookmark,
  Heart
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import toast from 'react-hot-toast'

const ArticlePage = () => {
  const { id } = useParams()
  const { isAuthenticated, getAuthHeaders } = useAuth()
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)
  const [readingTime, setReadingTime] = useState(0)

  useEffect(() => {
    loadArticle()
    
    // Start reading time tracking
    const startTime = Date.now()
    
    return () => {
      // Log reading time when component unmounts
      const endTime = Date.now()
      const duration = (endTime - startTime) / 1000 // seconds
      setReadingTime(duration)
      
      if (isAuthenticated() && article && duration > 5) {
        // Only log if user spent more than 5 seconds reading
        logInteraction('read', duration)
      }
    }
  }, [id])

  const loadArticle = async () => {
    try {
      setLoading(true)
      const data = await newsService.getArticle(
        id, 
        isAuthenticated() ? getAuthHeaders() : {}
      )
      setArticle(data.article)
      
      // Log view interaction
      if (isAuthenticated()) {
        await logInteraction('view')
      }
    } catch (error) {
      console.error('Error loading article:', error)
      toast.error('Failed to load article')
    } finally {
      setLoading(false)
    }
  }

  const logInteraction = async (type, duration = null) => {
    if (!isAuthenticated() || !article) return
    
    try {
      await newsService.logInteraction(
        article.id, 
        type, 
        duration, 
        getAuthHeaders()
      )
    } catch (error) {
      console.error('Error logging interaction:', error)
    }
  }

  const handleShare = async () => {
    if (navigator.share && article) {
      try {
        await navigator.share({
          title: article.title,
          text: article.summary,
          url: window.location.href
        })
        await logInteraction('share')
      } catch (error) {
        // Fallback to clipboard
        handleCopyLink()
      }
    } else {
      handleCopyLink()
    }
  }

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href)
    toast.success('Link copied to clipboard!')
  }

  const handleBookmark = async () => {
    await logInteraction('bookmark')
    toast.success('Article bookmarked!')
  }

  const handleLike = async () => {
    await logInteraction('like')
    toast.success('Article liked!')
  }

  const getCategoryColor = (category) => {
    const colors = {
      technology: 'bg-blue-100 text-blue-800',
      business: 'bg-green-100 text-green-800',
      health: 'bg-red-100 text-red-800',
      science: 'bg-purple-100 text-purple-800',
      general: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || colors.general
  }

  const formatPublishedDate = (dateString) => {
    try {
      const date = new Date(dateString)
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return 'Recently'
    }
  }

  const estimateReadingTime = (content) => {
    const wordsPerMinute = 200
    const words = content?.split(' ').length || 0
    return Math.ceil(words / wordsPerMinute)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    )
  }

  if (!article) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Article not found</h2>
          <p className="text-gray-600 mb-6">The article you're looking for doesn't exist.</p>
          <Link to="/" className="btn-primary">
            Go Home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back to News</span>
          </Link>
        </div>

        {/* Article */}
        <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* Article Image */}
          {article.image_url && (
            <div className="aspect-video w-full overflow-hidden">
              <img
                src={article.image_url}
                alt={article.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none'
                }}
              />
            </div>
          )}

          <div className="p-8">
            {/* Category and Metadata */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <span className={`category-badge ${getCategoryColor(article.category)}`}>
                  {article.category?.charAt(0).toUpperCase() + article.category?.slice(1)}
                </span>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-4 w-4" />
                    <span>{formatPublishedDate(article.published_at)}</span>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <span>{estimateReadingTime(article.content)} min read</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleLike}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                  title="Like article"
                >
                  <Heart className="h-5 w-5" />
                </button>
                
                <button
                  onClick={handleBookmark}
                  className="p-2 text-gray-400 hover:text-blue-500 transition-colors"
                  title="Bookmark article"
                >
                  <Bookmark className="h-5 w-5" />
                </button>
                
                <button
                  onClick={handleShare}
                  className="p-2 text-gray-400 hover:text-green-500 transition-colors"
                  title="Share article"
                >
                  <Share2 className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 leading-tight">
              {article.title}
            </h1>

            {/* Author and Source */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                {article.author && (
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">
                      {article.author}
                    </span>
                  </div>
                )}
                
                <div className="text-sm text-gray-500">
                  Published by <span className="font-medium">{article.source}</span>
                </div>
              </div>

              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => logInteraction('external_click')}
                  className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Read Original</span>
                </a>
              )}
            </div>

            {/* Summary */}
            {article.summary && (
              <div className="mb-8">
                <div className="bg-gray-50 rounded-lg p-6 border-l-4 border-primary-500">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Summary</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {article.summary}
                  </p>
                </div>
              </div>
            )}

            {/* Content */}
            <div className="prose prose-lg max-w-none">
              <div className="text-gray-800 leading-relaxed whitespace-pre-line">
                {article.content}
              </div>
            </div>

            {/* AI Insights */}
            {(article.recommendation_score || article.click_probability) && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {article.recommendation_score && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-900">
                          Recommendation Score
                        </span>
                        <span className="text-lg font-bold text-blue-600">
                          {Math.round(article.recommendation_score * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${article.recommendation_score * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {article.click_probability && (
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-green-900">
                          Engagement Prediction
                        </span>
                        <span className="text-lg font-bold text-green-600">
                          {Math.round(article.click_probability * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-green-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${article.click_probability * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </article>
      </div>
    </div>
  )
}

export default ArticlePage