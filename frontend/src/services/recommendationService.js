import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class RecommendationService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/recommendations`
  }

  async getPersonalizedRecommendations(limit = 20, category = null, authHeaders = {}) {
    try {
      const params = { limit }
      if (category) params.category = category

      const response = await axios.get(`${this.baseURL}/personalized`, {
        params,
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getForYouFeed(limit = 20, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/for-you`, {
        params: { limit },
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getSimilarArticles(articleId, limit = 10, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/similar/${articleId}`, {
        params: { limit },
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getTrendingRecommendations(limit = 20, category = null) {
    try {
      const params = { limit }
      if (category) params.category = category

      const response = await axios.get(`${this.baseURL}/trending`, { params })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getCategoryRecommendations(category, limit = 20, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/categories/${category}`, {
        params: { limit },
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRecommendationHistory(limit = 50, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/history`, {
        params: { limit },
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getRecommendationPreferences(authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/preferences`, {
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async submitFeedback(articleId, feedbackType, authHeaders = {}) {
    try {
      const response = await axios.post(
        `${this.baseURL}/feedback`,
        {},
        {
          params: {
            article_id: articleId,
            feedback_type: feedbackType
          },
          headers: authHeaders
        }
      )
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export const recommendationService = new RecommendationService()