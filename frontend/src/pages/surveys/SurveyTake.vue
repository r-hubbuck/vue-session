<template>
  <div class="container mt-4" style="max-width:800px">

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="loadError" class="alert alert-danger">{{ loadError }}</div>

    <template v-else-if="survey">
      <!-- Already submitted banner -->
      <div v-if="responseData?.is_complete" class="alert alert-success d-flex align-items-center gap-2 mb-4">
        <i class="bi bi-check-circle-fill fs-4"></i>
        <div>
          <strong>You have already submitted this survey.</strong>
          <span v-if="survey.is_graded && responseData.score !== null">
            &nbsp;Score: {{ responseData.score }} / {{ responseData.total_possible_points }}
          </span>
        </div>
      </div>

      <!-- Submission success message -->
      <div v-if="submitMsg" class="alert alert-success d-flex align-items-center gap-3 mb-4">
        <i class="bi bi-check-circle-fill fs-4"></i>
        <div>
          <strong>{{ submitMsg }}</strong>
          <div class="mt-2">
            <router-link :to="{ name: 'survey-list' }" class="btn btn-sm btn-outline-success">
              Back to Surveys
            </router-link>
          </div>
        </div>
      </div>

      <div v-if="!submitMsg">
        <!-- Survey header -->
        <div class="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h1 class="mb-1">{{ survey.title }}</h1>
            <p v-if="survey.description" class="text-muted mb-0">{{ survey.description }}</p>
          </div>
          <div v-if="saving" class="badge bg-secondary">
            <span class="spinner-border spinner-border-sm me-1"></span> Saving…
          </div>
        </div>

        <div v-if="submitError" class="alert alert-danger">{{ submitError }}</div>

        <!-- Questions -->
        <div v-for="question in survey.questions" :key="question.id" class="card mb-3">
          <div class="card-body">
            <p class="fw-semibold mb-1">
              {{ question.order + 1 }}. {{ question.question_text }}
              <span v-if="question.is_required" class="text-danger ms-1" title="Required">*</span>
            </p>
            <p v-if="question.help_text" class="text-muted small mb-2">{{ question.help_text }}</p>

            <!-- Multiple choice / dropdown: single select -->
            <div v-if="question.question_type === 'multiple_choice' || question.question_type === 'dropdown'">
              <div v-if="question.question_type === 'dropdown'">
                <select
                  :value="getSingleChoice(question.id)"
                  @change="setSingleChoice(question.id, +$event.target.value)"
                  class="form-select"
                  :disabled="responseData?.is_complete"
                >
                  <option value="">— Select an answer —</option>
                  <option v-for="c in question.choices" :key="c.id" :value="c.id">{{ c.choice_text }}</option>
                </select>
              </div>
              <div v-else>
                <div v-for="c in question.choices" :key="c.id" class="form-check">
                  <input
                    :id="`q${question.id}-c${c.id}`"
                    class="form-check-input"
                    type="radio"
                    :name="`q${question.id}`"
                    :value="c.id"
                    :checked="getSingleChoice(question.id) === c.id"
                    @change="setSingleChoice(question.id, c.id); onAnswerChange()"
                    :disabled="responseData?.is_complete"
                  />
                  <label :for="`q${question.id}-c${c.id}`" class="form-check-label">{{ c.choice_text }}</label>
                </div>
              </div>
            </div>

            <!-- True/False and Yes/No: radio -->
            <div v-else-if="question.question_type === 'true_false' || question.question_type === 'yes_no'">
              <div v-for="c in question.choices" :key="c.id" class="form-check form-check-inline">
                <input
                  :id="`q${question.id}-c${c.id}`"
                  class="form-check-input"
                  type="radio"
                  :name="`q${question.id}`"
                  :value="c.id"
                  :checked="getSingleChoice(question.id) === c.id"
                  @change="setSingleChoice(question.id, c.id); onAnswerChange()"
                  :disabled="responseData?.is_complete"
                />
                <label :for="`q${question.id}-c${c.id}`" class="form-check-label">{{ c.choice_text }}</label>
              </div>
            </div>

            <!-- Checkbox: multi-select -->
            <div v-else-if="question.question_type === 'checkbox'">
              <div v-for="c in question.choices" :key="c.id" class="form-check">
                <input
                  :id="`q${question.id}-c${c.id}`"
                  class="form-check-input"
                  type="checkbox"
                  :value="c.id"
                  :checked="isChoiceSelected(question.id, c.id)"
                  @change="toggleChoice(question.id, c.id); onAnswerChange()"
                  :disabled="responseData?.is_complete"
                />
                <label :for="`q${question.id}-c${c.id}`" class="form-check-label">{{ c.choice_text }}</label>
              </div>
            </div>

            <!-- Short answer -->
            <input
              v-else-if="question.question_type === 'short_answer'"
              v-model="answers[question.id].text_answer"
              type="text"
              class="form-control"
              placeholder="Your answer"
              :disabled="responseData?.is_complete"
              @input="onAnswerChange()"
            />

            <!-- Essay -->
            <textarea
              v-else-if="question.question_type === 'essay'"
              v-model="answers[question.id].text_answer"
              class="form-control"
              rows="5"
              placeholder="Your answer"
              :disabled="responseData?.is_complete"
              @input="onAnswerChange()"
            ></textarea>

            <!-- Rating -->
            <div v-else-if="question.question_type === 'rating'">
              <div class="d-flex align-items-center gap-3">
                <span class="text-muted small">{{ question.rating_min_label || question.rating_min }}</span>
                <input
                  v-model.number="answers[question.id].number_answer"
                  type="range"
                  class="form-range flex-grow-1"
                  :min="question.rating_min"
                  :max="question.rating_max"
                  step="1"
                  :disabled="responseData?.is_complete"
                  @input="onAnswerChange()"
                />
                <span class="text-muted small">{{ question.rating_max_label || question.rating_max }}</span>
              </div>
              <div class="text-center">
                <span class="badge bg-secondary">{{ answers[question.id].number_answer ?? question.rating_min }}</span>
              </div>
            </div>

            <!-- Number -->
            <input
              v-else-if="question.question_type === 'number'"
              v-model.number="answers[question.id].number_answer"
              type="number"
              class="form-control"
              placeholder="Enter a number"
              :disabled="responseData?.is_complete"
              @input="onAnswerChange()"
            />

            <!-- Date -->
            <input
              v-else-if="question.question_type === 'date'"
              v-model="answers[question.id].date_answer"
              type="date"
              class="form-control"
              :disabled="responseData?.is_complete"
              @change="onAnswerChange()"
            />
          </div>
        </div>

        <!-- Submit button -->
        <div v-if="!responseData?.is_complete" class="d-flex justify-content-end gap-2 mb-5">
          <router-link :to="{ name: 'survey-list' }" class="btn btn-outline-secondary">Save &amp; Exit</router-link>
          <button @click="submitSurvey" :disabled="submitting" class="btn btn-primary">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
            Submit
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api'

const route = useRoute()
const router = useRouter()
const surveyId = route.params.id

const survey = ref(null)
const responseData = ref(null)
const answers = reactive({})
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const loadError = ref(null)
const submitError = ref(null)
const submitMsg = ref(null)
let debounceTimer = null

// --- Answer helpers ---

function initAnswer(questionId) {
  if (!answers[questionId]) {
    answers[questionId] = { text_answer: '', number_answer: null, date_answer: null, selected_choices: [] }
  }
}

function getSingleChoice(questionId) {
  const a = answers[questionId]
  return a?.selected_choices?.[0] ?? null
}

function setSingleChoice(questionId, choiceId) {
  initAnswer(questionId)
  answers[questionId].selected_choices = [choiceId]
}

function isChoiceSelected(questionId, choiceId) {
  return answers[questionId]?.selected_choices?.includes(choiceId) ?? false
}

function toggleChoice(questionId, choiceId) {
  initAnswer(questionId)
  const arr = answers[questionId].selected_choices
  const idx = arr.indexOf(choiceId)
  if (idx === -1) arr.push(choiceId)
  else arr.splice(idx, 1)
}

// --- Load ---

async function loadSurvey() {
  loading.value = true
  loadError.value = null
  try {
    const [surveyRes, myResponseRes] = await Promise.all([
      api.get(`/api/surveys/${surveyId}/`),
      api.get(`/api/surveys/${surveyId}/my-response/`),
    ])

    survey.value = surveyRes.data

    // Initialize blank answers for every question
    for (const q of survey.value.questions) {
      initAnswer(q.id)
      if (q.question_type === 'rating' && q.rating_min != null) {
        answers[q.id].number_answer = q.rating_min
      }
    }

    // Restore existing answers if there's already a response
    const existing = myResponseRes.data.response
    if (existing) {
      responseData.value = existing
      for (const ans of existing.answers) {
        initAnswer(ans.question)
        answers[ans.question] = {
          text_answer: ans.text_answer ?? '',
          number_answer: ans.number_answer != null ? parseFloat(ans.number_answer) : null,
          date_answer: ans.date_answer ?? null,
          selected_choices: ans.selected_choices ?? [],
        }
      }
    } else {
      // Start a new response
      const startRes = await api.post(`/api/surveys/${surveyId}/start/`)
      responseData.value = { id: startRes.data.response_id, is_complete: false }
    }
  } catch (e) {
    loadError.value = e.response?.data?.error || 'Failed to load survey.'
  } finally {
    loading.value = false
  }
}

// --- Draft save ---

function buildPayload() {
  return {
    answers: Object.entries(answers).map(([qId, ans]) => ({
      question: parseInt(qId),
      text_answer: ans.text_answer ?? '',
      number_answer: ans.number_answer ?? null,
      date_answer: ans.date_answer ?? null,
      selected_choices: ans.selected_choices ?? [],
    })),
  }
}

async function saveDraft() {
  if (!responseData.value?.id || responseData.value?.is_complete) return
  saving.value = true
  try {
    await api.put(`/api/surveys/${surveyId}/responses/${responseData.value.id}/`, buildPayload())
  } catch {
    // Silent draft save failure
  } finally {
    saving.value = false
  }
}

function onAnswerChange() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(saveDraft, 1500)
}

// --- Submit ---

async function submitSurvey() {
  if (!confirm('Submit your answers? You will not be able to change them after submitting.')) return
  submitting.value = true
  submitError.value = null
  try {
    const res = await api.post(
      `/api/surveys/${surveyId}/responses/${responseData.value.id}/submit/`,
      buildPayload()
    )
    responseData.value = res.data
    if (survey.value.is_graded && res.data.score !== null) {
      submitMsg.value = `Submitted! Your score: ${res.data.score} / ${res.data.total_possible_points}`
    } else {
      submitMsg.value = 'Thank you — your response has been submitted!'
    }
  } catch (e) {
    submitError.value = e.response?.data?.error || 'Submission failed. Please try again.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadSurvey)
</script>
