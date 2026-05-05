<template>
  <div class="container mt-2">
    <div class="row justify-content-center">
      <div class="">
        <div class="d-flex">
          <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
        </div>
        <h1 class="page-title text-center my-4">Reset Your Password</h1>
        <p class="text-muted text-center mb-4">Enter your email address and we'll send you a link to reset your password.</p>

        <div v-if="success" class="alert alert-success" role="alert">
          {{ success }}
        </div>

        <form v-else @submit.prevent="requestPasswordReset" class="container-md">
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

          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading || !!emailError"
          >
            {{ loading ? 'Sending...' : 'Send Reset Link' }}
          </button>
        </form>

        <p class="text-center mt-3">
          <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
        </p>

        <p class="text-center mt-3">
          Don't have an account yet? Please <RouterLink to="/verify" class="text-decoration-none">register</RouterLink> now.
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

async function requestPasswordReset() {
  validateEmail()
  if (emailError.value) return
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await api.post('/api/accounts/password-reset-request', { email: email.value })
    success.value = response.data.message || 'Password reset email has been sent. Please allow a few minutes for it to arrive to your inbox.'
    email.value = ''
  } catch (err) {
    error.value = err.response?.data?.error || err.response?.data?.message || 'Failed to send reset email'
  } finally {
    loading.value = false
  }
}
</script>
