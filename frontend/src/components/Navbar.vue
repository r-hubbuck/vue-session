<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)

// Get user initials for avatar
const userInitials = computed(() => {
  if (authStore.user?.email) {
    const email = authStore.user.email
    return email.substring(0, 2).toUpperCase()
  }
  return 'U'
})

// Get user email
const userEmail = computed(() => {
  return authStore.user?.email || 'User'
})

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const logout = async () => {
  try {
    await authStore.logout(router)
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>

<template>
  <nav class="top-nav">
    <div class="nav-container">
      <!-- Brand Section -->
      <div class="brand-section">
        <router-link :to="authStore.isRecruiter ? '/recruiter/dashboard' : '/'" class="brand">
          <img src="/logo_circle_blue.png" alt="Logo" width="60" height="60" class="d-inline-block align-text-top">
          <div class="brand-text">
            <h5>Tau Beta Pi</h5>
            <p>{{ authStore.isRecruiter ? 'Recruiter Portal' : 'Member Portal' }}</p>
          </div>
        </router-link>

        <!-- Mobile Menu Toggle -->
        <button class="mobile-nav-toggle" @click="toggleMobileMenu" aria-label="Toggle navigation">
          <i class="bi" :class="mobileMenuOpen ? 'bi-x-lg' : 'bi-list'"></i>
        </button>

        <!-- Recruiter Navigation -->
        <ul v-if="authStore.isRecruiter" class="main-nav" :class="{ 'show': mobileMenuOpen }">
          <li>
            <router-link to="/recruiter/convention" @click="closeMobileMenu">
              <i class="bi bi-building"></i>
              Registration
            </router-link>
          </li>
          <li>
            <router-link to="/recruiter/attendees" @click="closeMobileMenu">
              <i class="bi bi-people"></i>
              Attendees
            </router-link>
          </li>
          <li>
            <router-link to="/recruiter/invoices" @click="closeMobileMenu">
              <i class="bi bi-receipt"></i>
              Invoices
            </router-link>
          </li>
        </ul>

        <!-- Member Navigation -->
        <ul v-else class="main-nav" :class="{ 'show': mobileMenuOpen }">
          <li>
            <router-link to="/account" @click="closeMobileMenu">
              <i class="bi bi-person"></i>
              Account
            </router-link>
          </li>
          <li>
            <router-link to="/convention" @click="closeMobileMenu">
              <i class="bi bi-calendar-event"></i>
              Convention
            </router-link>
          </li>
          <li>
            <router-link to="/expense-report" @click="closeMobileMenu">
              <i class="bi bi-receipt"></i>
              Expense Reports
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_admin')">
            <router-link to="/recruiter-admin" @click="closeMobileMenu">
              <i class="bi bi-briefcase"></i>
              Recruiter Admin
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_finance') || authStore.hasRole('hq_admin')">
            <router-link to="/invoice-admin" @click="closeMobileMenu">
              <i class="bi bi-file-earmark-text"></i>
              Invoice Admin
            </router-link>
          </li>
        </ul>
      </div>

      <!-- User Menu -->
      <div class="user-menu">
        <div class="user-info" @click="logout" role="button" tabindex="0" aria-label="Logout">
          <div class="user-details">
            <span>{{ userEmail }}</span>
          </div>
          <i class="bi bi-box-arrow-right" style="color: #718096; font-size: 1rem;"></i>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* Component-specific styles if needed */
/* Most styles are in the global style.css */
</style>
