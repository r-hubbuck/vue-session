import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Verify from './pages/Verify.vue'
import EmailConfirmation from './pages/EmailConfirmation.vue'
import CodeCheck from './pages/CodeCheck.vue'
import PasswordForgot from './pages/PasswordForgot.vue'
import PasswordResetConfirm from './pages/PasswordResetConfirm.vue'
import EmailLinkError from './pages/EmailLinkError.vue'
import { useAuthStore } from './store/auth'
import UserAccount from './pages/UserAccount.vue'
import ConventionHome from './pages/convention/ConventionHome.vue'
import ConventionTravel from './pages/convention/ConventionTravel.vue'
import ConventionCheckIn from './pages/convention/ConventionCheckIn.vue'
import ExpenseReport from './pages/ExpenseReport.vue'
import ExpenseReportAdmin from './pages/ExpenseReportAdmin.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresVerification: true }
  },
  {
    path: '/verify',
    name: 'verify',
    component: Verify,
  },
  {
    path: '/email-confirmation',
    name: 'email-confirmation',
    component: EmailConfirmation,
  },
  {
    path: '/code-check',
    name: 'code-check',
    component: CodeCheck,
  },
  {
    path: '/password-forgot',
    name: 'password-forgot',
    component: PasswordForgot,
  },
  {
    path: '/email-link-error',
    name: 'email-link-error',
    component: EmailLinkError,
  },
  {
    path: '/password-reset-confirm/:uidb64/:token',
    name: 'password-reset-confirm',
    component: PasswordResetConfirm,
  },
  {
    path: '/account',
    name: 'account',
    component: UserAccount,
    meta: { requiresAuth: true }
  },
  {
    path: '/convention',
    name: 'convention-home',
    component: ConventionHome,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['collegiate', 'official', 'non-member', 'alumni'] // Example: only collegiate and officials can access
    }
  },
  {
    path: '/expense-report',
    name: 'expense-report',
    component: ExpenseReport,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['collegiate', 'official', 'non-member', 'alumni']
    }
  },
  {
    path: '/expense-report-admin',
    name: 'expense-report-admin',
    component: ExpenseReportAdmin,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['collegiate', 'official', 'non-member', 'alumni']
    }
  },
  {
    path: '/convention-check-in',
    name: 'ConventionCheckIn',
    component: ConventionCheckIn,
    meta: { requiresAuth: true, requiresStaff: true }
  },
  {
  path: '/convention-travel',
  name: 'convention-travel',
  component: ConventionTravel,
  meta: { 
    requiresAuth: true,
    // Optional: Add role restriction if you want only certain users
    // requiresRoles: ['official'] // Only officials can access
  }
},
  // Example: Route only for officials
  // {
  //   path: '/admin',
  //   name: 'admin',
  //   component: () => import('./pages/Admin.vue'), // Lazy load
  //   meta: { 
  //     requiresAuth: true,
  //     requiresRoles: ['official']
  //   }
  // },
  // Example: Route for any member (not non-members)
  // {
  //   path: '/members',
  //   name: 'members',
  //   component: () => import('./pages/Members.vue'),
  //   meta: { 
  //     requiresAuth: true,
  //     requiresMember: true // Uses the isMember getter
  //   }
  // }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  // Check if route requires verification (for registration)
  if (to.meta.requiresVerification) {
    if (!authStore.hasValidVerification) {
      // Redirect to verify page with a message
      authStore.serverMessage = 'Please verify your membership before registering.'
      return next({ name: 'verify' })
    }
  }

  // Check if route requires specific roles
  if (to.meta.requiresRoles) {
    const userRole = authStore.userRole
    const requiredRoles = to.meta.requiresRoles
    
    if (!requiredRoles.includes(userRole)) {
      // User doesn't have the required role, redirect to home with message
      console.warn(`Access denied: User role '${userRole}' not in required roles ${requiredRoles}`)
      return next({ 
        name: 'home', 
        query: { 
          error: 'You do not have permission to access that page.' 
        }
      })
    }
  }

  // Check if route requires member status (any member type)
  if (to.meta.requiresMember) {
    if (!authStore.isMember) {
      console.warn('Access denied: User is not a member')
      return next({ 
        name: 'home', 
        query: { 
          error: 'This page is only available to TBP members.' 
        }
      })
    }
  }

  next()
})

export default router
