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
import RecruiterRegister from './pages/recruiter/RecruiterRegister.vue'
import RecruiterDashboard from './pages/recruiter/RecruiterDashboard.vue'
import RecruiterConvention from './pages/recruiter/RecruiterConvention.vue'
import RecruiterAttendees from './pages/recruiter/RecruiterAttendees.vue'
import RecruiterInvoices from './pages/recruiter/RecruiterInvoices.vue'
import RecruiterAdmin from './pages/recruiter/RecruiterAdmin.vue'
import InvoiceAdmin from './pages/recruiter/InvoiceAdmin.vue'
import SurveyList from './pages/surveys/SurveyList.vue'
import SurveyTake from './pages/surveys/SurveyTake.vue'
import SurveyBuilder from './pages/surveys/SurveyBuilder.vue'
import SurveyResults from './pages/surveys/SurveyResults.vue'
import SurveyAdmin from './pages/surveys/SurveyAdmin.vue'
import NotFound from './pages/NotFound.vue'

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
      requiresRoles: ['member', 'alumni']
    }
  },
  {
    path: '/expense-report',
    name: 'expense-report',
    component: ExpenseReport,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['member', 'alumni', 'collegiate_officer', 'alumni_officer']
    }
  },
  {
    path: '/expense-report-admin',
    name: 'expense-report-admin',
    component: ExpenseReportAdmin,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_finance', 'member']
    }
  },
  {
    path: '/convention-check-in',
    name: 'ConventionCheckIn',
    component: ConventionCheckIn,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'member']
    }
  },
  {
  path: '/convention-travel',
  name: 'convention-travel',
  component: ConventionTravel,
  meta: { 
    requiresAuth: true,
    requiresRoles: ['hq_staff', 'member']
  }
},
  // Recruiter routes
  {
    path: '/recruiter/register',
    name: 'recruiter-register',
    component: RecruiterRegister,
  },
  {
    path: '/recruiter/dashboard',
    name: 'recruiter-dashboard',
    component: RecruiterDashboard,
    meta: {
      requiresAuth: true,
      requiresRoles: ['recruiter']
    }
  },
  {
    path: '/recruiter/convention',
    name: 'recruiter-convention',
    component: RecruiterConvention,
    meta: {
      requiresAuth: true,
      requiresRoles: ['recruiter']
    }
  },
  {
    path: '/recruiter/attendees',
    name: 'recruiter-attendees',
    component: RecruiterAttendees,
    meta: {
      requiresAuth: true,
      requiresRoles: ['recruiter']
    }
  },
  {
    path: '/recruiter/invoices',
    name: 'recruiter-invoices',
    component: RecruiterInvoices,
    meta: {
      requiresAuth: true,
      requiresRoles: ['recruiter']
    }
  },
  {
    path: '/recruiter-admin',
    name: 'recruiter-admin',
    component: RecruiterAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_admin']
    }
  },
  {
    path: '/invoice-admin',
    name: 'invoice-admin',
    component: InvoiceAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_finance', 'hq_admin']
    }
  },
  // Survey routes
  {
    path: '/surveys/admin',
    name: 'survey-admin',
    component: SurveyAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']
    }
  },
  {
    path: '/surveys/admin/builder',
    name: 'survey-builder',
    component: SurveyBuilder,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']
    }
  },
  {
    path: '/surveys/admin/builder/:id',
    name: 'survey-builder-edit',
    component: SurveyBuilder,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']
    }
  },
  {
    path: '/surveys/admin/:id/results',
    name: 'survey-results',
    component: SurveyResults,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']
    }
  },
  {
    path: '/surveys',
    name: 'survey-list',
    component: SurveyList,
    meta: { requiresAuth: true }
  },
  {
    path: '/surveys/:id/take',
    name: 'survey-take',
    component: SurveyTake,
    meta: { requiresAuth: true }
  },
  // Catch-all: redirect unauthenticated users to login, show 404 for authenticated users
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: { requiresAuth: true }
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

router.beforeEach(async (to, from, next) => {
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

  // For role-protected routes, verify roles with the backend first
  if (to.meta.requiresRoles && authStore.isAuthenticated) {
    await authStore.fetchUser()

    if (!authStore.isAuthenticated) {
      return next({ name: 'login' })
    }

    const userRoles = authStore.userRoles
    const requiredRoles = to.meta.requiresRoles

    // Check if user has ANY of the required roles
    const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role))

    if (!hasRequiredRole) {
      console.warn('Access denied: insufficient role for route', to.name)
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
      console.warn('Access denied: membership required for route', to.name)
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
