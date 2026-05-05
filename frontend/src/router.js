import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './store/auth'

// All pages lazy-loaded — split into per-route chunks at build time
const Home              = () => import('./pages/Home.vue')
const Login             = () => import('./pages/Login.vue')
const Register          = () => import('./pages/Register.vue')
const Verify            = () => import('./pages/Verify.vue')
const EmailConfirmation = () => import('./pages/EmailConfirmation.vue')
const CodeCheck         = () => import('./pages/CodeCheck.vue')
const PasswordForgot    = () => import('./pages/PasswordForgot.vue')
const PasswordResetConfirm = () => import('./pages/PasswordResetConfirm.vue')
const EmailLinkError    = () => import('./pages/EmailLinkError.vue')
const UserAccount       = () => import('./pages/UserAccount.vue')
const ConventionHome    = () => import('./pages/convention/ConventionHome.vue')
const ConventionTravel  = () => import('./pages/convention/ConventionTravel.vue')
const ConventionCheckIn = () => import('./pages/convention/ConventionCheckIn.vue')
const ExpenseReport     = () => import('./pages/ExpenseReport.vue')
const ExpenseReportAdmin = () => import('./pages/ExpenseReportAdmin.vue')
const RecruiterRegister  = () => import('./pages/recruiter/RecruiterRegister.vue')
const RecruiterDashboard = () => import('./pages/recruiter/RecruiterDashboard.vue')
const RecruiterAccount   = () => import('./pages/recruiter/RecruiterAccount.vue')
const RecruiterConvention = () => import('./pages/recruiter/RecruiterConvention.vue')
const RecruiterResumes   = () => import('./pages/recruiter/RecruiterResumes.vue')
const RecruiterInvoices  = () => import('./pages/recruiter/RecruiterInvoices.vue')
const RecruiterAdmin     = () => import('./pages/recruiter/RecruiterAdmin.vue')
const InvoiceAdmin       = () => import('./pages/recruiter/InvoiceAdmin.vue')
const SurveyList    = () => import('./pages/surveys/SurveyList.vue')
const SurveyTake    = () => import('./pages/surveys/SurveyTake.vue')
const SurveyBuilder = () => import('./pages/surveys/SurveyBuilder.vue')
const SurveyResults = () => import('./pages/surveys/SurveyResults.vue')
const SurveyAdmin   = () => import('./pages/surveys/SurveyAdmin.vue')
const NotFound      = () => import('./pages/NotFound.vue')
const UserManagement = () => import('./pages/UserManagement.vue')

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
    path: '/user-management',
    name: 'user-management',
    component: UserManagement,
    meta: { requiresAuth: true, requiresRoles: ['hq_admin'] }
  },
  {
    path: '/admin/users/:userId',
    name: 'admin-user-account',
    component: UserAccount,
    meta: { requiresAuth: true, requiresRoles: ['hq_admin'] }
  },
  {
    path: '/convention',
    name: 'convention-home',
    component: ConventionHome,
    meta: { requiresAuth: true }
  },
  {
    path: '/expense-report',
    name: 'expense-report',
    component: ExpenseReport,
    meta: { requiresAuth: true }
  },
  {
    path: '/expense-report-admin',
    name: 'expense-report-admin',
    component: ExpenseReportAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_admin', 'hq_finance']
    }
  },
  {
    path: '/convention-check-in',
    name: 'ConventionCheckIn',
    component: ConventionCheckIn,
    meta: { 
      requiresAuth: true,
      requiresRoles: ['hq_staff']
    }
  },
  {
  path: '/convention-travel',
  name: 'convention-travel',
  component: ConventionTravel,
  meta: { 
    requiresAuth: true,
    requiresRoles: ['hq_admin', 'hq_convention_travel']
  }
},
  // Recruiter routes
  {
    path: '/recruiter/account',
    name: 'recruiter-account',
    component: RecruiterAccount,
    meta: { requiresAuth: true, requiresRoles: ['recruiter'] }
  },
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
    path: '/recruiter/resumes',
    name: 'recruiter-resumes',
    component: RecruiterResumes,
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
      requiresRoles: ['hq_recruiting', 'hq_admin']
    }
  },
  {
    path: '/invoice-admin',
    name: 'invoice-admin',
    component: InvoiceAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_finance', 'hq_admin']
    }
  },
  // Survey routes
  {
    path: '/surveys/admin',
    name: 'survey-admin',
    component: SurveyAdmin,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff']
    }
  },
  {
    path: '/surveys/admin/builder',
    name: 'survey-builder',
    component: SurveyBuilder,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff']
    }
  },
  {
    path: '/surveys/admin/builder/:id',
    name: 'survey-builder-edit',
    component: SurveyBuilder,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff']
    }
  },
  {
    path: '/surveys/admin/:id/results',
    name: 'survey-results',
    component: SurveyResults,
    meta: {
      requiresAuth: true,
      requiresRoles: ['hq_staff']
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
  if (to.meta.requiresVerification && !authStore.hasValidVerification) {
    authStore.serverMessage = 'Please verify your membership before registering.'
    return next({ name: 'verify' })
  }

  // Fetch current user for all authenticated routes (60s cache — negligible overhead).
  // This must happen before the recruiter confinement check so isRecruiter reflects
  // actual server-side roles rather than potentially stale startup state.
  if (authStore.isAuthenticated && to.meta.requiresAuth) {
    await authStore.fetchUser()
    if (!authStore.isAuthenticated) {
      return next({ name: 'login' })
    }
  }

  // Recruiters are confined to their own section — explicit allowlist avoids matching /recruiter-admin
  const RECRUITER_PATHS = [
    '/recruiter/dashboard',
    '/recruiter/convention',
    '/recruiter/resumes',
    '/recruiter/invoices',
    '/recruiter/account',
  ]
  if (authStore.isAuthenticated && authStore.isRecruiter &&
      !RECRUITER_PATHS.some(p => to.path.startsWith(p))) {
    return next({ name: 'recruiter-dashboard' })
  }

  // Check role requirements (fetchUser already called above for requiresAuth routes)
  if (to.meta.requiresRoles && authStore.isAuthenticated) {
    const userRoles = authStore.userRoles
    const requiredRoles = to.meta.requiresRoles
    const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role))

    if (!hasRequiredRole) {
      console.warn('Access denied: insufficient role for route', to.name)
      return next({
        name: 'home',
        query: { error: 'You do not have permission to access that page.' }
      })
    }
  }

  // Check if route requires member status (any member type)
  if (to.meta.requiresMember) {
    if (!authStore.isMember) {
      console.warn('Access denied: membership required for route', to.name)
      return next({
        name: 'home',
        query: { error: 'This page is only available to TBP members.' }
      })
    }
  }

  next()
})

export default router
