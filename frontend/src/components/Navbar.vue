<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
    <div class="container-fluid">
      <!-- Logo/Brand -->
      <router-link class="navbar-brand" to="/" @click="navigateHome">
        <img src="/logo_circle_blue.png" alt="Logo" width="60" height="60" class="d-inline-block align-text-top">
      </router-link>

      <!-- Navbar toggler for mobile -->
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav" 
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar items -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- Left side items -->
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/account" @click="navigateToAccount">
              Account Settings
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/convention" @click="navigateToConvention">
              Convention
            </router-link>
          </li>
           <li class="nav-item">
            <router-link class="nav-link" to="/expense-reports" @click="navigateToExpenseReports">
              Expense Reports
            </router-link>
          </li>
        </ul>

        <!-- Right side items -->
        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <a 
              class="nav-link dropdown-toggle" 
              href="#" 
              id="settingsDropdown" 
              role="button" 
              data-bs-toggle="dropdown" 
              aria-expanded="false"
              @click="toggleDropdown"
            >
              <!-- Gear icon -->
              <i class="bi bi-gear-fill gear-icon"></i>
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="settingsDropdown" :class="{ show: showDropdown }" style="right: 0; left: auto;">
              <li>
                <router-link class="dropdown-item" to="/account" @click="closeDropdown">
                  <i class="bi bi-person-circle me-2"></i>Account Settings
                </router-link>
              </li>
              <li>
                <a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '../store/auth.js'

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore()
    return {
      authStore
    }
  },
  data() {
    return {
      showDropdown: false
    }
  },
  methods: {
    async handleLogout() {
      this.closeDropdown()
      try {
        await this.authStore.logout(this.$router)
      } catch (error) {
        console.error('Logout error:', error)
      }
    },
    navigateHome() {
      if (this.$route.name !== 'home') {
        this.$router.push('/');
      }
    },
    navigateToAccount() {
      if (this.$route.name !== 'account') {
        this.$router.push('/account');
      }
    },
    navigateToConvention() {
      if (this.$route.name !== 'convention') {
        this.$router.push('/convention');
      }
    },
    navigateToExpenseReports() {
      if (this.$route.name !== 'expense-reports') {
        this.$router.push('/expense-reports');
      }
    },
    toggleDropdown(event) {
      event.preventDefault()
      this.showDropdown = !this.showDropdown
    },
    closeDropdown() {
      this.showDropdown = false
    }
  },
  mounted() {
    // Close dropdown when clicking outside
    document.addEventListener('click', (event) => {
      const dropdown = this.$el.querySelector('.dropdown')
      if (dropdown && !dropdown.contains(event.target)) {
        this.showDropdown = false
      }
    })
  }
}
</script>

<style scoped>
.navbar {
  border-bottom: 1px solid #dee2e6;
}

.navbar-brand img {
  transition: transform 0.2s ease;
}

.navbar-brand:hover img {
  transform: scale(1.1);
}

.nav-link {
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #0d6efd !important;
}

.dropdown-toggle::after {
  display: none;
}

.gear-icon {
  font-size: 1.2em;
  transition: transform 0.2s ease;
}

.dropdown-menu {
  border: 1px solid #dee2e6;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  transition: opacity 0.15s linear, transform 0.15s ease-in-out;
  min-width: 200px;
}

.dropdown-menu.show {
  display: block;
}

.dropdown-menu-end {
  right: 0 !important;
  left: auto !important;
  transform: translate3d(0px, 10px, 0px) !important;
}

.nav-link:hover .gear-icon {
  transform: rotate(90deg);
}

.dropdown-menu {
  border: 1px solid #dee2e6;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.dropdown-item {
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}
</style>