<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Verify Tau Beta Pi Membership</h1>
    <form @submit.prevent="submitVerifyForm" class="container-md">
      <div class="form-group row">
        <label class="form-label" for="email">Email:</label>
        <input
          class="form-control"
          :class="{ 'is-invalid': emailError }"
          v-model.trim="formData.email"
          id="email"
          type="email"
          maxlength="254"
          required
          @blur="validateEmail"
          @input="validateEmail"
        >
        <div class="invalid-feedback fw-bold">{{ emailError }}</div>
      </div>
      <div class="form-group row">
        <label class="form-label" for="chapter">Chapter:</label>
        <select class="form-control chapter-select" v-model="formData.chapter" id="chapter" required>
          <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
            {{ chapter.title }}
          </option>
        </select>
      </div>
      <div class="form-group row">
        <label class="form-label" for="year">Graduation Year:</label>
        <select class="form-control" id="year" v-model="formData.year" @change="handleYearChange" required>
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
      <div v-if="errorMessage" class="alert alert-danger mt-3" role="alert">{{ errorMessage }}</div>
      <button class="btn btn-danger mt-5 me-4" type="button" @click="router.push('/login')">Back</button>
      <button class="btn btn-primary mt-5" type="submit">Verify</button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import api from '../api'
import { isValidEmail } from '../utils/validation'

const authStore = useAuthStore()
const router = useRouter()

const chapters = ref([])
const years = generateYearRange(1900, new Date().getFullYear())
const formData = reactive({
  chapter: '',
  email: '',
  year: new Date().getFullYear(),
})
const errorMessage = ref('')
const emailError = ref('')

function generateYearRange(start, end) {
  const range = []
  for (let i = end; i >= start; i--) range.push(i)
  return range
}

function validateEmail() {
  emailError.value = isValidEmail(formData.email) ? '' : 'Please enter a valid email address.'
}

function handleYearChange(event) {
  formData.year = parseInt(event.target.value)
}

async function fetchChapters() {
  try {
    const response = await api.get('/api/accounts/chapter-list')
    chapters.value = Object.values(response.data.chapters)
  } catch {
    errorMessage.value = 'Failed to load chapters'
  }
}

async function submitVerifyForm() {
  validateEmail()
  if (emailError.value) return
  try {
    const response = await api.post('/api/accounts/verify-member', formData)
    if (response.data.message === 'OK') {
      authStore.setVerified(formData.email)
      await router.push({ name: 'register' })
    } else {
      errorMessage.value = response.data.message
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || 'Verification failed'
  }
}

onMounted(async () => {
  authStore.clearMessage()
  await fetchChapters()
  if (authStore.serverMessage) {
    errorMessage.value = authStore.serverMessage
    authStore.clearMessage()
  }
})
</script>
