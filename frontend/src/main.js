import { createApp } from 'vue'
import { createPinia } from 'pinia'
// import './style.css'

import router from './router'
import App from './App.vue'
import { useAuthStore } from './store/auth'

import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, {
  position: "top-right",
  timeout: 3000
})

const authStore = useAuthStore()
authStore.setCsrfToken()

// Verify session with backend on startup before trusting localStorage
if (authStore.isAuthenticated) {
  authStore.fetchUser()
}

app.mount('#app')