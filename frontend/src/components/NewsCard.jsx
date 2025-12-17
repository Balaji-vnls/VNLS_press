import React from 'react'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { Clock, ExternalLink, TrendingUp, User } from 'lucide-react'

const NewsCard = ({ 
  article, 
  showRecommendationScore = false, 
  onInteraction = null,
  className = '' 
}) => {
  const {
    id,
    title,
    summary,
    url,
    source,
    category,
    published_at,
    image_url,
    author,
    recommendation_score,
    click_probability
  } = article

  const handleClick = () => {
    if (onInteraction) {
      onInteraction(id, 'click')
    }
  }

  const handleExternalClick = (e) => {
    e.stopPropagation()
    if (onInteraction) {
      onInteraction(id, 'external_click')
    }
  }

  const getCategoryColor = (cat) => {
    const colors = {
      technology: 'bg-blue-100 text-blue-800',
      business: 'bg-green-100 text-green-800',
      health: 'bg-red-100 text-red-800',
      science: 'bg-purple-100 text-purple-800',
      general: 'bg-gray-100 text-gray-800',
      sports: 'bg-orange-100 text-orange-800',
      entertainment: 'bg-pink-100 text-pink-800'
    }
    return colors[cat] || colors.general
  }

  const formatPublishedDate = (dateString) => {
    try {
      const date = new Date(dateString)
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return 'Recently'
    }
  }

  return (
    <article className={`news-card ${className}`}>
      <Link to={`/article/${id}`} onClick={handleClick} className="block">
        {/* Image */}
        {image_url && (
          <div className="aspect-video w-full overflow-hidden">
            <img
              src={image_url}
              alt={title}
              className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                e.target.style.display = 'none'
              }}
            />
          </div>
        )}

        <div className="p-4">
          {/* Category and Recommendation Score */}
          <div className="flex items-center justify-between mb-2">
            <span className={`category-badge ${getCategoryColor(category)}`}>
              {category?.charAt(0).toUpperCase() + category?.slice(1)}
            </span>
            
            {showRecommendationScore && recommendation_score && (
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <TrendingUp className="h-3 w-3" />
                <span>{Math.round(recommendation_score * 100)}%</span>
              </div>
            )}
          </div>

          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 hover:text-primary-600 transition-colors">
            {title}
          </h3>

          {/* Summary */}
          {summary && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-3">
              {summary}
            </p>
          )}

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-4">
              {/* Source */}
              <span className="font-medium">{source}</span>
              
              {/* Author */}
              {author && (
                <div className="flex items-center space-x-1">
                  <User className="h-3 w-3" />
                  <span>{author}</span>
                </div>
              )}
              
              {/* Published Date */}
              <div className="flex items-center space-x-1">
                <Clock className="h-3 w-3" />
                <span>{formatPublishedDate(published_at)}</span>
              </div>
            </div>

            {/* External Link */}
            {url && (
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={handleExternalClick}
                className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors"
              >
                <ExternalLink className="h-3 w-3" />
                <span>Source</span>
              </a>
            )}
          </div>

          {/* AI Insights (if available) */}
          {click_probability && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>AI Prediction</span>
                <div className="flex items-center space-x-2">
                  <span>Click likelihood:</span>
                  <div className="w-16 bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${click_probability * 100}%` }}
                    />
                  </div>
                  <span>{Math.round(click_probability * 100)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </Link>
    </article>
  )
}

export default NewsCard