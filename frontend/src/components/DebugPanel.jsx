import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { newsService } from '../services/newsService'
import { Bug, RefreshCw, User, Database } from 'lucide-react'
import toast from 'react-hot-toast'

const DebugPanel = () => {
  const { user, session, isAuthenticated, signOut } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [testing, setTesting] = useState(false)

  const testRefresh = async () => {
    try {
      setTesting(true)
      const result = await newsService.refreshNews()
      toast.success(`Refresh successful! ${result.articles_count} articles`)
    } catch (error) {
      toast.error('Refresh failed: ' + error.message)
    } finally {
      setTesting(false)
    }
  }

  const testSignOut = async () => {
    try {
      await signOut()
      toast.success('Sign out successful!')
    } catch (error) {
      toast.error('Sign out failed: ' + error.message)
    }
  }

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gray-800 text-white p-3 rounded-full shadow-lg hover:bg-gray-700 transition-colors"
        >
          <Bug className="h-5 w-5" />
        </button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-4 w-80 max-h-96 overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Debug Panel</h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-400 hover:text-gray-600"
        >
          ×
        </button>
      </div>

      {/* Authentication Status */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <User className="h-4 w-4 mr-1" />
          Authentication
        </h4>
        <div className="text-xs space-y-1">
          <div>Status: {isAuthenticated() ? '✅ Authenticated' : '❌ Not authenticated'}</div>
          {user && (
            <>
              <div>Email: {user.email}</div>
              <div>Verified: {user.email_verified ? '✅ Yes' : '❌ No'}</div>
              <div>ID: {user.id?.substring(0, 8)}...</div>
            </>
          )}
          {session && (
            <div>Token: {session.access_token?.substring(0, 20)}...</div>
          )}
        </div>
      </div>

      {/* Test Buttons */}
      <div className="space-y-2">
        <button
          onClick={testRefresh}
          disabled={testing}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${testing ? 'animate-spin' : ''}`} />
          <span>Test Refresh</span>
        </button>

        {isAuthenticated() && (
          <button
            onClick={testSignOut}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            <Database className="h-4 w-4" />
            <span>Test Sign Out</span>
          </button>
        )}
      </div>

      {/* System Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">System Info</h4>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Frontend: http://localhost:3001</div>
          <div>Backend: http://localhost:8000</div>
          <div>Company: Narayanaswamy Sons</div>
        </div>
      </div>
    </div>
  )
}

export default DebugPanel