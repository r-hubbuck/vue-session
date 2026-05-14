<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import SupportModal from './SupportModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const openDropdown = ref(null)
const userMenuRef = ref(null)
const userTriggerRef = ref(null)

onMounted(async () => {
  if (authStore.isRecruiter) {
    await authStore.fetchRecruiterRegistration()
  }
  document.addEventListener('click', closeAllMenus)
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('click', closeAllMenus)
  document.removeEventListener('keydown', handleEscapeKey)
  document.body.style.overflow = ''
})

const userEmail = computed(() => authStore.user?.email || 'User')

const userName = computed(() => {
  const first = authStore.user?.member?.preferred_first_name || authStore.user?.member?.first_name || ''
  const last = authStore.user?.member?.last_name || ''
  if (first || last) return `${first} ${last}`.trim()
  return userEmail.value
})

const userInitials = computed(() => {
  const first = authStore.user?.member?.preferred_first_name || authStore.user?.member?.first_name || ''
  const last = authStore.user?.member?.last_name || ''
  if (first && last) return `${first[0]}${last[0]}`.toUpperCase()
  if (first) return first[0].toUpperCase()
  return (userEmail.value[0] || '?').toUpperCase()
})

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
  document.body.style.overflow = mobileMenuOpen.value ? 'hidden' : ''
  if (!mobileMenuOpen.value) openDropdown.value = null
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
  openDropdown.value = null
  document.body.style.overflow = ''
}

const toggleUserMenu = () => {
  openDropdown.value = null
  userMenuOpen.value = !userMenuOpen.value
  if (userMenuOpen.value) {
    nextTick(() => userMenuRef.value?.querySelector('[role="menuitem"]')?.focus())
  }
}

const closeAllMenus = () => {
  userMenuOpen.value = false
  openDropdown.value = null
}

const handleEscapeKey = (event) => {
  if (event.key === 'Escape' && mobileMenuOpen.value) closeMobileMenu()
}

const toggleDropdown = (label) => {
  userMenuOpen.value = false
  openDropdown.value = openDropdown.value === label ? null : label
}

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

const supportModalOpen = ref(false)

const logout = async () => {
  userMenuOpen.value = false
  closeMobileMenu()
  try {
    await authStore.logout(router)
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// roles: null → visible to any authenticated non-recruiter user
// roles: [...] → visible only if user has at least one listed role
const navCategoryDefs = [
  {
    label: 'Convention',
    icon: 'bi-calendar-event',
    items: [
      { to: '/convention',          label: 'My Registration',   icon: 'bi-person-badge',       roles: null },
      { to: '/convention-admin',    label: 'Registration Admin', icon: 'bi-person-lines-fill', roles: ['hq_staff'] },
      { to: '/convention-check-in', label: 'Check In',           icon: 'bi-person-check',      roles: ['hq_staff'] },
      { to: '/convention-travel',   label: 'Travel Requests',    icon: 'bi-airplane',           roles: ['hq_admin', 'hq_convention_travel'] },
      { to: '/recruiter-admin',     label: 'Recruiters',         icon: 'bi-briefcase',          roles: ['hq_recruiting', 'hq_admin'] },
    ],
  },
  {
    label: 'Expense Reports',
    icon: 'bi-receipt',
    items: [
      { to: '/expense-report',       label: 'My Expense Reports',   icon: 'bi-receipt',        roles: null },
      { to: '/expense-report-admin', label: 'Expense Report Admin', icon: 'bi-clipboard-data', roles: ['hq_admin', 'hq_finance'] },
    ],
  },
  {
    label: 'Invoices',
    icon: 'bi-file-earmark-text',
    items: [
      { to: '/invoice-admin', label: 'Invoice Admin', icon: 'bi-file-earmark-text', roles: ['hq_finance', 'hq_admin'] },
    ],
  },
  {
    label: 'Administration',
    icon: 'bi-gear',
    items: [
      { to: '/user-management', label: 'User Management', icon: 'bi-people',          roles: ['hq_admin'] },
      // { to: '/surveys',         label: 'View Surveys',    icon: 'bi-clipboard',       roles: ['hq_staff'] },
      // { to: '/surveys/admin',   label: 'Survey Admin',    icon: 'bi-clipboard-check', roles: ['hq_staff'] },
    ],
  },
]

const visibleCategories = computed(() =>
  navCategoryDefs
    .map(cat => ({
      ...cat,
      visibleItems: cat.items.filter(item =>
        item.roles === null || item.roles.some(role => authStore.hasRole(role))
      ),
    }))
    .filter(cat => cat.visibleItems.length > 0)
)
</script>

<template>
  <nav class="top-nav">
    <div class="nav-container">
      <div class="brand-section">
        <!-- Brand -->
        <router-link :to="authStore.isRecruiter ? '/recruiter/dashboard' : '/'" class="brand">
          <img src="/logo_circle_blue.png" alt="Logo" width="60" height="60" class="d-inline-block align-text-top">
          <div class="brand-text">
            <h5>Tau Beta Pi</h5>
            <p>{{ authStore.isRecruiter ? 'Recruiter Portal' : 'Member Portal' }}</p>
          </div>
        </router-link>

        <!-- Recruiter Navigation (desktop flat links) -->
        <ul v-if="authStore.isRecruiter" class="main-nav">
          <li>
            <router-link to="/recruiter/convention">
              <i class="bi bi-building"></i>
              Registration
            </router-link>
          </li>
          <li v-if="authStore.canAccessResumes">
            <router-link to="/recruiter/resumes">
              <i class="bi bi-file-earmark-person"></i>
              Resumes
            </router-link>
          </li>
          <li>
            <router-link to="/recruiter/invoices">
              <i class="bi bi-receipt"></i>
              Invoices
            </router-link>
          </li>
        </ul>

        <!-- Member / HQ Navigation (desktop category dropdowns) -->
        <ul v-else class="main-nav">
          <li
            v-for="cat in visibleCategories"
            :key="cat.label"
            class="nav-dropdown-group"
            @click.stop
          >
            <button
              class="nav-dropdown-trigger"
              :class="{ 'open': openDropdown === cat.label }"
              @click="toggleDropdown(cat.label)"
            >
              <i class="bi" :class="cat.icon"></i>
              {{ cat.label }}
              <i class="bi bi-chevron-down nav-chevron" :class="{ 'rotated': openDropdown === cat.label }"></i>
            </button>

            <div v-if="openDropdown === cat.label" class="nav-dropdown-panel">
              <router-link
                v-for="item in cat.visibleItems"
                :key="item.to"
                :to="item.to"
                class="nav-dropdown-item"
                @click="openDropdown = null"
              >
                <i class="bi" :class="item.icon"></i>
                {{ item.label }}
              </router-link>
            </div>
          </li>
        </ul>

        <!-- Desktop User Menu -->
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
            class="user-dropdown"
          >
            <router-link
              :to="accountRoute"
              @click="closeAllMenus"
              role="menuitem"
              tabindex="-1"
              class="user-dropdown-item"
            >
              <i class="bi bi-person-gear"></i>
              Account Settings
            </router-link>
            <button
              @click="supportModalOpen = true; closeAllMenus()"
              role="menuitem"
              tabindex="-1"
              class="user-dropdown-item"
            >
              <i class="bi bi-headset"></i>
              Contact Support
            </button>
            <div class="user-dropdown-divider"></div>
            <button
              @click="logout"
              role="menuitem"
              tabindex="-1"
              class="user-dropdown-item user-dropdown-item--danger"
            >
              <i class="bi bi-box-arrow-right"></i>
              Logout
            </button>
          </div>
        </div>

        <!-- Mobile hamburger (tablet + mobile only) -->
        <button class="mobile-nav-toggle" @click="toggleMobileMenu" :aria-expanded="mobileMenuOpen" aria-label="Toggle navigation">
          <i class="bi bi-list"></i>
        </button>
      </div>
    </div>

    <!-- Mobile left drawer + overlay (teleported outside nav stacking context) -->
    <Teleport to="body">
      <Transition name="mld-fade">
        <div v-if="mobileMenuOpen" class="mld-overlay" @click="closeMobileMenu"></div>
      </Transition>

      <div class="mld-drawer" :class="{ open: mobileMenuOpen }" role="dialog" aria-modal="true" aria-label="Navigation menu">
        <!-- Navy user header -->
        <div class="mld-header">
          <div class="mld-user">
            <div class="mld-avatar">{{ userInitials }}</div>
            <div class="mld-user-info">
              <div class="mld-user-name">{{ userName }}</div>
              <div class="mld-user-email">{{ userEmail }}</div>
            </div>
          </div>
          <button class="mld-close" @click="closeMobileMenu" aria-label="Close menu">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Scrollable nav -->
        <div class="mld-nav">
          <!-- Recruiter nav -->
          <template v-if="authStore.isRecruiter">
            <div class="mld-section-label">Navigation</div>
            <router-link to="/recruiter/dashboard" class="mld-item" @click="closeMobileMenu">
              <i class="bi bi-house-door"></i>Dashboard
            </router-link>
            <router-link to="/recruiter/convention" class="mld-item" @click="closeMobileMenu">
              <i class="bi bi-building"></i>Registration
            </router-link>
            <router-link v-if="authStore.canAccessResumes" to="/recruiter/resumes" class="mld-item" @click="closeMobileMenu">
              <i class="bi bi-file-earmark-person"></i>Resumes
            </router-link>
            <router-link to="/recruiter/invoices" class="mld-item" @click="closeMobileMenu">
              <i class="bi bi-receipt"></i>Invoices
            </router-link>
          </template>

          <!-- Member / HQ nav -->
          <template v-else>
            <div class="mld-section-label">Main</div>
            <router-link to="/" class="mld-item" exact-active-class="mld-item-active" @click="closeMobileMenu">
              <i class="bi bi-house-door"></i>Home
            </router-link>

            <template v-for="cat in visibleCategories" :key="cat.label">
              <hr class="mld-divider">
              <div class="mld-section-label">{{ cat.label }}</div>
              <router-link
                v-for="item in cat.visibleItems"
                :key="item.to"
                :to="item.to"
                class="mld-item"
                @click="closeMobileMenu"
              >
                <i class="bi" :class="item.icon"></i>{{ item.label }}
              </router-link>
            </template>
          </template>
        </div>

        <!-- Footer: account, support, logout -->
        <div class="mld-footer">
          <router-link :to="accountRoute" class="mld-footer-item" @click="closeMobileMenu">
            <i class="bi bi-person-gear"></i>Account Settings
          </router-link>
          <button class="mld-footer-item" @click="supportModalOpen = true; closeMobileMenu()">
            <i class="bi bi-headset"></i>Contact Support
          </button>
          <hr class="mld-footer-divider">
          <button class="mld-footer-item mld-logout" @click="logout">
            <i class="bi bi-box-arrow-right"></i>Logout
          </button>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <SupportModal v-if="supportModalOpen" @close="supportModalOpen = false" />
    </Teleport>
  </nav>
</template>

<style scoped>
/* ─── Desktop user dropdown ─────────────────────────── */
.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  min-width: 180px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow: hidden;
}

.user-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  width: 100%;
  color: #374151;
  font-size: 0.875rem;
  font-family: inherit;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.user-dropdown-item:hover {
  background: #f8fafc;
}

.user-dropdown-item--danger {
  color: #ef4444;
}

.user-dropdown-item--danger:hover {
  background: #fef2f2;
}

.user-dropdown-divider {
  border-top: 1px solid #e2e8f0;
}

/* ─── Desktop dropdown group ─────────────────────────── */
.nav-dropdown-group {
  position: relative;
}

.nav-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  color: #4a5568;
  background: none;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
}

.nav-dropdown-trigger:hover,
.nav-dropdown-trigger.open {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
}

.nav-chevron {
  font-size: 0.7rem;
  margin-left: 0.1rem;
  transition: transform 0.2s;
}

.nav-chevron.rotated {
  transform: rotate(180deg);
}

.nav-dropdown-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 999;
  overflow: hidden;
  padding: 0.375rem;
}

.nav-dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.875rem;
  color: #374151;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 6px;
  transition: background 0.15s, color 0.15s;
}

.nav-dropdown-item:hover {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
}

.nav-dropdown-item.router-link-exact-active {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  font-weight: 600;
}

/* ─── Mobile / tablet left drawer ───────────────────── */

/* Scrim overlay */
.mld-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1100;
  backdrop-filter: blur(1px);
}

.mld-fade-enter-active,
.mld-fade-leave-active {
  transition: opacity 0.25s ease;
}
.mld-fade-enter-from,
.mld-fade-leave-to {
  opacity: 0;
}

/* Drawer panel */
.mld-drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 85vw;
  background: white;
  z-index: 1200;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 32px rgba(0, 0, 0, 0.15);
}

.mld-drawer.open {
  transform: translateX(0);
}

/* ─── Header ─────────────────────────────────────────── */
.mld-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 44px 16px 20px;
  background: var(--brand-blue);
  flex-shrink: 0;
}

.mld-user {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.mld-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
}

.mld-user-info {
  min-width: 0;
}

.mld-user-name {
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mld-user-email {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.7rem;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mld-close {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s;
}

.mld-close:hover {
  background: rgba(255, 255, 255, 0.22);
}

/* ─── Scrollable nav area ────────────────────────────── */
.mld-nav {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.mld-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #a0aec0;
  padding: 10px 20px 4px;
}

.mld-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  text-decoration: none;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  border-left: 3px solid transparent;
}

.mld-item i {
  font-size: 1rem;
  width: 18px;
  flex-shrink: 0;
  color: #718096;
  transition: color 0.15s;
}

.mld-item:hover {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
}

.mld-item:hover i {
  color: var(--brand-blue);
}

/* Active state — exact match only (avoids / matching everything) */
.mld-item.router-link-exact-active,
.mld-item-active {
  background: var(--brand-blue-light);
  color: var(--brand-blue);
  font-weight: 600;
  border-left-color: var(--brand-blue);
}

.mld-item.router-link-exact-active i,
.mld-item-active i {
  color: var(--brand-blue);
}

.mld-divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 6px 0;
}

/* ─── Footer ─────────────────────────────────────────── */
.mld-footer {
  border-top: 1px solid #e2e8f0;
  padding: 8px 0 max(16px, env(safe-area-inset-bottom));
  flex-shrink: 0;
}

.mld-footer-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  text-decoration: none;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}

.mld-footer-item i {
  font-size: 1rem;
  width: 18px;
  flex-shrink: 0;
  color: #718096;
  transition: color 0.15s;
}

.mld-footer-item:hover {
  background: #f7fafc;
  color: var(--brand-blue);
}

.mld-footer-item:hover i {
  color: var(--brand-blue);
}

.mld-footer-divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 6px 0;
}

.mld-logout {
  color: #ef4444;
}

.mld-logout i {
  color: #ef4444;
}

.mld-logout:hover {
  background: #fef2f2 !important;
  color: #dc2626 !important;
}

.mld-logout:hover i {
  color: #dc2626 !important;
}

/* ─── Only show drawer on mobile/tablet ──────────────── */
@media (min-width: 1025px) {
  .mld-drawer,
  .mld-overlay {
    display: none !important;
  }
}
</style>
