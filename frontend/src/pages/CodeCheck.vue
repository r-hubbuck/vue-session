<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Code Verification</h1>
    <div>
      <form @submit.prevent="verify" class="container-md">
        <p class="mt-4 mb-3">Please check your email for a 5-digit verification code. <br/><small>If you are not recieving these emails, please contact <a href="mailto:tbp.it@tbp.org">tbp.it@tbp.org</a>.</small></p>
        <div class="form-group">
          <label class="form-label" for="code">Code:</label>
          <input
            :class="['form-control', { 'is-invalid': codeError || error }]"
            v-model="code"
            id="code"
            type="text"
            required
            @input="resetError"
            @blur="validateCode"
          />
          <div class="invalid-feedback">{{ codeError || error }}</div>
        </div>

        <button class="btn btn-primary mt-5" type="submit">Verify</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const code = ref('')
const error = ref('')
const codeError = ref('')

function validateCode() {
  codeError.value = /^\d{5}$/.test(code.value) ? '' : 'Code must be exactly 5 digits.'
}

async function verify() {
  validateCode()
  if (codeError.value) return
  await authStore.verify(code.value, router)
  error.value = authStore.error || ''
}

function resetError() {
  error.value = ''
  codeError.value = ''
}
</script>

<style scoped>
.container-sm {
  max-width: 540px !important;
  width: 100%;
}
</style>
