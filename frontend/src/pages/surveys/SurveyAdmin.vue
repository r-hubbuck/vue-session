<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Survey Management</h1>
      <router-link :to="{ name: 'survey-builder' }" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i> Create Survey
      </router-link>
    </div>

    <!-- Search -->
    <div class="card mb-3">
      <div class="card-body">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control"
          placeholder="Search surveys by title..."
        />
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="filteredSurveys.length === 0" class="card">
      <div class="card-body text-center py-5 text-muted">
        <i class="bi bi-clipboard2 fs-1 d-block mb-2"></i>
        No surveys found.
      </div>
    </div>

    <div v-else class="card">
      <div class="table-responsive">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Status</th>
              <th>Responses</th>
              <th>Open Date</th>
              <th>Close Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="survey in filteredSurveys" :key="survey.id">
              <td>
                <strong>{{ survey.title }}</strong>
                <span v-if="survey.is_graded" class="badge bg-info text-dark ms-2 small">Graded</span>
              </td>
              <td>
                <span class="badge" :class="typeBadgeClass(survey.survey_type)">
                  {{ survey.survey_type_display }}
                </span>
              </td>
              <td>
                <span class="badge" :class="survey.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ survey.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ survey.response_count ?? '—' }}</td>
              <td class="small text-muted">{{ formatDate(survey.open_date) || '—' }}</td>
              <td class="small text-muted">{{ formatDate(survey.close_date) || '—' }}</td>
              <td>
                <div class="btn-group btn-group-sm">
                  <router-link
                    :to="{ name: 'survey-builder-edit', params: { id: survey.id } }"
                    class="btn btn-outline-primary"
                    title="Edit"
                  >
                    <i class="bi bi-pencil"></i>
                  </router-link>
                  <router-link
                    :to="{ name: 'survey-results', params: { id: survey.id } }"
                    class="btn btn-outline-secondary"
                    title="Results"
                  >
                    <i class="bi bi-bar-chart"></i>
                  </router-link>
                  <button
                    v-if="survey.is_active"
                    @click="deactivate(survey)"
                    class="btn btn-outline-danger"
                    title="Deactivate"
                  >
                    <i class="bi bi-archive"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()

const surveys = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const filteredSurveys = computed(() =>
  surveys.value.filter(s =>
    s.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
)

async function loadSurveys() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/api/surveys/admin/')
    surveys.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to load surveys.'
  } finally {
    loading.value = false
  }
}

async function deactivate(survey) {
  if (!confirm(`Deactivate "${survey.title}"? It will no longer be visible to users.`)) return
  try {
    await api.delete(`/api/surveys/admin/${survey.id}/`)
    survey.is_active = false
  } catch (e) {
    toast.error(e.response?.data?.error || 'Failed to deactivate survey.')
  }
}

function typeBadgeClass(type) {
  const map = {
    survey: 'bg-primary',
    questionnaire: 'bg-info text-dark',
    test: 'bg-danger',
    quiz: 'bg-warning text-dark',
    assessment: 'bg-dark',
  }
  return map[type] || 'bg-secondary'
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString()
}

onMounted(loadSurveys)
</script>
