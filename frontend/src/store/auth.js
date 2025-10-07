import { defineStore } from 'pinia'
import api from '../api'

const getStoredState = () => {
  const storedState = localStorage.getItem('authState')
  return storedState
    ? JSON.parse(storedState)
    : {
        user: null,
        isAuthenticated: false,
      }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    serverMessage: null,
    // Verification state
    isVerified: false,
    verificationTimestamp: null,
    verificationEmail: null, // Store the verified email
  }),
  
  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated,
    
    // Check if verification is still valid (expires after 15 minutes)
    hasValidVerification: (state) => {
      if (!state.isVerified || !state.verificationTimestamp) {
        return false
      }
      
      const now = Date.now()
      const fifteenMinutes = 15 * 60 * 1000
      const elapsed = now - state.verificationTimestamp
      
      return elapsed < fifteenMinutes
    },
  },
  
  actions: {
    clearMessage() {
      this.serverMessage = null
    },

    setVerified(email) {
      this.isVerified = true
      this.verificationTimestamp = Date.now()
      this.verificationEmail = email
    },

    clearVerification() {
      this.isVerified = false
      this.verificationTimestamp = null
      this.verificationEmail = null
    },

    async setCsrfToken() {
      try {
        await api.get('/api/set-csrf-token')
      } catch (error) {
        console.error('Failed to set CSRF token', error)
      }
    },

    async login(email, password, router = null) {
      try {
        const response = await api.post('/api/login', { email, password })
        this.serverMessage = response.data.message
        
        if (response.data.success) {
          this.saveState()
          if (router) {
            await router.push({ name: 'code-check' })
          }
        } else {
          this.user = null
          this.isAuthenticated = false
          this.saveState()
        }
      } catch (error) {
        console.error('Login failed', error)
        this.serverMessage = error.response?.data?.message || 'Login failed'
        this.user = null
        this.isAuthenticated = false
        this.saveState()
      }
    },

    async verify(code, router = null) {
      try {
        const response = await api.post('/api/code-check', { code })
        
        if (response.data.success) {
          this.isAuthenticated = true
          
          if (router) {
            await router.push({ name: 'home' })
          }
        }
      } catch (error) {
        console.error('Verification failed', error)
        throw error
      }
    },

    async logout(router = null) {
      try {
        await api.post('/api/logout')
        this.user = null
        this.isAuthenticated = false
        this.clearVerification() // Clear verification on logout
        this.saveState()
        
        if (router) {
          await router.push({ name: 'login' })
        }
      } catch (error) {
        console.error('Logout failed', error)
        throw error
      }
    },

    async fetchUser() {
      try {
        const response = await api.get('/api/user')
        this.user = response.data
        this.isAuthenticated = true
      } catch (error) {
        console.error('Failed to fetch user', error)
        this.user = null
        this.isAuthenticated = false
      }
      this.saveState()
    },

    saveState() {
      localStorage.setItem(
        'authState',
        JSON.stringify({
          user: this.user,
          isAuthenticated: this.isAuthenticated,
        })
      )
    },
  },
})

// Export getCSRFToken for use in other files if needed
export { getCSRFToken } from '../api'