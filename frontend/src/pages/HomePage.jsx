import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { newsService } from '../services/newsService'
import { recommendationService } from '../services/recommendationService'
import NewsCard from '../components/NewsCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { TrendingUp, Rss, Sparkles, ArrowRight, Newspaper, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

const HomePage = () => {
  const { isAuthenticated, getAuthHeaders } = useAuth()
  const [trendingNews, setTrendingNews] = useState([])
  const [personalizedNews, setPersonalizedNews] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('trending')

  useEffect(() => {
    loadInitialData()
  }, [isAuthenticated()])

  const loadInitialData = async (retryCount = 0) => {
    try {
      setLoading(true)
      
      // Load categories
      const categoriesData = await newsService.getCategories()
      setCategories(categoriesData.categories || [])

      // Load trending news
      const trendingData = await newsService.getTrendingNews(20)
      setTrendingNews(trendingData.articles || [])

      // Load personalized news if user is authenticated
      if (isAuthenticated()) {
        try {
          const personalizedData = await recommendationService.getForYouFeed(20, getAuthHeaders())
          setPersonalizedNews(personalizedData.feed || [])
          setActiveTab('personalized')
        } catch (error) {
          console.error('Error loading personalized news:', error)
          // Fall back to trending if personalized fails
          setActiveTab('trending')
        }
      }
    } catch (error) {
      console.error('Error loading initial data:', error)
      
      // Retry once if first attempt fails
      if (retryCount === 0) {
        setTimeout(() => loadInitialData(1), 2000)
        return
      }
      
      // Only show error if we have no data at all after retry
      if (trendingNews.length === 0 && personalizedNews.length === 0) {
        toast.error('Unable to connect to NARAYANASWAMY SONS news service. Please refresh the page.')
      }
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="xl" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                NARAYANASWAMY SONS
              </span>{' '}
              News Intelligence Platform
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
              Advanced AI-powered news intelligence by Narayanaswamy Sons. 
              Get personalized recommendations from trusted global sources with real-time updates.
            </p>
            
            {!isAuthenticated() && (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/signup"
                  className="bg-white text-primary-600 hover:bg-gray-100 font-semibold py-3 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center"
                >
                  <Sparkles className="h-5 w-5 mr-2" />
                  Get Personalized News
                </Link>
                <Link
                  to="/login"
                  className="border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
                >
                  Sign In
                </Link>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Indicator */}
        {(trendingNews.length > 0 || personalizedNews.length > 0) && (
          <div className="mb-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-700 font-medium">
                  NARAYANASWAMY SONS News Intelligence Platform - Live & Operational
                </span>
                <span className="text-xs text-green-600">
                  {trendingNews.length + personalizedNews.length} articles loaded
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            {isAuthenticated() && (
              <button
                onClick={() => setActiveTab('personalized')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
                  activeTab === 'personalized'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Rss className="h-4 w-4" />
                <span>For You</span>
              </button>
            )}
            <button
              onClick={() => setActiveTab('trending')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === 'trending'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <TrendingUp className="h-4 w-4" />
              <span>Trending</span>
            </button>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => loadInitialData(0)}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            {isAuthenticated() && (
              <Link
                to="/feed"
                className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium"
              >
                <span>View Full Feed</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            )}
          </div>
        </div>

        {/* News Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {activeTab === 'personalized' && personalizedNews.length > 0 ? (
            personalizedNews.slice(0, 12).map((article) => (
              <NewsCard
                key={article.id}
                article={article}
                showRecommendationScore={true}
                onInteraction={handleNewsInteraction}
              />
            ))
          ) : (
            trendingNews.slice(0, 12).map((article) => (
              <NewsCard
                key={article.id}
                article={article}
                onInteraction={handleNewsInteraction}
              />
            ))
          )}
        </div>

        {/* Categories Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Explore Categories</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {categories.map((category) => (
              <Link
                key={category.id}
                to={`/category/${category.id}`}
                className="group bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-primary-300 transition-all duration-200"
              >
                <div className="text-center">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {category.name}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {category.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Why Choose NARAYANASWAMY SONS News Platform?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI-Powered Recommendations
              </h3>
              <p className="text-gray-600">
                Our advanced machine learning model learns from your reading habits to deliver personalized news recommendations.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Real-Time Updates
              </h3>
              <p className="text-gray-600">
                Stay up-to-date with breaking news and trending stories from trusted sources around the world.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Rss className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Diverse Sources
              </h3>
              <p className="text-gray-600">
                Access news from multiple reputable sources including Reuters, BBC, TechCrunch, and many more.
              </p>
            </div>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg">
                  <Newspaper className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">NARAYANASWAMY SONS</h3>
                  <p className="text-gray-400 text-sm">News Intelligence Platform</p>
                </div>
              </div>
              <p className="text-gray-400 mb-4">
                Advanced AI-powered news intelligence platform delivering personalized, 
                real-time news recommendations from trusted global sources.
              </p>
              <p className="text-sm text-gray-500">
                © 2024 Narayanaswamy Sons. All rights reserved.
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-gray-400">
                <li>AI Recommendations</li>
                <li>Real-time Updates</li>
                <li>Multi-source News</li>
                <li>Personalization</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>About Us</li>
                <li>Technology</li>
                <li>Privacy Policy</li>
                <li>Terms of Service</li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage