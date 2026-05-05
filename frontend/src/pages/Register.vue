<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Register for an Account</h1>
    <form @submit.prevent="register" class="container-md">
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
          @blur="validateEmail"
        />
        <div class="invalid-feedback">{{ emailError }}</div>
      </div>

      <!-- Password -->
      <div class="form-group position-relative">
        <label class="form-label" for="password1">Password:</label>
        <input
          :class="['form-control', { 'is-invalid': passwordError }]"
          v-model="password1"
          id="password1"
          type="password"
          required
          @focus="showPasswordReq = true"
          @blur="onPasswordBlur"
          @input="validatePasswords"
          autocomplete="new-password"
          pattern="[A-Za-z0-9!@#$%^&*_=+\-.]{8,}"
        />
        <div v-if="showPasswordReq" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
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

      <!-- Password Confirm -->
      <div class="form-group position-relative">
        <label class="form-label" for="password2">Confirm Password:</label>
        <input
          :class="['form-control', { 'is-invalid': passwordError }]"
          v-model="password2"
          id="password2"
          type="password"
          required
          @focus="showPassword2Req = true"
          @blur="onPassword2Blur"
          @input="validatePasswords"
          autocomplete="new-password"
        />
        <div v-if="showPassword2Req" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:280px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div class="small">
            <span :style="passwordsMatch ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordsMatch ? '✓' : '✗' }}</span>
            <span :class="{'text-success': passwordsMatch, 'text-danger': !passwordsMatch}"> Passwords match</span>
          </div>
        </div>
        <div class="invalid-feedback">{{ passwordError }}</div>
      </div>
      <button class="btn btn-danger mt-5 me-4" type="button" @click="router.push('/login')">Back</button>
      <button class="btn btn-primary mt-5" type="submit">Register</button>
    </form>

    <!-- Server messages -->
    <div v-if="error" class="alert alert-danger mt-3" role="alert">{{ error }}</div>
    <div v-if="success" class="text-success mt-4 fw-bold">{{ success }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../store/auth'
import { isValidEmail } from '../utils/validation'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password1 = ref('')
const password2 = ref('')
const error = ref('')
const success = ref('')
const emailError = ref('')
const passwordError = ref('')
const showPasswordReq = ref(false)
const showPassword2Req = ref(false)

const passwordLength  = computed(() => password1.value.length >= 8)
const passwordUpper   = computed(() => /[A-Z]/.test(password1.value))
const passwordLower   = computed(() => /[a-z]/.test(password1.value))
const passwordNumber  = computed(() => /[0-9]/.test(password1.value))
const passwordSpecial = computed(() => /[!@#$%^&*_=+\-.]/.test(password1.value))
const passwordSafe    = computed(() => !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(password1.value))
const passwordsMatch  = computed(() => password1.value.length > 0 && password1.value === password2.value)

function onPasswordBlur() { setTimeout(() => { showPasswordReq.value = false }, 200) }
function onPassword2Blur() { setTimeout(() => { showPassword2Req.value = false }, 200) }

function validateEmail() {
  emailError.value = isValidEmail(email.value) ? '' : 'Please enter a valid email address.'
}

function validatePasswords() {
  if (password1.value && password2.value && password1.value !== password2.value) {
    passwordError.value = 'Passwords do not match.'
  } else {
    passwordError.value = ''
  }
  return (
    passwordLength.value && passwordUpper.value && passwordLower.value &&
    passwordNumber.value && passwordSpecial.value && passwordSafe.value
  )
}

async function register() {
  validateEmail()
  const passwordsValid = validatePasswords()
  if (emailError.value || passwordError.value || !passwordsValid) {
    error.value = 'Please fix the highlighted errors before submitting.'
    return
  }
  error.value = ''
  try {
    await api.post('/api/accounts/register', {
      email: email.value,
      password1: password1.value,
      password2: password2.value,
    })
    success.value = 'Registration successful! Please log in.'
    authStore.clearVerification()
    setTimeout(() => { router.push('/email-confirmation') }, 500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed'
  }
}

onMounted(() => {
  if (authStore.verificationEmail) {
    email.value = authStore.verificationEmail
  }
})
</script>
