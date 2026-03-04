<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Surveys &amp; Questionnaires</h1>
      <router-link v-if="isStaff" :to="{ name: 'survey-admin' }" class="btn btn-primary">
        <i class="bi bi-gear me-1"></i> Manage Surveys
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="surveys.length === 0" class="card">
      <div class="card-body text-center py-5 text-muted">
        <i class="bi bi-clipboard2 fs-1 d-block mb-2"></i>
        No surveys are currently available.
      </div>
    </div>

    <div v-else class="row g-3">
      <div v-for="survey in surveys" :key="survey.id" class="col-md-6 col-lg-4">
        <div class="card h-100" :class="{ 'border-success': survey.response_status === 'completed' }">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge" :class="typeBadgeClass(survey.survey_type)">
                {{ survey.survey_type_display }}
              </span>
              <span class="badge" :class="statusBadgeClass(survey.response_status)">
                {{ statusLabel(survey.response_status) }}
              </span>
            </div>

            <h5 class="card-title">{{ survey.title }}</h5>
            <p v-if="survey.description" class="card-text text-muted small flex-grow-1">
              {{ truncate(survey.description, 120) }}
            </p>

            <div class="mt-2 small text-muted">
              <span v-if="!survey.is_open_now" class="text-danger">
                <i class="bi bi-lock me-1"></i>Closed
              </span>
              <span v-else>
                <i class="bi bi-unlock me-1"></i>Open
                <span v-if="survey.close_date"> · Closes {{ formatDate(survey.close_date) }}</span>
              </span>
              <span v-if="survey.is_graded" class="ms-2">
                <i class="bi bi-patch-check me-1"></i>Graded
              </span>
            </div>
          </div>

          <div class="card-footer bg-transparent">
            <button
              v-if="survey.response_status === 'completed'"
              class="btn btn-outline-success btn-sm w-100"
              disabled
            >
              <i class="bi bi-check-circle me-1"></i> Completed
            </button>
            <button
              v-else-if="!survey.is_open_now"
              class="btn btn-outline-secondary btn-sm w-100"
              disabled
            >
              Survey Closed
            </button>
            <router-link
              v-else
              :to="{ name: 'survey-take', params: { id: survey.id } }"
              class="btn btn-sm w-100"
              :class="survey.response_status === 'in_progress' ? 'btn-warning' : 'btn-primary'"
            >
              <i class="bi bi-pencil me-1"></i>
              {{ survey.response_status === 'in_progress' ? 'Continue' : 'Take Survey' }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../store/auth'
import api from '../../api'

const authStore = useAuthStore()
const surveys = ref([])
const loading = ref(false)
const error = ref(null)

const STAFF_ROLES = ['hq_staff', 'hq_it', 'hq_admin', 'hq_finance', 'executive_council']
const isStaff = computed(() => STAFF_ROLES.some(r => authStore.hasRole(r)))

async function loadSurveys() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/api/surveys/')
    surveys.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to load surveys.'
  } finally {
    loading.value = false
  }
}

function statusLabel(status) {
  const map = { not_started: 'Not Started', in_progress: 'In Progress', completed: 'Completed' }
  return map[status] || status
}

function statusBadgeClass(status) {
  if (status === 'completed') return 'bg-success'
  if (status === 'in_progress') return 'bg-warning text-dark'
  return 'bg-secondary'
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

function truncate(text, len) {
  if (!text || text.length <= len) return text
  return text.slice(0, len) + '…'
}

onMounted(loadSurveys)
</script>
