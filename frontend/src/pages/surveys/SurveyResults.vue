<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Survey Results</h1>
      <div class="d-flex gap-2">
        <router-link
          v-if="survey"
          :to="{ name: 'survey-builder-edit', params: { id: surveyId } }"
          class="btn btn-outline-primary btn-sm"
        >
          <i class="bi bi-pencil me-1"></i> Edit Survey
        </router-link>
        <router-link :to="{ name: 'survey-admin' }" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i> Back
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <template v-else-if="survey">
      <!-- Survey summary header -->
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <div class="fs-1 fw-bold text-primary">{{ totalResponses }}</div>
              <div class="text-muted small">Total Responses</div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center">
            <div class="card-body">
              <div class="fs-1 fw-bold text-success">{{ completedResponses }}</div>
              <div class="text-muted small">Completed</div>
            </div>
          </div>
        </div>
        <template v-if="scoreSummary">
          <div class="col-md-3">
            <div class="card text-center">
              <div class="card-body">
                <div class="fs-1 fw-bold text-info">{{ scoreSummary.avg_score }}</div>
                <div class="text-muted small">Avg Score</div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card text-center">
              <div class="card-body">
                <div class="fs-1 fw-bold text-warning">{{ scoreSummary.pass_rate }}%</div>
                <div class="text-muted small">Pass Rate</div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Per-question stats -->
      <h4 class="mb-3">Question Summary</h4>
      <div v-for="qs in questionStats" :key="qs.question_id" class="card mb-3">
        <div class="card-header">
          <strong>{{ qs.question_text }}</strong>
          <span class="badge bg-secondary ms-2 small">{{ qs.question_type.replace('_', ' ') }}</span>
        </div>
        <div class="card-body">
          <!-- Choice-based questions -->
          <template v-if="qs.stats.choices">
            <div class="text-muted small mb-2">{{ qs.stats.total_answers }} answer(s)</div>
            <div v-for="choice in qs.stats.choices" :key="choice.choice_text" class="mb-2">
              <div class="d-flex justify-content-between small mb-1">
                <span>
                  {{ choice.choice_text }}
                  <span v-if="choice.is_correct" class="text-success ms-1"><i class="bi bi-check-circle"></i></span>
                </span>
                <span>{{ choice.count }} ({{ choice.percentage }}%)</span>
              </div>
              <div class="progress" style="height:8px">
                <div
                  class="progress-bar"
                  :class="choice.is_correct ? 'bg-success' : 'bg-primary'"
                  :style="`width:${choice.percentage}%`"
                ></div>
              </div>
            </div>
          </template>

          <!-- Text responses -->
          <template v-else-if="qs.stats.responses !== undefined">
            <div class="text-muted small mb-2">{{ qs.stats.count }} response(s)</div>
            <div v-if="qs.stats.responses.length === 0" class="text-muted small">No responses yet.</div>
            <ul v-else class="list-group list-group-flush" style="max-height:200px;overflow-y:auto">
              <li v-for="(text, i) in qs.stats.responses" :key="i" class="list-group-item small py-1">
                {{ text }}
              </li>
            </ul>
          </template>

          <!-- Number / rating -->
          <template v-else-if="qs.stats.avg !== undefined">
            <div class="row text-center g-2">
              <div class="col">
                <div class="fw-bold">{{ qs.stats.min ?? '—' }}</div>
                <div class="text-muted small">Min</div>
              </div>
              <div class="col">
                <div class="fw-bold">{{ qs.stats.avg ?? '—' }}</div>
                <div class="text-muted small">Avg</div>
              </div>
              <div class="col">
                <div class="fw-bold">{{ qs.stats.max ?? '—' }}</div>
                <div class="text-muted small">Max</div>
              </div>
              <div class="col">
                <div class="fw-bold">{{ qs.stats.count }}</div>
                <div class="text-muted small">Count</div>
              </div>
            </div>
          </template>

          <!-- Date responses -->
          <template v-else-if="qs.stats.dates !== undefined">
            <div class="text-muted small mb-2">{{ qs.stats.count }} response(s)</div>
            <div v-if="qs.stats.dates.length === 0" class="text-muted small">No responses yet.</div>
            <ul v-else class="list-unstyled small mb-0" style="max-height:150px;overflow-y:auto">
              <li v-for="(d, i) in qs.stats.dates" :key="i">{{ d }}</li>
            </ul>
          </template>
        </div>
      </div>

      <!-- Individual responses table -->
      <h4 class="mt-4 mb-3">Individual Responses</h4>
      <div class="card">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>#</th>
                <th>Respondent</th>
                <th>Started</th>
                <th>Submitted</th>
                <th>Status</th>
                <th v-if="survey.is_graded">Score</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <template v-for="(resp, i) in individualResponses" :key="resp.id">
                <tr>
                  <td class="text-muted small">{{ i + 1 }}</td>
                  <td>{{ resp.user_email }}</td>
                  <td class="small text-muted">{{ formatDateTime(resp.started_at) }}</td>
                  <td class="small text-muted">{{ formatDateTime(resp.submitted_at) || '—' }}</td>
                  <td>
                    <span class="badge" :class="resp.is_complete ? 'bg-success' : 'bg-warning text-dark'">
                      {{ resp.is_complete ? 'Completed' : 'In Progress' }}
                    </span>
                  </td>
                  <td v-if="survey.is_graded">
                    {{ resp.score != null ? `${resp.score} / ${resp.total_possible_points}` : '—' }}
                  </td>
                  <td>
                    <button @click="toggleExpand(resp.id)" class="btn btn-sm btn-outline-secondary">
                      <i class="bi" :class="expanded.has(resp.id) ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                    </button>
                  </td>
                </tr>
                <!-- Expanded answer detail -->
                <tr v-if="expanded.has(resp.id)">
                  <td :colspan="survey.is_graded ? 7 : 6" class="bg-light">
                    <div class="ps-3">
                      <div v-for="ans in resp.answers" :key="ans.id" class="mb-1 small">
                        <strong>Q{{ questionText(ans.question) }}</strong>:
                        <span v-if="ans.text_answer">{{ ans.text_answer }}</span>
                        <span v-else-if="ans.number_answer != null">{{ ans.number_answer }}</span>
                        <span v-else-if="ans.date_answer">{{ ans.date_answer }}</span>
                        <span v-else-if="ans.selected_choices?.length">
                          {{ choiceTexts(ans.question, ans.selected_choices) }}
                        </span>
                        <span v-else class="text-muted">—</span>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'

const route = useRoute()
const surveyId = route.params.id

const survey = ref(null)
const questionStats = ref([])
const individualResponses = ref([])
const scoreSummary = ref(null)
const loading = ref(false)
const expanded = ref(new Set())

const totalResponses = computed(() => individualResponses.value.length)
const completedResponses = computed(() => individualResponses.value.filter(r => r.is_complete).length)

// Build a lookup: questionId → question_text (from questionStats)
const questionTextMap = computed(() => {
  const map = {}
  for (const qs of questionStats.value) {
    map[qs.question_id] = qs.question_text
  }
  return map
})

// Build a lookup: questionId → choices array (from questionStats)
const questionChoicesMap = computed(() => {
  const map = {}
  for (const qs of questionStats.value) {
    if (qs.stats.choices) {
      map[qs.question_id] = qs.stats.choices
    }
  }
  return map
})

function questionText(questionId) {
  const text = questionTextMap.value[questionId]
  return text ? (text.length > 50 ? text.slice(0, 50) + '…' : text) : questionId
}

function choiceTexts(questionId, selectedIds) {
  const choices = questionChoicesMap.value[questionId]
  if (!choices) return selectedIds.join(', ')
  return selectedIds
    .map(id => choices.find(c => c.choice_text)?.choice_text || id)
    .join(', ')
}

function toggleExpand(id) {
  const s = new Set(expanded.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  expanded.value = s
}

async function loadResults() {
  loading.value = true
  try {
    const res = await api.get(`/api/surveys/admin/${surveyId}/results/`)
    survey.value = res.data.survey
    questionStats.value = res.data.question_stats
    individualResponses.value = res.data.individual_responses
    scoreSummary.value = res.data.score_summary
  } catch (e) {
    alert(e.response?.data?.error || 'Failed to load results.')
  } finally {
    loading.value = false
  }
}

function formatDateTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString()
}

onMounted(loadResults)
</script>
