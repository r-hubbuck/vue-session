<template>
  <div class="container mt-2">
    <div class="row justify-content-center">
      <div class="">
        <div class="d-flex">
          <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
        </div>
        <h1 class="page-title text-center my-4">Resend Activation Email</h1>
        <p class="text-muted text-center mb-4">Enter your email address and we'll send you a new activation link.</p>

        <div v-if="success" class="alert alert-success container-md" role="alert">
          <i class="bi bi-check-circle-fill me-2"></i>{{ success }}
        </div>

        <form v-else @submit.prevent="submit" class="container-md">
          <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

          <div class="mb-3">
            <label for="email" class="form-label">Email:</label>
            <input
              v-model.trim="email"
              type="email"
              maxlength="254"
              :class="['form-control', { 'is-invalid': emailError }]"
              id="email"
              required
              :disabled="loading"
              @blur="validateEmail"
              @input="validateEmail"
            />
            <div class="invalid-feedback">{{ emailError }}</div>
          </div>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !!emailError"
          >
            {{ loading ? 'Sending...' : 'Resend Activation Email' }}
          </button>
        </form>

        <p class="text-center mt-3">
          <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import { isValidEmail } from '../utils/validation'

const email = ref('')
const error = ref('')
const success = ref('')
const emailError = ref('')
const loading = ref(false)

function validateEmail() {
  emailError.value = isValidEmail(email.value) ? '' : 'Please enter a valid email address.'
}

async function submit() {
  validateEmail()
  if (emailError.value) return
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await api.post('/api/accounts/resend-activation', { email: email.value })
    success.value = response.data.message
    email.value = ''
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to send activation email. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
