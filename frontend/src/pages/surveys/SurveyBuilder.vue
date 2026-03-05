<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>{{ isEdit ? 'Edit Survey' : 'Create Survey' }}</h1>
      <router-link :to="{ name: 'survey-admin' }" class="btn btn-outline-secondary btn-sm">
        <i class="bi bi-arrow-left me-1"></i> Back
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <template v-else>
      <div v-if="saveError" class="alert alert-danger mb-3">
        <strong>Save failed:</strong> {{ saveError }}
      </div>

      <!-- Survey Metadata -->
      <div class="card mb-4">
        <div class="card-header fw-semibold">Survey Details</div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-8">
              <label class="form-label">Title <span class="text-danger">*</span></label>
              <input v-model="form.title" type="text" class="form-control" placeholder="Survey title" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Type</label>
              <select v-model="form.survey_type" class="form-select">
                <option value="survey">Survey</option>
                <option value="questionnaire">Questionnaire</option>
                <option value="test">Test</option>
                <option value="quiz">Quiz</option>
                <option value="assessment">Assessment</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Description</label>
              <textarea v-model="form.description" class="form-control" rows="2" placeholder="Optional description"></textarea>
            </div>
            <div class="col-md-4">
              <label class="form-label">Open Date</label>
              <input v-model="form.open_date" type="datetime-local" class="form-control" />
              <div class="form-text">Leave blank for no start restriction.</div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Close Date</label>
              <input v-model="form.close_date" type="datetime-local" class="form-control" />
              <div class="form-text">Leave blank for no end date.</div>
            </div>
            <div class="col-md-4 d-flex align-items-end">
              <div v-if="form.is_graded">
                <label class="form-label">Passing Score (%)</label>
                <input v-model.number="form.passing_score" type="number" min="0" max="100" class="form-control" placeholder="e.g. 70" />
              </div>
            </div>
            <div class="col-12">
              <div class="row g-3">
                <div class="col-auto">
                  <div class="form-check form-switch">
                    <input v-model="form.is_active" class="form-check-input" type="checkbox" id="chkActive" />
                    <label class="form-check-label" for="chkActive">Active</label>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="form-check form-switch">
                    <input v-model="form.is_graded" class="form-check-input" type="checkbox" id="chkGraded" />
                    <label class="form-check-label" for="chkGraded">Graded (track correct answers &amp; score)</label>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="form-check form-switch">
                    <input v-model="form.is_anonymous" class="form-check-input" type="checkbox" id="chkAnon" />
                    <label class="form-check-label" for="chkAnon">Anonymous responses</label>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="form-check form-switch">
                    <input v-model="form.allow_multiple_submissions" class="form-check-input" type="checkbox" id="chkMulti" />
                    <label class="form-check-label" for="chkMulti">Allow multiple submissions</label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Audience -->
      <div class="card mb-4">
        <div class="card-header fw-semibold d-flex justify-content-between align-items-center">
          Audience
          <div class="btn-group btn-group-sm">
            <button @click="addAudience('open')" class="btn btn-outline-secondary">+ Open to All</button>
            <button @click="addAudience('role')" class="btn btn-outline-secondary">+ By Role</button>
            <button @click="addAudience('user')" class="btn btn-outline-secondary">+ Specific User</button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="form.audience.length === 0" class="text-muted small">
            No audience rules yet. Add at least one rule or the survey will be invisible to all users.
          </div>
          <div v-for="(aud, i) in form.audience" :key="i" class="d-flex align-items-center gap-2 mb-2">
            <span class="badge bg-secondary">{{ aud.audience_type }}</span>
            <input
              v-if="aud.audience_type === 'role'"
              v-model="aud.role"
              type="text"
              class="form-control form-control-sm"
              placeholder="Role name (e.g. member, alumni)"
              list="roleList"
            />
            <datalist id="roleList">
              <option v-for="r in ALL_ROLES" :key="r" :value="r" />
            </datalist>
            <input
              v-if="aud.audience_type === 'user'"
              v-model.number="aud.user"
              type="number"
              class="form-control form-control-sm"
              placeholder="User ID"
            />
            <span v-if="aud.audience_type === 'open'" class="text-muted small">All authenticated users</span>
            <button @click="form.audience.splice(i, 1)" class="btn btn-outline-danger btn-sm ms-auto">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Questions -->
      <div class="card mb-4">
        <div class="card-header fw-semibold d-flex justify-content-between align-items-center">
          Questions ({{ form.questions.length }})
          <button @click="addQuestion" class="btn btn-primary btn-sm">
            <i class="bi bi-plus-lg me-1"></i> Add Question
          </button>
        </div>
        <div class="card-body">
          <div v-if="form.questions.length === 0" class="text-muted small text-center py-3">
            No questions yet. Click "Add Question" to get started.
          </div>

          <div
            v-for="(q, qi) in form.questions"
            :key="qi"
            class="card mb-3 border-secondary"
          >
            <div class="card-header bg-light d-flex align-items-center gap-2 py-2">
              <span class="text-muted small fw-semibold">Q{{ qi + 1 }}</span>
              <div class="ms-auto d-flex gap-1">
                <button @click="moveQuestion(qi, -1)" :disabled="qi === 0" class="btn btn-outline-secondary btn-sm">
                  <i class="bi bi-arrow-up"></i>
                </button>
                <button @click="moveQuestion(qi, 1)" :disabled="qi === form.questions.length - 1" class="btn btn-outline-secondary btn-sm">
                  <i class="bi bi-arrow-down"></i>
                </button>
                <button @click="form.questions.splice(qi, 1)" class="btn btn-outline-danger btn-sm">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label small">Question Type</label>
                  <select v-model="q.question_type" class="form-select form-select-sm" @change="onTypeChange(q)">
                    <option value="multiple_choice">Multiple Choice</option>
                    <option value="checkbox">Checkbox (multi-select)</option>
                    <option value="true_false">True / False</option>
                    <option value="yes_no">Yes / No</option>
                    <option value="short_answer">Short Answer</option>
                    <option value="essay">Essay</option>
                    <option value="rating">Rating Scale</option>
                    <option value="number">Number</option>
                    <option value="date">Date</option>
                    <option value="dropdown">Dropdown</option>
                  </select>
                </div>
                <div class="col-md-8">
                  <label class="form-label small">Question Text <span class="text-danger">*</span></label>
                  <textarea v-model="q.question_text" class="form-control form-control-sm" rows="2" placeholder="Enter your question..."></textarea>
                </div>
                <div class="col-md-6">
                  <label class="form-label small">Help Text (optional)</label>
                  <input v-model="q.help_text" type="text" class="form-control form-control-sm" placeholder="Additional guidance for respondents" />
                </div>
                <div class="col-md-3 d-flex align-items-end">
                  <div class="form-check form-switch">
                    <input v-model="q.is_required" class="form-check-input" type="checkbox" :id="`req-${qi}`" />
                    <label class="form-check-label small" :for="`req-${qi}`">Required</label>
                  </div>
                </div>
                <!-- Grading fields -->
                <div v-if="form.is_graded" class="col-md-3 d-flex align-items-end gap-3">
                  <div class="form-check form-switch">
                    <input v-model="q.has_correct_answer" class="form-check-input" type="checkbox" :id="`correct-${qi}`" />
                    <label class="form-check-label small" :for="`correct-${qi}`">Has correct answer</label>
                  </div>
                  <div v-if="q.has_correct_answer">
                    <label class="form-label small mb-0">Points</label>
                    <input v-model.number="q.points" type="number" min="1" class="form-control form-control-sm" style="width:70px" />
                  </div>
                </div>

                <!-- Rating configuration -->
                <template v-if="q.question_type === 'rating'">
                  <div class="col-md-2">
                    <label class="form-label small">Min</label>
                    <input v-model.number="q.rating_min" type="number" class="form-control form-control-sm" />
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small">Max</label>
                    <input v-model.number="q.rating_max" type="number" class="form-control form-control-sm" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Min Label</label>
                    <input v-model="q.rating_min_label" type="text" class="form-control form-control-sm" placeholder="e.g. Strongly Disagree" />
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Max Label</label>
                    <input v-model="q.rating_max_label" type="text" class="form-control form-control-sm" placeholder="e.g. Strongly Agree" />
                  </div>
                </template>

                <!-- Choices for MC, checkbox, dropdown, true_false, yes_no -->
                <div v-if="hasChoices(q.question_type)" class="col-12">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <label class="form-label small mb-0">Answer Choices</label>
                    <button
                      v-if="!isAutoChoiceType(q.question_type)"
                      @click="addChoice(qi)"
                      class="btn btn-outline-secondary btn-sm"
                    >
                      <i class="bi bi-plus me-1"></i> Add Choice
                    </button>
                  </div>
                  <div v-if="isAutoChoiceType(q.question_type)" class="text-muted small">
                    Choices are auto-populated ({{ autoChoiceLabel(q.question_type) }}).
                  </div>
                  <div v-else>
                    <div
                      v-for="(choice, ci) in q.choices"
                      :key="ci"
                      class="d-flex align-items-center gap-2 mb-2"
                    >
                      <span class="text-muted small" style="min-width:1.5rem">{{ ci + 1 }}.</span>
                      <input
                        v-model="choice.choice_text"
                        type="text"
                        class="form-control form-control-sm"
                        placeholder="Choice text"
                      />
                      <div v-if="form.is_graded && q.has_correct_answer" class="form-check ms-1 mb-0" style="min-width:90px">
                        <input
                          v-model="choice.is_correct"
                          class="form-check-input"
                          type="checkbox"
                          :id="`correct-${qi}-${ci}`"
                        />
                        <label class="form-check-label small" :for="`correct-${qi}-${ci}`">Correct</label>
                      </div>
                      <button @click="q.choices.splice(ci, 1)" class="btn btn-outline-danger btn-sm">
                        <i class="bi bi-x"></i>
                      </button>
                    </div>
                    <div v-if="q.choices.length === 0" class="text-muted small">No choices added yet.</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Save button -->
      <div class="d-flex justify-content-end gap-2 mb-5">
        <router-link :to="{ name: 'survey-admin' }" class="btn btn-outline-secondary">Cancel</router-link>
        <button @click="saveSurvey" :disabled="saving" class="btn btn-primary">
          <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
          {{ isEdit ? 'Save Changes' : 'Create Survey' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()

const route = useRoute()
const router = useRouter()

const surveyId = computed(() => route.params.id)
const isEdit = computed(() => !!surveyId.value)

const ALL_ROLES = [
  'member', 'alumni', 'collegiate_officer', 'alumni_officer', 'district_director',
  'engineering_futures_facilitator', 'executive_council', 'trust_advisory_committee',
  'chapter_development_committee', 'fellowship_board', 'editorial_board',
  'director_alumni_affairs', 'director_district_program', 'director_engineering_futures',
  'director_fellowships', 'director_rituals', 'nest_program_lead',
  'hq_staff', 'hq_it', 'hq_finance', 'hq_chapter_services', 'hq_admin', 'recruiter',
]

const CHOICE_TYPES = new Set(['multiple_choice', 'checkbox', 'dropdown', 'true_false', 'yes_no'])
const AUTO_CHOICE_TYPES = new Set(['true_false', 'yes_no'])

const form = ref({
  title: '',
  description: '',
  survey_type: 'survey',
  is_active: true,
  is_anonymous: false,
  allow_multiple_submissions: false,
  is_graded: false,
  passing_score: null,
  open_date: null,
  close_date: null,
  questions: [],
  audience: [],
})

const loading = ref(false)
const saving = ref(false)
const saveError = ref(null)

function hasChoices(type) { return CHOICE_TYPES.has(type) }
function isAutoChoiceType(type) { return AUTO_CHOICE_TYPES.has(type) }
function autoChoiceLabel(type) {
  return type === 'true_false' ? 'True, False' : 'Yes, No'
}

function newQuestion() {
  return {
    order: form.value.questions.length,
    question_text: '',
    question_type: 'multiple_choice',
    is_required: true,
    help_text: '',
    rating_min: 1,
    rating_max: 5,
    rating_min_label: '',
    rating_max_label: '',
    has_correct_answer: false,
    points: 1,
    choices: [],
  }
}

function addQuestion() {
  form.value.questions.push(newQuestion())
}

function moveQuestion(index, direction) {
  const arr = form.value.questions
  const target = index + direction
  if (target < 0 || target >= arr.length) return
  ;[arr[index], arr[target]] = [arr[target], arr[index]]
  arr.forEach((q, i) => { q.order = i })
}

function onTypeChange(q) {
  // Clear choices when switching away from a choice type
  if (!CHOICE_TYPES.has(q.question_type)) {
    q.choices = []
  }
}

function addChoice(qi) {
  form.value.questions[qi].choices.push({ order: form.value.questions[qi].choices.length, choice_text: '', is_correct: false })
}

function addAudience(type) {
  form.value.audience.push({ audience_type: type, role: null, user: null })
}

function toDatetimeLocal(dt) {
  if (!dt) return null
  return new Date(dt).toISOString().slice(0, 16)
}

async function loadSurvey() {
  if (!isEdit.value) return
  loading.value = true
  try {
    const res = await api.get(`/api/surveys/admin/${surveyId.value}/`)
    const data = res.data
    form.value = {
      title: data.title || '',
      description: data.description || '',
      survey_type: data.survey_type || 'survey',
      is_active: data.is_active ?? true,
      is_anonymous: data.is_anonymous ?? false,
      allow_multiple_submissions: data.allow_multiple_submissions ?? false,
      is_graded: data.is_graded ?? false,
      passing_score: data.passing_score ?? null,
      open_date: toDatetimeLocal(data.open_date),
      close_date: toDatetimeLocal(data.close_date),
      questions: (data.questions || []).map(q => ({ ...q, choices: q.choices || [] })),
      audience: data.audience || [],
    }
  } catch (e) {
    toast.error('Failed to load survey.')
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  return {
    ...form.value,
    open_date: form.value.open_date || null,
    close_date: form.value.close_date || null,
    passing_score: form.value.is_graded ? (form.value.passing_score ?? null) : null,
    questions: form.value.questions.map((q, i) => ({
      ...q,
      order: i,
      choices: isAutoChoiceType(q.question_type) ? [] : q.choices,
    })),
  }
}

async function saveSurvey() {
  saving.value = true
  saveError.value = null
  try {
    if (isEdit.value) {
      await api.put(`/api/surveys/admin/${surveyId.value}/`, buildPayload())
      router.push({ name: 'survey-admin' })
    } else {
      const res = await api.post('/api/surveys/admin/', buildPayload())
      router.push({ name: 'survey-builder-edit', params: { id: res.data.id } })
    }
  } catch (e) {
    const data = e.response?.data
    if (typeof data === 'string') {
      saveError.value = data
    } else if (data?.error) {
      saveError.value = data.error
    } else if (data?.detail) {
      saveError.value = data.detail
    } else if (data && typeof data === 'object') {
      saveError.value = Object.values(data).flat().join(' ')
    } else {
      saveError.value = 'Save failed.'
    }
  } finally {
    saving.value = false
  }
}

onMounted(loadSurvey)
</script>
