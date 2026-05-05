<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Resumes</h1>
        <p class="page-subtitle">Browse Tau Beta Pi member resumes</p>
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
        <!-- Search & Filters -->
        <div class="section-card">
          <div class="row g-3 align-items-end">
            <div class="col-md-3">
              <label class="form-label">Search Resumes</label>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input
                  v-model.trim="searchQuery"
                  type="text"
                  class="form-control"
                  placeholder="Search by name or school..."
                  maxlength="100"
                  @input="debouncedSearch"
                >
              </div>
            </div>
            <div class="col-md-3" v-if="schools.length">
              <label class="form-label">School</label>
              <select v-model="selectedSchool" class="form-select" @change="applyFilter">
                <option value="">All Schools</option>
                <option v-for="school in schools" :key="school" :value="school">{{ school }}</option>
              </select>
            </div>
            <div class="col-md-2" v-if="hasResumeAccess && curricula.length">
              <label class="form-label">Major</label>
              <select v-model="selectedCurriculum" class="form-select" @change="applyFilter">
                <option value="">All Majors</option>
                <option v-for="c in curricula" :key="c.id" :value="c.id">{{ c.full_name }}</option>
              </select>
            </div>
            <div class="col-auto ms-auto" v-if="hasResumeAccess">
              <button
                @click="bulkDownload"
                :disabled="bulkDownloadLoading || totalCount === 0"
                class="btn btn-outline-custom text-nowrap"
              >
                <span v-if="bulkDownloadLoading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                <i v-else class="bi bi-file-earmark-zip me-1"></i>
                {{ bulkDownloadLoading ? 'Preparing...' : 'Download All Resumes' }}
              </button>
            </div>
          </div>
          <div class="mt-2 d-flex flex-wrap align-items-center gap-3">
            <small class="text-muted">{{ totalCount }} resumes found</small>
            <small v-if="hasResumeAccess" class="text-muted">
              <i class="bi bi-info-circle me-1"></i>
              "Download All Resumes" downloads every resume matching your current filters.
            </small>
          </div>
        </div>

        <!-- Resume List -->
        <div class="section-card">
          <div v-if="resumes.length === 0" class="text-center py-4 text-muted">
            No resumes found.
          </div>

          <div class="table-responsive" v-else>
            <table class="table table-custom">
              <thead>
                <tr>
                  <th class="sortable-col" @click="setSort('last_name')">
                    Name <i :class="sortIcon('last_name')"></i>
                  </th>
                  <th class="sortable-col" @click="setSort('email')">
                    Email <i :class="sortIcon('email')"></i>
                  </th>
                  <th class="sortable-col" @click="setSort('school_name')">
                    School <i :class="sortIcon('school_name')"></i>
                  </th>
                  <th v-if="hasResumeAccess">Majors</th>
                  <th v-if="hasResumeAccess">Resume</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="resume in resumes" :key="resume.id">
                  <td class="fw-medium">{{ resume.first_name }} {{ resume.last_name }}</td>
                  <td>{{ resume.email || '—' }}</td>
                  <td>{{ resume.school_name || '—' }}</td>
                  <td v-if="hasResumeAccess">
                    <span v-if="resume.resume_curricula && resume.resume_curricula.length">
                      {{ resume.resume_curricula.map(c => c.abbreviated).join(', ') }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td v-if="hasResumeAccess">
                    <template v-if="resume.resume_url">
                      <button
                        @click="viewResume(resume)"
                        class="btn btn-sm btn-outline-secondary me-1"
                      >
                        <i class="bi bi-eye me-1"></i>View
                      </button>
                      <button
                        @click="downloadResume(resume)"
                        class="btn btn-sm btn-outline-custom"
                      >
                        <i class="bi bi-file-earmark-pdf me-1"></i>Download
                      </button>
                    </template>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const loading = ref(true)
const error = ref('')
const resumes = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 50
const hasResumeAccess = ref(false)

const sortField = ref('last_name')
const sortDir = ref('asc')
const bulkDownloadLoading = ref(false)

const selectedSchool = ref('')
const selectedCurriculum = ref('')
const schools = ref([])
const curricula = ref([])

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))
const displayedPages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const sortParam = computed(() =>
  sortDir.value === 'desc' ? `-${sortField.value}` : sortField.value
)

const sortIcon = (field) => {
  if (sortField.value !== field) return 'bi bi-sort ms-1 opacity-50'
  return sortDir.value === 'asc' ? 'bi bi-sort-up ms-1' : 'bi bi-sort-down ms-1'
}

const setSort = (field) => {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = 'asc'
  }
  currentPage.value = 1
  fetchResumes()
}

const applyFilter = () => {
  currentPage.value = 1
  fetchResumes()
}

let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchResumes()
  }, 300)
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchResumes()
}

const bulkDownload = async () => {
  bulkDownloadLoading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value.trim()
    if (selectedSchool.value) params.school = selectedSchool.value
    if (selectedCurriculum.value) params.curriculum = selectedCurriculum.value

    const res = await api.get('/api/recruiters/convention/resumes/bulk-download/', {
      params,
      responseType: 'blob',
    })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = res.headers['content-disposition']?.match(/filename="(.+)"/)?.[1] ?? 'resumes.zip'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    // Blob error responses need to be parsed manually
    if (err.response?.data instanceof Blob) {
      try {
        const text = await err.response.data.text()
        toast.error(JSON.parse(text).error || 'Failed to download resumes.')
      } catch {
        toast.error('Failed to download resumes.')
      }
    } else {
      toast.error(err.response?.data?.error || 'Failed to download resumes.')
    }
  } finally {
    bulkDownloadLoading.value = false
  }
}

const isSafeUrl = (url) => typeof url === 'string' && /^(https?:\/\/|\/)/i.test(url)

const viewResume = (resume) => {
  if (!isSafeUrl(resume.resume_url)) return
  window.open(resume.resume_url, '_blank', 'noopener,noreferrer')
}

const downloadResume = async (resume) => {
  try {
    const res = await api.get(resume.resume_url, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `${resume.last_name}_${resume.first_name}_resume.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to download resume.'
  }
}

const fetchResumes = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      ordering: sortParam.value,
    }
    if (searchQuery.value) params.search = searchQuery.value.trim()
    if (selectedSchool.value) params.school = selectedSchool.value
    if (selectedCurriculum.value) params.curriculum = selectedCurriculum.value

    const res = await api.get('/api/recruiters/convention/resumes/', { params })
    resumes.value = res.data.results
    totalCount.value = res.data.count
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load resumes.'
  }
}

const fetchFilterOptions = async () => {
  try {
    const res = await api.get('/api/recruiters/convention/resumes/filters/')
    schools.value = res.data.schools
    curricula.value = res.data.curricula
  } catch {
    // Non-critical — filters just won't populate
  }
}

onUnmounted(() => clearTimeout(searchTimeout))

onMounted(async () => {
  try {
    const regRes = await api.get('/api/recruiters/convention/my-registration/')
    if (regRes.data.booth_package_detail?.includes_resume_access) {
      hasResumeAccess.value = true
    }
  } catch {
    // Ignore - will show error when fetching resumes
  }

  await Promise.all([fetchResumes(), fetchFilterOptions()])
  loading.value = false
})
</script>

<style scoped>
.form-select {
  cursor: pointer;
}
.sortable-col {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.sortable-col:hover {
  background-color: rgba(0, 0, 0, 0.04);
}
</style>
