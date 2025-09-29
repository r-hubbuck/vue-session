import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'

import router from './router'
import App from './App.vue'
import { useAuthStore } from './store/auth'

// Load Bootstrap CSS and JS from CDN
const bootstrapCSS = document.createElement('link')
bootstrapCSS.rel = 'stylesheet'
bootstrapCSS.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
document.head.appendChild(bootstrapCSS)

const bootstrapJS = document.createElement('script')
bootstrapJS.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
document.head.appendChild(bootstrapJS)

// Load Bootstrap Icons from CDN
const bootstrapIcons = document.createElement('link')
bootstrapIcons.rel = 'stylesheet'
bootstrapIcons.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
document.head.appendChild(bootstrapIcons)

const app = createApp(App)

app.use(createPinia())
app.use(router)

const authStore = useAuthStore()
authStore.setCsrfToken()

app.mount('#app')