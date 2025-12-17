import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import { User, Settings, BarChart3, Clock, Heart } from 'lucide-react'
import toast from 'react-hot-toast'

const ProfilePage = () => {
  const { user, updateProfile, loading } = useAuth()
  const [preferences, setPreferences] = useState({
    categories: [],
    notifications: true,
    emailUpdates: false
  })
  const [stats, setStats] = useState({
    articlesRead: 42,
    timeSpent: '2h 15m',
    favoriteCategory: 'Technology',
    streak: 7
  })

  useEffect(() => {
    if (user?.user_metadata?.preferences) {
      setPreferences(user.user_metadata.preferences)
    } else if (user?.preferences) {
      setPreferences(user.preferences)
    }
  }, [user])

  const categories = [
    { id: 'technology', name: 'Technology', emoji: '💻' },
    { id: 'business', name: 'Business', emoji: '💼' },
    { id: 'health', name: 'Health', emoji: '🏥' },
    { id: 'science', name: 'Science', emoji: '🔬' },
    { id: 'general', name: 'General', emoji: '📰' },
    { id: 'sports', name: 'Sports', emoji: '⚽' },
    { id: 'entertainment', name: 'Entertainment', emoji: '🎬' }
  ]

  const handleCategoryToggle = (categoryId) => {
    setPreferences(prev => ({
      ...prev,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter(id => id !== categoryId)
        : [...prev.categories, categoryId]
    }))
  }

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const [saving, setSaving] = useState(false)

  const handleSavePreferences = async () => {
    try {
      setSaving(true)
      const result = await updateProfile(preferences)
      if (result && result.success) {
        toast.success('Preferences saved successfully!')
      } else {
        toast.success('Preferences updated!')
      }
    } catch (error) {
      console.error('Save preferences error:', error)
      toast.error('Failed to save preferences')
    } finally {
      setSaving(false)
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center">
              <User className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {user?.email?.split('@')[0] || 'User'}
              </h1>
              <p className="text-gray-600">{user?.email}</p>
              <p className="text-sm text-gray-500">
                Member since {new Date(user?.created_at || Date.now()).toLocaleDateString()}
              </p>
              {user?.email_verified && (
                <p className="text-xs text-green-600 font-medium">✅ Email Verified</p>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Stats */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Reading Stats
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">📚</span>
                    </div>
                    <span className="text-sm text-gray-600">Articles Read</span>
                  </div>
                  <span className="font-semibold text-gray-900">{stats.articlesRead}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Clock className="h-4 w-4 text-green-600" />
                    </div>
                    <span className="text-sm text-gray-600">Time Spent</span>
                  </div>
                  <span className="font-semibold text-gray-900">{stats.timeSpent}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <Heart className="h-4 w-4 text-purple-600" />
                    </div>
                    <span className="text-sm text-gray-600">Favorite Category</span>
                  </div>
                  <span className="font-semibold text-gray-900">{stats.favoriteCategory}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="h-8 w-8 bg-orange-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-orange-600">🔥</span>
                    </div>
                    <span className="text-sm text-gray-600">Reading Streak</span>
                  </div>
                  <span className="font-semibold text-gray-900">{stats.streak} days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Preferences
              </h2>

              {/* Category Preferences */}
              <div className="mb-8">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  Interested Categories
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Select the categories you're most interested in to get better recommendations.
                </p>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => handleCategoryToggle(category.id)}
                      className={`flex items-center space-x-2 p-3 rounded-lg border-2 transition-all ${
                        preferences.categories.includes(category.id)
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      <span className="text-lg">{category.emoji}</span>
                      <span className="text-sm font-medium">{category.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Notification Preferences */}
              <div className="mb-8">
                <h3 className="text-md font-medium text-gray-900 mb-4">
                  Notifications
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-900">
                        Push Notifications
                      </label>
                      <p className="text-sm text-gray-600">
                        Get notified about breaking news and personalized recommendations
                      </p>
                    </div>
                    <button
                      onClick={() => handlePreferenceChange('notifications', !preferences.notifications)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        preferences.notifications ? 'bg-primary-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          preferences.notifications ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-900">
                        Email Updates
                      </label>
                      <p className="text-sm text-gray-600">
                        Receive weekly digest of your personalized news
                      </p>
                    </div>
                    <button
                      onClick={() => handlePreferenceChange('emailUpdates', !preferences.emailUpdates)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        preferences.emailUpdates ? 'bg-primary-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          preferences.emailUpdates ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Save Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleSavePreferences}
                  disabled={loading || saving}
                  className="btn-primary"
                >
                  {(loading || saving) ? <LoadingSpinner size="sm" /> : 'Save Preferences'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage