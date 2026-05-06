<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Member Portal</h1>
    <div>
      <div v-if="hasActivateParam" class="alert alert-success container-md text-center" role="alert">
        <i class="bi bi-check-circle-fill me-2"></i>Your account has been activated!
      </div>
    </div>
    <form @submit.prevent="login" class="container-md">
      <div v-if="authStore.serverMessage" class="alert alert-danger" role="alert">{{ authStore.serverMessage }}</div>

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

      <button
        class="btn btn-primary mt-5"
        type="submit"
        :disabled="loading"
      >
        {{ loading ? 'Please wait...' : 'Login' }}
      </button>
    </form>
    <div class="container-md mt-4">
      <div class="d-flex flex-column align-items-center gap-2 text-center">
        <RouterLink to="/password-forgot">Forgot your password?</RouterLink>
        <RouterLink to="/resend-activation">Need to resend your activation email?</RouterLink>
        <p class="mb-0">Don't have an account yet? Please <RouterLink to="/verify">register</RouterLink> now.</p>
      </div>
      <hr class="my-3">
      <p class="text-center text-muted mb-0" style="font-size: 0.825rem;">
        Trouble signing in? Contact <a href="mailto:tbp.it@tbp.org">tbp.it@tbp.org</a> for assistance.
      </p>
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
