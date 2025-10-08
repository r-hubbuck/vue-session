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
  }
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

  next()
})

export default router