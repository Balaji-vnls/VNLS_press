import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class AuthService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/auth`
  }

  async signUp(email, password, fullName = '', preferences = {}) {
    try {
      const response = await axios.post(`${this.baseURL}/signup`, {
        email,
        password,
        full_name: fullName,
        preferences
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async resendVerification(email) {
    try {
      const response = await axios.post(`${this.baseURL}/resend-verification`, {
        email
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async signIn(email, password) {
    try {
      const response = await axios.post(`${this.baseURL}/signin`, {
        email,
        password
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async signOut(accessToken) {
    try {
      const response = await axios.post(`${this.baseURL}/signout`, {}, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async refreshToken(refreshToken) {
    try {
      const response = await axios.post(`${this.baseURL}/refresh-token`, {
        refresh_token: refreshToken
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getCurrentUser(accessToken) {
    try {
      const response = await axios.get(`${this.baseURL}/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return response.data.user
    } catch (error) {
      console.error('Get current user error:', error)
      return null
    }
  }

  async updateUser(accessToken, updates) {
    try {
      const response = await axios.put(`${this.baseURL}/me`, {
        user_metadata: updates
      }, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return { success: true, data: response.data }
    } catch (error) {
      throw error
    }
  }

  async resetPassword(email) {
    try {
      const response = await axios.post(`${this.baseURL}/reset-password`, {
        email
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async getUserPreferences(accessToken) {
    try {
      const response = await axios.get(`${this.baseURL}/preferences`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  }
}

export const authService = new AuthService()