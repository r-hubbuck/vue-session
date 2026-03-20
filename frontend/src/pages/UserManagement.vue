<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">User Management</h1>
        <p class="page-subtitle">Search and manage member accounts</p>
      </div>
    </div>

    <div class="content-container">
      <div class="section-card">
        <div class="mb-4">
          <label class="form-label fw-semibold">Search Users</label>
          <input
            v-model="searchQuery"
            type="text"
            class="form-control"
            placeholder="Name, email, or member ID..."
            @input="onSearchInput"
            maxlength="200"
          >
          <small class="text-muted">Results limited to 100. Refine your search if needed.</small>
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>

        <div v-else-if="users.length > 0" class="table-responsive">
          <table class="table table-custom table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Member ID</th>
                <th>Chapter</th>
                <th>Roles</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" style="vertical-align: middle;">
                <td>{{ user.first_name }} {{ user.last_name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.member_id || '—' }}</td>
                <td>{{ user.chapter || '—' }}</td>
                <td>
                  <span
                    v-for="role in user.roles"
                    :key="role"
                    class="badge bg-secondary me-1"
                    style="font-size: 0.75rem;"
                  >{{ role }}</span>
                </td>
                <td>
                  <router-link
                    :to="`/admin/users/${user.person_id}`"
                    class="btn btn-sm btn-outline-primary"
                  >
                    <i class="bi bi-person-gear me-1"></i>Manage
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="hasSearched" class="text-center py-4 text-muted">
          <i class="bi bi-search me-2"></i>No users found matching "{{ searchQuery }}".
        </div>

        <div v-else class="text-center py-5 text-muted">
          <i class="bi bi-people" style="font-size: 2rem; display: block; margin-bottom: 0.5rem;"></i>
          Enter a name, email, or member ID to search.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
import { useAuthStore } from '../store/auth'

export default {
  name: 'UserManagement',

  data() {
    return {
      searchQuery: '',
      users: [],
      loading: false,
      error: null,
      hasSearched: false,
      searchDebounce: null,
    }
  },

  async created() {
    const authStore = useAuthStore()
    if (!authStore.hasRole('hq_admin')) {
      this.$router.push({ name: 'home' })
    }
  },

  methods: {
    onSearchInput() {
      clearTimeout(this.searchDebounce)
      if (!this.searchQuery.trim()) {
        this.users = []
        this.hasSearched = false
        return
      }
      this.searchDebounce = setTimeout(() => this.fetchUsers(), 400)
    },

    async fetchUsers() {
      this.loading = true
      this.error = null
      this.hasSearched = true
      try {
        const response = await api.get('/api/accounts/admin/users/', {
          params: { search: this.searchQuery.trim() }
        })
        this.users = response.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load users.'
        this.users = []
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
