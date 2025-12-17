import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class NewsService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/news`
  }

  async getTrendingNews(limit = 20, category = null) {
    try {
      const params = { limit }
      if (category) params.category = category

      const response = await axios.get(`${this.baseURL}/trending`, { params })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getNewsByCategory(category, limit = 20, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/category/${category}`, {
        params: { limit },
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async searchNews(query, limit = 20, category = null) {
    try {
      const params = { q: query, limit }
      if (category) params.category = category

      const response = await axios.get(`${this.baseURL}/search`, { params })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getArticle(articleId, authHeaders = {}) {
    try {
      const response = await axios.get(`${this.baseURL}/article/${articleId}`, {
        headers: authHeaders
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async logInteraction(articleId, interactionType, duration = null, authHeaders = {}) {
    try {
      const params = { interaction_type: interactionType }
      if (duration !== null) params.duration = duration

      const response = await axios.post(
        `${this.baseURL}/article/${articleId}/interact`,
        {},
        {
          params,
          headers: authHeaders
        }
      )
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getCategories() {
    try {
      const response = await axios.get(`${this.baseURL}/categories`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getSources() {
    try {
      const response = await axios.get(`${this.baseURL}/sources`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getNewsStats() {
    try {
      const response = await axios.get(`${this.baseURL}/stats`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async refreshNews() {
    try {
      const response = await axios.post(`${this.baseURL}/refresh`)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export const newsService = new NewsService()