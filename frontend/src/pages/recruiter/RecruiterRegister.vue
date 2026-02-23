<template>
  <div class="container mt-2">
    <div class="d-flex mb-5">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <div class="section-card" style="max-width: 800px; margin: 0 auto;">
      <h2 class="section-title mb-4">
        <i class="bi bi-building me-2"></i>Recruiter Registration
      </h2>
      <p class="text-muted mb-4">Register your organization to participate in the Tau Beta Pi Convention career fair.</p>

      <div v-if="submitted" class="alert alert-success">
        <i class="bi bi-check-circle-fill me-2"></i>
        Registration submitted! Please check your email to activate your account.
      </div>

      <form v-else @submit.prevent="handleSubmit">
        <div v-if="errorMessage" class="alert alert-danger mb-4">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
        </div>

        <!-- Personal Information -->
        <h5 class="fw-bold mb-3">Personal Information</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label">First Name *</label>
            <input v-model.trim="form.first_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label">Last Name *</label>
            <input v-model.trim="form.last_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label">Email *</label>
            <input v-model.trim="form.email" type="email" class="form-control" :class="{'is-invalid': emailError}" required maxlength="254" @blur="validateEmail" @input="validateEmail">
            <div v-if="emailError" class="text-danger small mt-1">{{ emailError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" @input="formatPhone('phone')" @blur="validatePhoneField('phone', phoneError)" type="tel" class="form-control" :class="{'is-invalid': phoneError}" placeholder="(555) 123-4567" maxlength="14">
            <div v-if="phoneError" class="text-danger small mt-1">{{ phoneError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Cell Phone</label>
            <input v-model="form.cell_phone" @input="formatPhone('cell_phone')" @blur="validatePhoneField('cell_phone', cellPhoneError)" type="tel" class="form-control" :class="{'is-invalid': cellPhoneError}" placeholder="(555) 123-4567" maxlength="14">
            <div v-if="cellPhoneError" class="text-danger small mt-1">{{ cellPhoneError }}</div>
          </div>
        </div>

        <!-- Password -->
        <h5 class="fw-bold mb-3">Create Password</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label">Password *</label>
            <input v-model="form.password1" type="password" class="form-control" required minlength="8" maxlength="128">
            <small class="form-text text-muted">Min 8 chars, uppercase, lowercase, number, special character</small>
          </div>
          <div class="col-md-6">
            <label class="form-label">Confirm Password *</label>
            <input v-model="form.password2" type="password" class="form-control" required minlength="8" maxlength="128">
          </div>
        </div>

        <!-- Organization Information -->
        <h5 class="fw-bold mb-3">Organization Information</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-8">
            <label class="form-label">Organization Name *</label>
            <input v-model.trim="form.org_name" type="text" class="form-control" required maxlength="255">
          </div>
          <div class="col-md-4">
            <label class="form-label">Type *</label>
            <select v-model="form.org_type" class="form-select" required>
              <option value="">Select...</option>
              <option value="business">Business</option>
              <option value="graduate_school">Graduate School</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label">Website</label>
            <input v-model.trim="form.org_website" type="url" class="form-control" placeholder="https://..." maxlength="200">
          </div>
          <div class="col-md-6">
            <label class="form-label">Organization Phone</label>
            <input v-model="form.org_phone" @input="formatPhone('org_phone')" @blur="validatePhoneField('org_phone', orgPhoneError)" type="tel" class="form-control" :class="{'is-invalid': orgPhoneError}" placeholder="(555) 123-4567" maxlength="14">
            <div v-if="orgPhoneError" class="text-danger small mt-1">{{ orgPhoneError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Address Line 1 *</label>
            <input v-model.trim="form.org_address_line1" type="text" class="form-control" required maxlength="255">
          </div>
          <div class="col-md-6">
            <label class="form-label">Address Line 2</label>
            <input v-model.trim="form.org_address_line2" type="text" class="form-control" maxlength="255">
          </div>
          <div class="col-md-4">
            <label class="form-label">City *</label>
            <input v-model.trim="form.org_city" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-4">
            <label class="form-label">State</label>
            <select v-if="form.org_country === 'United States'" v-model="form.org_state" class="form-select">
              <option value="">Select state...</option>
              <option v-for="s in usStates" :key="s.id" :value="s.abbrev">{{ s.name }}</option>
            </select>
            <input v-else v-model.trim="form.org_state" type="text" class="form-control" maxlength="100">
          </div>
          <div class="col-md-4">
            <label class="form-label">Zip Code</label>
            <input v-model.trim="form.org_zip_code" type="text" class="form-control" maxlength="20">
          </div>
          <div class="col-md-4">
            <label class="form-label"># of Recruiters Attending *</label>
            <input v-model.number="form.org_num_recruiters" type="number" class="form-control" min="1" required>
          </div>
        </div>

        <!-- Billing Contact -->
        <h5 class="fw-bold mb-3">Billing Contact</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label">Billing Contact First Name *</label>
            <input v-model.trim="form.org_billing_contact_first_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label">Billing Contact Last Name *</label>
            <input v-model.trim="form.org_billing_contact_last_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label">Billing Email *</label>
            <input v-model.trim="form.org_billing_email" type="email" class="form-control" :class="{'is-invalid': billingEmailError}" required maxlength="254" @blur="validateBillingEmail" @input="validateBillingEmail">
            <div v-if="billingEmailError" class="text-danger small mt-1">{{ billingEmailError }}</div>
          </div>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Submitting...</span>
          <span v-else><i class="bi bi-check2 me-2"></i>Create Account</span>
        </button>

        <p class="mt-3 text-muted">
          Already have an account? <router-link to="/login">Login</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { useAuthStore } from '../../store/auth'
import { isValidEmail, validatePhone } from '../../utils/validation'

const authStore = useAuthStore()
const usStates = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/api/accounts/states-provinces')
    usStates.value = res.data['United States'] || []
  } catch {
    // dropdown stays empty; text input fallback still shows
  }
})
const saving = ref(false)
const submitted = ref(false)
const errorMessage = ref('')
const emailError = ref('')
const billingEmailError = ref('')
const phoneError = ref('')
const cellPhoneError = ref('')
const orgPhoneError = ref('')

const cleanPhone = (value) => {
  if (!value) return ''
  return value.replace(/\D/g, '')
}

const formatPhoneNumber = (value) => {
  if (!value) return value
  const cleaned = cleanPhone(value)
  if (cleaned.length === 10) {
    return `(${cleaned.substr(0, 3)}) ${cleaned.substr(3, 3)}-${cleaned.substr(6, 4)}`
  }
  return cleaned
}

const formatPhone = (field) => {
  form.value[field] = formatPhoneNumber(form.value[field])
}

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  cell_phone: '',
  password1: '',
  password2: '',
  org_name: '',
  org_type: '',
  org_website: '',
  org_phone: '',
  org_address_line1: '',
  org_address_line2: '',
  org_city: '',
  org_state: '',
  org_zip_code: '',
  org_country: 'United States',
  org_billing_email: '',
  org_billing_contact_first_name: '',
  org_billing_contact_last_name: '',
  org_num_recruiters: 1,
})

const validateEmail = () => {
  emailError.value = form.value.email && !isValidEmail(form.value.email)
    ? 'Please enter a valid email address'
    : ''
}

const validateBillingEmail = () => {
  billingEmailError.value = form.value.org_billing_email && !isValidEmail(form.value.org_billing_email)
    ? 'Please enter a valid email address'
    : ''
}

const validatePhoneField = (field, errorRef) => {
  const value = form.value[field]
  if (!value) {
    errorRef.value = ''
    return
  }
  const result = validatePhone(cleanPhone(value))
  errorRef.value = result.valid ? '' : result.error
}

const handleSubmit = async () => {
  errorMessage.value = ''

  // Run validations
  validateEmail()
  validateBillingEmail()
  validatePhoneField('phone', phoneError)
  validatePhoneField('cell_phone', cellPhoneError)
  validatePhoneField('org_phone', orgPhoneError)

  if (emailError.value || billingEmailError.value || phoneError.value || cellPhoneError.value || orgPhoneError.value) {
    errorMessage.value = 'Please fix the validation errors above.'
    return
  }

  saving.value = true

  // Get CSRF token first
  await authStore.setCsrfToken()

  try {
    await api.post('/api/recruiters/register/', form.value)
    submitted.value = true
  } catch (error) {
    const data = error.response?.data
    if (data?.errors) {
      // Map field-specific errors to their inline displays
      if (data.errors.email) {
        emailError.value = [data.errors.email].flat()[0]
      }
      if (data.errors.org_billing_email) {
        billingEmailError.value = [data.errors.org_billing_email].flat()[0]
      }
      // Only show the banner for errors without a dedicated field display
      const remaining = Object.entries(data.errors)
        .filter(([k]) => k !== 'email' && k !== 'org_billing_email')
        .map(([, v]) => [v].flat().join(' '))
        .join(' ')
      if (remaining) {
        errorMessage.value = remaining
      }
    } else {
      errorMessage.value = data?.error || data?.detail || 'Registration failed. Please try again.'
    }
  } finally {
    saving.value = false
  }
}
</script>
