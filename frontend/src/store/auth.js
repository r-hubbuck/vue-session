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
    // Recruiter convention registration (fetched on demand, not persisted)
    recruiterRegistration: null,
  }),
  
  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated,
    
    // Get user roles as an array
    userRoles: (state) => state.user?.roles || [],
    
    // Helper to check if user has a specific role
    hasRole: (state) => (roleName) => {
      return state.user?.roles?.includes(roleName) || false
    },
    
    // Role checking getters
    isMember: (state) => state.user?.roles?.includes('member') || false,
    isAlumni: (state) => state.user?.roles?.includes('alumni') || false,
    isCollegiateOfficer: (state) => state.user?.roles?.includes('collegiate_officer') || false,
    isAlumniOfficer: (state) => state.user?.roles?.includes('alumni_officer') || false,
    
    // National officials
    isDistrictDirector: (state) => state.user?.roles?.includes('district_director') || false,
    isExecutiveCouncil: (state) => state.user?.roles?.includes('executive_council') || false,
    
    // HQ Staff
    isHQStaff: (state) => state.user?.roles?.includes('hq_staff') || false,
    isHQIT: (state) => state.user?.roles?.includes('hq_it') || false,
    isHQFinance: (state) => state.user?.roles?.includes('hq_finance') || false,
    isHQRecruiting: (state) => state.user?.roles?.includes('hq_recruiting') || false,
    isHQConventionTravel: (state) => state.user?.roles?.includes('hq_convention_travel') || false,

    // Recruiter
    isRecruiter: (state) => state.user?.roles?.includes('recruiter') || false,
    userType: (state) => state.user?.roles?.includes('recruiter') ? 'recruiter' : 'member',
    canAccessResumes: (state) => {
      const reg = state.recruiterRegistration
      return !!(reg && reg.status === 'confirmed' && reg.booth_package_detail?.includes_resume_access)
    },
    
    // Convenience getters for permission checks
    isAnyMember: (state) => {
      // Check if user has member OR alumni role
      const roles = state.user?.roles || []
      return roles.includes('member') || roles.includes('alumni')
    },
    
    isAnyOfficer: (state) => {
      // Check if user is any type of officer
      const roles = state.user?.roles || []
      return roles.includes('collegiate_officer') || 
             roles.includes('alumni_officer') ||
             roles.includes('district_director') ||
             roles.includes('executive_council')
    },
    
    canAccessConvention: (state) => {
      // Members and alumni can access convention
      const roles = state.user?.roles || []
      return roles.includes('member') || roles.includes('alumni')
    },
    
    canManageFinances: (state) => {
      // HQ finance staff and executive council can manage finances
      const roles = state.user?.roles || []
      return roles.includes('hq_finance') || roles.includes('executive_council')
    },
    
    canManageChapter: (state) => {
      // Chapter officers can manage their chapter
      const roles = state.user?.roles || []
      return roles.includes('collegiate_officer') || roles.includes('alumni_officer')
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
            // Route recruiters to their dashboard
            if (this.user?.roles?.includes('recruiter')) {
              await router.push({ name: 'recruiter-dashboard' })
            } else {
              await router.push({ name: 'home' })
            }
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

    async fetchRecruiterRegistration() {
      try {
        const response = await api.get('/api/recruiters/convention/my-registration/')
        this.recruiterRegistration = response.data?.id ? response.data : null
      } catch {
        this.recruiterRegistration = null
      }
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
