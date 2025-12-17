import React, { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/authService'
import toast from 'react-hot-toast'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [session, setSession] = useState(null)

  useEffect(() => {
    // Check for existing session on app load
    const initializeAuth = async () => {
      try {
        const savedSession = localStorage.getItem('newsai_session')
        if (savedSession) {
          const sessionData = JSON.parse(savedSession)
          
          // Verify token is still valid
          const userInfo = await authService.getCurrentUser(sessionData.access_token)
          if (userInfo) {
            setUser(userInfo)
            setSession(sessionData)
          } else {
            // Token expired, clear storage
            localStorage.removeItem('newsai_session')
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        localStorage.removeItem('newsai_session')
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()
  }, [])

  const signUp = async (email, password, fullName = '', preferences = {}) => {
    try {
      setLoading(true)
      const response = await authService.signUp(email, password, fullName, preferences)
      
      if (response.email_sent) {
        toast.success('Account created! Please check your email to verify your account.')
        return { success: true, email_sent: true, message: response.message }
      } else if (response.user && response.session) {
        setUser(response.user)
        setSession(response.session)
        localStorage.setItem('newsai_session', JSON.stringify(response.session))
        toast.success('Account created successfully!')
        return { success: true }
      } else {
        throw new Error('Failed to create account')
      }
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to create account'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email, password) => {
    try {
      setLoading(true)
      const response = await authService.signIn(email, password)
      
      if (response.success && response.user && response.session) {
        setUser(response.user)
        setSession(response.session)
        localStorage.setItem('newsai_session', JSON.stringify(response.session))
        toast.success('Signed in successfully!')
        return { success: true }
      } else if (response.success === false && !response.email_verified) {
        return { 
          success: false, 
          email_verified: false, 
          message: response.message,
          resend_verification: response.resend_verification 
        }
      } else {
        throw new Error('Invalid credentials')
      }
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to sign in'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    try {
      if (session?.access_token) {
        await authService.signOut(session.access_token)
      }
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      setUser(null)
      setSession(null)
      localStorage.removeItem('newsai_session')
      toast.success('Signed out successfully')
    }
  }

  const updateProfile = async (updates) => {
    try {
      if (!session?.access_token) {
        throw new Error('Not authenticated')
      }

      const response = await authService.updateUser(session.access_token, updates)
      
      if (response.success) {
        // Refresh user data
        const userInfo = await authService.getCurrentUser(session.access_token)
        if (userInfo) {
          setUser(userInfo)
        }
        toast.success('Profile updated successfully!')
        return { success: true }
      } else {
        throw new Error('Failed to update profile')
      }
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to update profile'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const refreshToken = async () => {
    try {
      if (!session?.refresh_token) {
        throw new Error('No refresh token available')
      }

      const response = await authService.refreshToken(session.refresh_token)
      
      if (response.session) {
        setSession(response.session)
        localStorage.setItem('newsai_session', JSON.stringify(response.session))
        return response.session
      } else {
        throw new Error('Failed to refresh token')
      }
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, sign out user
      await signOut()
      return null
    }
  }

  const getAuthHeaders = () => {
    if (session?.access_token) {
      return {
        'Authorization': `Bearer ${session.access_token}`
      }
    }
    return {}
  }

  const isAuthenticated = () => {
    return !!(user && session?.access_token)
  }

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    updateProfile,
    refreshToken,
    getAuthHeaders,
    isAuthenticated
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}