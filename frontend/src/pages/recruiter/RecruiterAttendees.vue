<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Convention Attendees</h1>
        <p class="page-subtitle">Browse members attending the convention</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="error" class="section-card">
        <div class="alert alert-warning mb-0">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
      </div>

      <template v-else>
        <!-- Search -->
        <div class="section-card">
          <div class="row g-3 align-items-end">
            <div class="col-md-6">
              <label class="form-label">Search Attendees</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input
                  v-model.trim="searchQuery"
                  type="text"
                  class="form-control"
                  placeholder="Search by name or chapter..."
                  maxlength="100"
                  @input="debouncedSearch"
                >
              </div>
            </div>
            <div class="col-md-3">
              <span class="text-muted">{{ totalCount }} attendees found</span>
            </div>
          </div>
        </div>

        <!-- Attendee List -->
        <div class="section-card">
          <div v-if="attendees.length === 0" class="text-center py-4 text-muted">
            No attendees found.
          </div>

          <div class="table-responsive" v-else>
            <table class="table table-custom">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Chapter</th>
                  <th v-if="hasResumeAccess">Resume</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attendee in attendees" :key="attendee.id">
                  <td class="fw-medium">{{ attendee.first_name }} {{ attendee.last_name }}</td>
                  <td>{{ attendee.chapter }}</td>
                  <td v-if="hasResumeAccess">
                    <a
                      v-if="attendee.resume_url"
                      :href="attendee.resume_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="btn btn-sm btn-outline-custom"
                    >
                      <i class="bi bi-file-earmark-pdf me-1"></i>Download
                    </a>
                    <span v-else class="text-muted">No resume</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="d-flex justify-content-center mt-3">
            <nav>
              <ul class="pagination pagination-sm">
                <li class="page-item" :class="{ disabled: currentPage <= 1 }">
                  <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)">Previous</a>
                </li>
                <li
                  v-for="page in displayedPages"
                  :key="page"
                  class="page-item"
                  :class="{ active: page === currentPage }"
                >
                  <a class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
                </li>
                <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
                  <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">Next</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const loading = ref(true)
const error = ref('')
const attendees = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 50
const hasResumeAccess = ref(false)

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))
const displayedPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchAttendees()
  }, 300)
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchAttendees()
}

const fetchAttendees = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (searchQuery.value) params.search = searchQuery.value.trim()

    const res = await api.get('/api/recruiters/convention/attendees/', { params })
    attendees.value = res.data.results
    totalCount.value = res.data.count

    // Determine resume access from first result
    if (attendees.value.length > 0 && attendees.value[0].resume_url !== undefined) {
      hasResumeAccess.value = true
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load attendees.'
  }
}

onMounted(async () => {
  // Check resume access via registration
  try {
    const regRes = await api.get('/api/recruiters/convention/my-registration/')
    if (regRes.data.booth_package_detail?.includes_resume_access) {
      hasResumeAccess.value = true
    }
  } catch {
    // Ignore - will show error when fetching attendees
  }

  await fetchAttendees()
  loading.value = false
})
</script>
