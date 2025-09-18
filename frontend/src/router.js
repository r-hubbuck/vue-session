import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Verify from './pages/Verify.vue'
import RegisterConfirmation from './pages/RegisterConfirmation.vue'
import CodeCheck from './pages/CodeCheck.vue'
import AddressList from './pages/AddressList.vue'
import { useAuthStore } from './store/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
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
  },
  {
    path: '/verify',
    name: 'verify',
    component: Verify,
  },
  {
    path: '/register-confirmation',
    name: 'register-confirmation',
    component: RegisterConfirmation,
  },
  {
    path: '/code-check',
    name: 'code-check',
    component: CodeCheck,
  },
  {
    path: '/addresses',
    name: 'addresses',
    component: AddressList,
  },
]

const router = createRouter({
  history: createWebHistory('/'),
  // history: createWebHistory('/portal/'),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.name == 'home' && !authStore.isAuthenticated) next({ name: 'login' })
  else next()
})

export default router