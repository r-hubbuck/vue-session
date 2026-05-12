<template>
  <div class="section-card">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="fw-bold mb-0"><i class="bi bi-lock me-2"></i>Change Password</h5>
      <button v-if="!showForm" type="button" class="btn btn-outline-secondary btn-sm" @click="showForm = true">
        <i class="bi bi-pencil me-1"></i>Change Password
      </button>
      <button v-else type="button" class="btn btn-link btn-sm text-muted p-0" @click="cancel">
        Cancel
      </button>
    </div>

    <p v-if="!showForm" class="text-muted small mb-0">Click "Change Password" to update your password.</p>

    <form v-if="showForm" @submit.prevent="submit" style="max-width: 480px;">
      <!-- Current Password -->
      <div class="mb-3">
        <label class="form-label" for="current-password">Current Password</label>
        <input
          id="current-password"
          v-model="currentPassword"
          type="password"
          :class="['form-control', { 'is-invalid': currentPasswordError }]"
          autocomplete="current-password"
          @input="currentPasswordError = ''"
        >
        <div class="invalid-feedback">{{ currentPasswordError }}</div>
      </div>

      <!-- New Password -->
      <div class="mb-3 position-relative">
        <label class="form-label" for="new-password">New Password</label>
        <input
          id="new-password"
          v-model="newPassword1"
          type="password"
          :class="['form-control', { 'is-invalid': newPasswordError }]"
          autocomplete="new-password"
          @focus="showReq = true"
          @blur="onNewPasswordBlur"
          @input="newPasswordError = ''"
        >
        <div v-if="showReq" class="password-req-box bg-light border rounded p-2" style="position:absolute; left:0; top:100%; min-width:340px; z-index:100; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div class="small">
            <span :style="reqLen ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqLen ? '✓' : '✗' }}</span>
            <span :class="reqLen ? 'text-success' : 'text-danger'"> At least 8 characters</span>
          </div>
          <div class="small">
            <span :style="reqUpper ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqUpper ? '✓' : '✗' }}</span>
            <span :class="reqUpper ? 'text-success' : 'text-danger'"> At least one uppercase letter</span>
          </div>
          <div class="small">
            <span :style="reqLower ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqLower ? '✓' : '✗' }}</span>
            <span :class="reqLower ? 'text-success' : 'text-danger'"> At least one lowercase letter</span>
          </div>
          <div class="small">
            <span :style="reqNumber ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqNumber ? '✓' : '✗' }}</span>
            <span :class="reqNumber ? 'text-success' : 'text-danger'"> At least one number</span>
          </div>
          <div class="small">
            <span :style="reqSpecial ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqSpecial ? '✓' : '✗' }}</span>
            <span :class="reqSpecial ? 'text-success' : 'text-danger'"> At least one special character (!@#$%^&*_=+-.)</span>
          </div>
          <div class="small">
            <span :style="reqSafe ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ reqSafe ? '✓' : '✗' }}</span>
            <span :class="reqSafe ? 'text-success' : 'text-danger'"> No invalid characters</span>
          </div>
        </div>
        <div class="invalid-feedback">{{ newPasswordError }}</div>
      </div>

      <!-- Confirm New Password -->
      <div class="mb-4">
        <label class="form-label" for="confirm-password">Confirm New Password</label>
        <input
          id="confirm-password"
          v-model="newPassword2"
          type="password"
          :class="['form-control', { 'is-invalid': confirmError }]"
          autocomplete="new-password"
          @input="confirmError = ''"
        >
        <div class="invalid-feedback">{{ confirmError }}</div>
      </div>

      <div v-if="serverError" class="alert alert-danger mb-3" role="alert">{{ serverError }}</div>

      <button type="submit" class="btn btn-primary" :disabled="saving">
        <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
        <span v-else><i class="bi bi-check2 me-2"></i>Change Password</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'
import { useToast } from 'vue-toastification'

const toast = useToast()

const showForm = ref(false)
const currentPassword = ref('')
const newPassword1 = ref('')
const newPassword2 = ref('')
const showReq = ref(false)
const saving = ref(false)
const currentPasswordError = ref('')
const newPasswordError = ref('')
const confirmError = ref('')
const serverError = ref('')

const cancel = () => {
  showForm.value = false
  currentPassword.value = ''
  newPassword1.value = ''
  newPassword2.value = ''
  currentPasswordError.value = ''
  newPasswordError.value = ''
  confirmError.value = ''
  serverError.value = ''
}

const reqLen     = computed(() => newPassword1.value.length >= 8)
const reqUpper   = computed(() => /[A-Z]/.test(newPassword1.value))
const reqLower   = computed(() => /[a-z]/.test(newPassword1.value))
const reqNumber  = computed(() => /[0-9]/.test(newPassword1.value))
const reqSpecial = computed(() => /[!@#$%^&*_=+\-.]/.test(newPassword1.value))
const reqSafe    = computed(() => !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(newPassword1.value))

const onNewPasswordBlur = () => setTimeout(() => { showReq.value = false }, 200)

const validate = () => {
  let valid = true
  if (!currentPassword.value) {
    currentPasswordError.value = 'Please enter your current password.'
    valid = false
  }
  if (!reqLen.value || !reqUpper.value || !reqLower.value || !reqNumber.value || !reqSpecial.value || !reqSafe.value) {
    newPasswordError.value = 'New password does not meet the requirements above.'
    valid = false
  }
  if (!newPassword2.value) {
    confirmError.value = 'Please confirm your new password.'
    valid = false
  } else if (newPassword1.value !== newPassword2.value) {
    confirmError.value = 'Passwords do not match.'
    valid = false
  }
  return valid
}

const submit = async () => {
  serverError.value = ''
  if (!validate() || saving.value) return
  saving.value = true
  try {
    await api.post('/api/accounts/change-password', {
      current_password: currentPassword.value,
      new_password1: newPassword1.value,
      new_password2: newPassword2.value,
    })
    showForm.value = false
    currentPassword.value = ''
    newPassword1.value = ''
    newPassword2.value = ''
    toast.success('Password changed successfully.')
  } catch (err) {
    const data = err.response?.data
    if (data?.error) {
      serverError.value = data.error
    } else if (data?.new_password2) {
      confirmError.value = Array.isArray(data.new_password2) ? data.new_password2[0] : data.new_password2
    } else if (data?.new_password1) {
      newPasswordError.value = Array.isArray(data.new_password1) ? data.new_password1[0] : data.new_password1
    } else {
      serverError.value = 'Failed to change password. Please try again.'
    }
  } finally {
    saving.value = false
  }
}
</script>
