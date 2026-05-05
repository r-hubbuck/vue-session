<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const authStore = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const userMenuRef = ref(null)
const userTriggerRef = ref(null)

onMounted(async () => {
  if (authStore.isRecruiter) {
    await authStore.fetchRecruiterRegistration()
  }
  document.addEventListener('click', closeUserMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
})

const userEmail = computed(() => authStore.user?.email || 'User')

const toggleMobileMenu = () => { mobileMenuOpen.value = !mobileMenuOpen.value }
const closeMobileMenu = () => { mobileMenuOpen.value = false }

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
  if (userMenuOpen.value) {
    nextTick(() => userMenuRef.value?.querySelector('[role="menuitem"]')?.focus())
  }
}
const closeUserMenu = () => { userMenuOpen.value = false }

const handleTriggerKeydown = (event) => {
  if (event.key === 'Escape') {
    userMenuOpen.value = false
  } else if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    toggleUserMenu()
  }
}

const handleMenuKeydown = (event) => {
  if (event.key === 'Escape') {
    userMenuOpen.value = false
    userTriggerRef.value?.focus()
  }
}

const accountRoute = computed(() =>
  authStore.isRecruiter ? '/recruiter/account' : '/account'
)

const logout = async () => {
  userMenuOpen.value = false
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
          <li v-if="authStore.canAccessResumes">
            <router-link to="/recruiter/resumes" @click="closeMobileMenu">
              <i class="bi bi-file-earmark-person"></i>
              Resumes
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
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_admin') || authStore.hasRole('hq_finance')">
            <router-link to="/convention-travel" @click="closeMobileMenu">
              <i class="bi bi-calendar-event"></i>
              Convention Admin
            </router-link>
          </li>
          <li v-else>
            <router-link to="/convention" @click="closeMobileMenu">
              <i class="bi bi-calendar-event"></i>
              Convention
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_admin') || authStore.hasRole('hq_finance')">
            <router-link to="/expense-report-admin" @click="closeMobileMenu">
              <i class="bi bi-receipt"></i>
              Expense Reports
            </router-link>
          </li>
          <li v-else>
            <router-link to="/expense-report" @click="closeMobileMenu">
              <i class="bi bi-receipt"></i>
              Expense Reports
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_admin')">
            <router-link to="/recruiter-admin" @click="closeMobileMenu">
              <i class="bi bi-briefcase"></i>
              Recruiters
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_staff') || authStore.hasRole('hq_finance') || authStore.hasRole('hq_admin')">
            <router-link to="/invoice-admin" @click="closeMobileMenu">
              <i class="bi bi-file-earmark-text"></i>
              Invoices
            </router-link>
          </li>
          <li v-if="authStore.hasRole('hq_admin')">
            <router-link to="/user-management" @click="closeMobileMenu">
              <i class="bi bi-people"></i>
              Users
            </router-link>
          </li>
        </ul>
      </div>

      <!-- User Menu -->
      <div class="user-menu" style="position: relative;" @click.stop>
        <div
          ref="userTriggerRef"
          class="user-info"
          @click="toggleUserMenu"
          @keydown="handleTriggerKeydown"
          role="button"
          tabindex="0"
          :aria-expanded="userMenuOpen"
          aria-haspopup="menu"
        >
          <div class="user-details">
            <span>{{ userEmail }}</span>
          </div>
          <i class="bi bi-chevron-down" style="color: #718096; font-size: 0.75rem; transition: transform 0.2s;" :style="userMenuOpen ? 'transform: rotate(180deg)' : ''"></i>
        </div>
        <div
          v-if="userMenuOpen"
          ref="userMenuRef"
          role="menu"
          @keydown="handleMenuKeydown"
          style="position: absolute; right: 0; top: calc(100% + 8px); min-width: 180px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 1000; overflow: hidden;"
        >
          <router-link
            :to="accountRoute"
            @click="closeUserMenu"
            role="menuitem"
            tabindex="-1"
            style="display: flex; align-items: center; gap: 8px; padding: 10px 16px; color: #374151; text-decoration: none; font-size: 0.875rem;"
            @mouseenter="e => e.currentTarget.style.background='#f8fafc'"
            @mouseleave="e => e.currentTarget.style.background=''"
          >
            <i class="bi bi-person-gear"></i>
            Account Settings
          </router-link>
          <div style="border-top: 1px solid #e2e8f0;"></div>
          <button
            @click="logout"
            role="menuitem"
            tabindex="-1"
            style="display: flex; align-items: center; gap: 8px; padding: 10px 16px; color: #ef4444; font-size: 0.875rem; width: 100%; background: none; border: none; cursor: pointer; text-align: left;"
            @mouseenter="e => e.currentTarget.style.background='#fef2f2'"
            @mouseleave="e => e.currentTarget.style.background=''"
          >
            <i class="bi bi-box-arrow-right"></i>
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* Component-specific styles if needed */
/* Most styles are in the global style.css */
</style>
