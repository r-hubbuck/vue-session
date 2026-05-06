<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Reset Your Password</h1>
    <div v-if="tokenError" class="alert alert-danger" role="alert">
      {{ tokenError }}
      <div class="mt-2">
        <RouterLink to="/password-forgot" class="text-decoration-none">Request a new reset link</RouterLink>
      </div>
    </div>

    <div v-else-if="success" class="alert alert-success" role="alert">
      {{ success }}
    </div>

    <form v-else @submit.prevent="resetPassword" class="container-md">
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

      <div class="mb-3 position-relative">
        <label for="newPassword1" class="form-label">New Password:</label>
        <input
          v-model="newPassword1"
          type="password"
          :class="['form-control', { 'is-invalid': passwordError }]"
          id="newPassword1"
          required
          :disabled="loading"
          @focus="showPasswordReq = true"
          @blur="onPasswordBlur"
          @input="validatePasswords"
          autocomplete="new-password"
        />
        <div v-if="showPasswordReq" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="text-align:left; z-index:1050; min-width:320px;">
          <div class="small">
            <span :style="passwordLength ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordLength ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordLength, 'text-danger': !passwordLength}"> At least 8 characters</span>
          </div>
          <div class="small">
            <span :style="passwordUpper ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordUpper ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordUpper, 'text-danger': !passwordUpper}"> At least one uppercase letter</span>
          </div>
          <div class="small">
            <span :style="passwordLower ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordLower ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordLower, 'text-danger': !passwordLower}"> At least one lowercase letter</span>
          </div>
          <div class="small">
            <span :style="passwordNumber ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordNumber ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordNumber, 'text-danger': !passwordNumber}"> At least one number</span>
          </div>
          <div class="small">
            <span :style="passwordSpecial ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordSpecial ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordSpecial, 'text-danger': !passwordSpecial}"> At least one special character (!@#$%^&*_=+-.)</span>
          </div>
          <div class="small">
            <span :style="passwordSafe ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordSafe ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordSafe, 'text-danger': !passwordSafe}"> No invalid characters</span>
          </div>
        </div>
      </div>

      <div class="mb-3 position-relative">
        <label for="newPassword2" class="form-label">Confirm New Password:</label>
        <input
          v-model="newPassword2"
          type="password"
          :class="['form-control', { 'is-invalid': passwordError }]"
          id="newPassword2"
          required
          :disabled="loading"
          @focus="showPassword2Req = true"
          @blur="onPassword2Blur"
          @input="validatePasswords"
          autocomplete="new-password"
        />
        <div v-if="showPassword2Req" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="text-align:left; z-index:1050; min-width:280px;">
          <div class="small">
            <span :style="passwordsMatch ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordsMatch ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordsMatch, 'text-danger': !passwordsMatch}"> Passwords match</span>
          </div>
        </div>
        <div class="invalid-feedback">{{ passwordError }}</div>
      </div>

      <button
        type="submit"
        class="btn btn-primary mt-5"
        :disabled="loading || !isFormValid"
      >
        {{ loading ? 'Updating...' : 'Update Password' }}
      </button>
    </form>

    <p class="text-center mt-3">
      <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()

const newPassword1 = ref('')
const newPassword2 = ref('')
const error = ref('')
const success = ref('')
const tokenError = ref('')
const passwordError = ref('')
const loading = ref(false)
const showPasswordReq = ref(false)
const showPassword2Req = ref(false)
const uidb64 = ref('')
const token = ref('')

const passwordLength  = computed(() => newPassword1.value.length >= 8)
const passwordUpper   = computed(() => /[A-Z]/.test(newPassword1.value))
const passwordLower   = computed(() => /[a-z]/.test(newPassword1.value))
const passwordNumber  = computed(() => /[0-9]/.test(newPassword1.value))
const passwordSpecial = computed(() => /[!@#$%^&*_=+\-.]/.test(newPassword1.value))
const passwordSafe    = computed(() => !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(newPassword1.value))
const passwordsMatch  = computed(() => newPassword1.value.length > 0 && newPassword1.value === newPassword2.value)

const isFormValid = computed(() =>
  passwordLength.value && passwordUpper.value && passwordLower.value &&
  passwordNumber.value && passwordSpecial.value && passwordSafe.value &&
  passwordsMatch.value && !passwordError.value
)

function onPasswordBlur()  { setTimeout(() => { showPasswordReq.value  = false }, 200) }
function onPassword2Blur() { setTimeout(() => { showPassword2Req.value = false }, 200) }

function validatePasswords() {
  if (newPassword1.value && newPassword2.value && newPassword1.value !== newPassword2.value) {
    passwordError.value = 'Passwords do not match.'
  } else {
    passwordError.value = ''
  }
}

async function resetPassword() {
  validatePasswords()
  if (!isFormValid.value) return
  loading.value = true
  error.value = ''
  try {
    const response = await api.post(
      `/api/accounts/password-reset-confirm/${uidb64.value}/${token.value}/`,
      { new_password1: newPassword1.value, new_password2: newPassword2.value }
    )
    success.value = response.data.message || 'Password has been reset successfully! You can now log in with your new password.'
    newPassword1.value = ''
    newPassword2.value = ''
  } catch (err) {
    const data = err.response?.data
    if (err.response?.status === 400) {
      error.value = data?.error || data?.new_password1?.[0] || data?.new_password2?.[0] || 'Invalid password. Please check the requirements.'
    } else {
      error.value = data?.error || data?.message || 'Failed to reset password'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  uidb64.value = route.params.uidb64
  token.value  = route.params.token
  if (!uidb64.value || !token.value) {
    tokenError.value = 'Invalid reset link. Please request a new password reset.'
  }
})
</script>
