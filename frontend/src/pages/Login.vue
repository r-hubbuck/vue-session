<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Member Portal</h1>
    <div>
      <p v-if="hasActivateParam" class="text-success text-center">Your account has been activated!</p>
    </div>
    <form @submit.prevent="login" class="container-md">
      <!-- Email -->
      <div class="form-group">
        <label class="form-label" for="email">Email:</label>
        <input
          :class="['form-control', { 'is-invalid': emailError }]"
          v-model.trim="email"
          id="email"
          type="email"
          maxlength="254"
          required
          :disabled="loading"
        />
        <div class="invalid-feedback">{{ emailError }}</div>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label class="form-label" for="password">Password:</label>
        <input
          :class="['form-control', { 'is-invalid': passwordError }]"
          v-model="password"
          id="password"
          type="password"
          required
          :disabled="loading"
        />
        <div class="invalid-feedback">{{ passwordError }}</div>
      </div>

      <div v-if="authStore.serverMessage" class="alert alert-danger" role="alert">{{ authStore.serverMessage }}</div>

      <button
        class="btn btn-primary mt-5"
        type="submit"
        :disabled="loading"
      >
        {{ loading ? 'Please wait...' : 'Login' }}
      </button>
    </form>
    <div class="container-md mt-5">
      <p class="mt-3">
        <RouterLink class="" to="/password-forgot">Forgot your password?</RouterLink>
      </p>
      <p class="mt-3">Don't have an account yet? Please <RouterLink class="" to="/verify">register</RouterLink> now.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { isValidEmail } from '../utils/validation'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const activateParam = ref(null)
const emailError = ref('')
const passwordError = ref('')
const loading = ref(false)

const hasActivateParam = computed(() => activateParam.value !== null)

function validateEmail() {
  emailError.value = isValidEmail(email.value) ? '' : 'Please enter a valid email address.'
}

function validatePassword() {
  if (!password.value) {
    passwordError.value = 'Password cannot be empty.'
  } else if (password.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters long.'
  } else {
    passwordError.value = ''
  }
}

async function login() {
  if (loading.value) return
  validateEmail()
  validatePassword()
  if (emailError.value || passwordError.value) return
  loading.value = true
  try {
    await authStore.login(email.value, password.value, router)
    resetForm()
  } catch {
    // auth store handles error messaging
  } finally {
    loading.value = false
  }
}

function resetForm() {
  email.value = ''
  password.value = ''
  emailError.value = ''
  passwordError.value = ''
}

onMounted(() => {
  authStore.clearMessage()
  activateParam.value = new URLSearchParams(window.location.search).get('activate')
})
</script>
