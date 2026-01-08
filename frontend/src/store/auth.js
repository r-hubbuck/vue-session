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
    ...getStoredState(),  // ✅ FIXED: Load saved auth state from localStorage
    serverMessage: null,
    // Verification state
    isVerified: false,
    verificationTimestamp: null,
    verificationEmail: null, // Store the verified email
  }),
  
  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated,
    
    // Get user role
    userRole: (state) => state.user?.role || 'non-member',
    
    // Role checking getters
    isNonMember: (state) => state.user?.role === 'non-member',
    isCollegiate: (state) => state.user?.role === 'collegiate',
    isAlumni: (state) => state.user?.role === 'alumni',
    isOfficial: (state) => state.user?.role === 'official',
    
    // Convenience getters for permission checks
    isMember: (state) => {
      const role = state.user?.role
      return role === 'collegiate' || role === 'alumni' || role === 'official'
    },
    
    canAccessConvention: (state) => {
      // Example: only collegiate and officials can access convention
      const role = state.user?.role
      return role === 'collegiate' || role === 'official'
    },
    
    canManageChapter: (state) => {
      // Example: only officials can manage chapter
      return state.user?.role === 'official'
    },
    
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
        await api.get('/api/accounts/set-csrf-token')
      } catch (error) {
        console.error('Failed to set CSRF token', error)
      }
    },

    async login(email, password, router = null) {
      try {
        const response = await api.post('/api/accounts/login', { email, password })
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
        const response = await api.post('/api/accounts/code-check', { code })
        
        if (response.data.success) {
          this.isAuthenticated = true
          
          // Fetch user data after successful verification to get role
          await this.fetchUser()
          
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
        await api.post('/api/accounts/logout')
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
        const response = await api.get('/api/accounts/user')
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
