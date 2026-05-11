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
        <div v-if="errorMessage" class="alert alert-danger mb-4" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
        </div>

        <!-- Organization Information -->
        <h5 class="fw-bold mb-3 mt-5">Organization Information</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-8">
            <label class="form-label" for="org-name">Organization Name *</label>
            <input id="org-name" v-model.trim="form.org_name" type="text" class="form-control" required maxlength="255">
          </div>
          <div class="col-md-4">
            <label class="form-label" for="org-type">Type *</label>
            <select id="org-type" v-model="form.org_type" class="form-select" required>
              <option value="">Select...</option>
              <option value="business">Business</option>
              <option value="graduate_school">Graduate School</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label" for="org-website">Website *</label>
            <input id="org-website" v-model.trim="form.org_website" type="url" class="form-control" placeholder="https://..." maxlength="200" required
              @invalid="e => e.target.setCustomValidity('Please enter a full URL, e.g. https://example.com')"
              @input="e => e.target.setCustomValidity('')">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="org-phone">Organization Phone</label>
            <input id="org-phone" v-model="form.org_phone" @input="formatPhone('org_phone')" @blur="validatePhoneField('org_phone')" type="tel" :class="['form-control', { 'is-invalid': orgPhoneError }]" placeholder="(555) 123-4567" maxlength="14">
            <div class="invalid-feedback">{{ orgPhoneError }}</div>
          </div>
          <div class="col-md-8">
            <label class="form-label" for="org-logo">Organization Logo</label>
            <input
              id="org-logo"
              type="file"
              :class="['form-control', { 'is-invalid': logoError }]"
              accept=".png,.jpg,.jpeg"
              @change="handleLogoChange"
            >
            <div class="invalid-feedback">{{ logoError }}</div>
            <small class="form-text text-muted">Optional. PNG or JPG only, max 5MB.</small>
          </div>
          <div v-if="logoPreview" class="col-md-4 d-flex align-items-center">
            <img :src="logoPreview" alt="Logo preview" style="max-height: 80px; max-width: 100%; border-radius: 4px;">
          </div>
        </div>

        <!-- Primary Recruiter Information -->
        <h5 class="fw-bold mb-3 mt-5">Primary Recruiter Information</h5>
        <p class="text-muted small mb-3">Important information regarding event details, invoicing, resume bank access, and day-of information will be emailed to this individual to ensure that the recruiters at the event receive all necessary information.</p>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label" for="recruiter-first">First Name *</label>
            <input id="recruiter-first" v-model.trim="form.first_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="recruiter-last">Last Name *</label>
            <input id="recruiter-last" v-model.trim="form.last_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="recruiter-email">Email *</label>
            <input id="recruiter-email" v-model.trim="form.email" type="email" :class="['form-control', { 'is-invalid': emailError }]" required maxlength="254" @blur="validateEmail" @input="validateEmail">
            <div class="invalid-feedback">{{ emailError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label" for="recruiter-phone">Phone</label>
            <input id="recruiter-phone" v-model="form.phone" @input="formatPhone('phone')" @blur="validatePhoneField('phone')" type="tel" :class="['form-control', { 'is-invalid': phoneError }]" placeholder="(555) 123-4567" maxlength="14">
            <div class="invalid-feedback">{{ phoneError }}</div>
          </div>
          <div class="col-md-6">
            <label class="form-label" for="recruiter-cell">Cell Phone</label>
            <input id="recruiter-cell" v-model="form.cell_phone" @input="formatPhone('cell_phone')" @blur="validatePhoneField('cell_phone')" type="tel" :class="['form-control', { 'is-invalid': cellPhoneError }]" placeholder="(555) 123-4567" maxlength="14">
            <div class="invalid-feedback">{{ cellPhoneError }}</div>
          </div>
        </div>

        <!-- Billing Information -->
        <h5 class="fw-bold mb-3 mt-5">Billing Information</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label" for="org-addr1">Address Line 1 *</label>
            <input id="org-addr1" v-model.trim="form.org_address_line1" type="text" class="form-control" required maxlength="255">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="org-addr2">Address Line 2</label>
            <input id="org-addr2" v-model.trim="form.org_address_line2" type="text" class="form-control" maxlength="255">
          </div>
          <div class="col-md-4">
            <label class="form-label" for="org-city">City *</label>
            <input id="org-city" v-model.trim="form.org_city" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-4">
            <label class="form-label" for="org-state">State *</label>
            <select v-if="form.org_country === 'United States'" id="org-state" v-model="form.org_state" class="form-select" required>
              <option value="">Select state...</option>
              <option v-for="s in usStates" :key="s.id" :value="s.abbrev">{{ s.name }}</option>
            </select>
            <input v-else id="org-state" v-model.trim="form.org_state" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-4">
            <label class="form-label" for="org-zip">Zip Code *</label>
            <input id="org-zip" v-model.trim="form.org_zip_code" type="text" class="form-control" required maxlength="20">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="billing-first">Invoice Contact First Name *</label>
            <input id="billing-first" v-model.trim="form.org_billing_contact_first_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="billing-last">Invoice Contact Last Name *</label>
            <input id="billing-last" v-model.trim="form.org_billing_contact_last_name" type="text" class="form-control" required maxlength="100">
          </div>
          <div class="col-md-6">
            <label class="form-label" for="billing-email">Invoice Email *</label>
            <input id="billing-email" v-model.trim="form.org_billing_email" type="email" :class="['form-control', { 'is-invalid': billingEmailError }]" required maxlength="254" @blur="validateBillingEmail" @input="validateBillingEmail">
            <div class="invalid-feedback">{{ billingEmailError }}</div>
          </div>
        </div>

        <!-- Password -->
        <h5 class="fw-bold mb-3 mt-5">Create Password</h5>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label" for="password1">Password *</label>
            <div class="position-relative">
              <input
                id="password1"
                v-model="form.password1"
                type="password"
                class="form-control"
                required
                maxlength="128"
                autocomplete="new-password"
                pattern="[A-Za-z0-9!@#$%^&*_=+\-.]{8,}"
                @focus="showPasswordReq = true"
                @blur="onPasswordBlur"
                @input="validatePasswords"
              >
              <div v-if="showPasswordReq" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <div class="small">
                  <span v-if="passwordLength" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordLength, 'text-danger': !passwordLength}"> At least 8 characters</span>
                </div>
                <div class="small">
                  <span v-if="passwordUpper" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordUpper, 'text-danger': !passwordUpper}"> At least one uppercase letter</span>
                </div>
                <div class="small">
                  <span v-if="passwordLower" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordLower, 'text-danger': !passwordLower}"> At least one lowercase letter</span>
                </div>
                <div class="small">
                  <span v-if="passwordNumber" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordNumber, 'text-danger': !passwordNumber}"> At least one number</span>
                </div>
                <div class="small">
                  <span v-if="passwordSpecial" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordSpecial, 'text-danger': !passwordSpecial}"> At least one special character (!@#$%^&*_=+-.)</span>
                </div>
                <div class="small">
                  <span v-if="passwordSafe" style="color:#28a745; font-weight:bold;">✓</span>
                  <span v-else style="color:red; margin-right:5px;">✗</span>
                  <span :class="{'text-success': passwordSafe, 'text-danger': !passwordSafe}"> No invalid characters</span>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <label class="form-label" for="password2">Confirm Password *</label>
            <div class="position-relative">
              <input
                id="password2"
                v-model="form.password2"
                type="password"
                :class="['form-control', { 'is-invalid': passwordError }]"
                required
                maxlength="128"
                autocomplete="new-password"
                pattern="[A-Za-z0-9!@#$%^&*_=+\-.]{8,}"
                @focus="showPassword2Req = true"
                @blur="onPassword2Blur"
                @input="validatePasswords"
              >
              <div v-if="showPassword2Req" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:240px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
                <div class="small">
                  <span :style="passwordsMatch ? 'color:#28a745;font-weight:bold;' : 'color:red;margin-right:5px;'">{{ passwordsMatch ? '✓' : '✗' }}</span>
                  <span :class="{'text-success': passwordsMatch, 'text-danger': !passwordsMatch}"> Passwords match</span>
                </div>
              </div>
              <div class="invalid-feedback fw-bold">{{ passwordError }}</div>
            </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../../api'
import { isValidEmail, validatePhone, formatPhone as formatPhoneValue } from '../../utils/validation'

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
const passwordError = ref('')
const showPasswordReq = ref(false)
const showPassword2Req = ref(false)

const passwordLength  = computed(() => form.value.password1.length >= 8)
const passwordUpper   = computed(() => /[A-Z]/.test(form.value.password1))
const passwordLower   = computed(() => /[a-z]/.test(form.value.password1))
const passwordNumber  = computed(() => /[0-9]/.test(form.value.password1))
const passwordSpecial = computed(() => /[!@#$%^&*_=+\-.]/.test(form.value.password1))
const passwordSafe    = computed(() => !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(form.value.password1))

const passwordsMatch   = computed(() => form.value.password1.length > 0 && form.value.password1 === form.value.password2)

const onPasswordBlur  = () => setTimeout(() => { showPasswordReq.value  = false }, 200)
const onPassword2Blur = () => setTimeout(() => { showPassword2Req.value = false }, 200)

const validatePasswords = () => {
  const p1 = form.value.password1
  const p2 = form.value.password2
  if (p1 && p2 && p1 !== p2) {
    passwordError.value = 'Passwords do not match.'
  } else {
    passwordError.value = ''
  }
  return (
    p1.length >= 8 &&
    /[A-Z]/.test(p1) &&
    /[a-z]/.test(p1) &&
    /[0-9]/.test(p1) &&
    /[!@#$%^&*_=+\-.]/.test(p1) &&
    !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(p1)
  )
}
const emailError = ref('')
const billingEmailError = ref('')
const phoneError = ref('')
const cellPhoneError = ref('')
const orgPhoneError = ref('')
const logoError = ref('')
const logoFile = ref(null)
const logoPreview = ref('')

const cleanPhone = (value) => {
  if (!value) return ''
  return value.replace(/\D/g, '')
}

const formatPhone = (field) => {
  form.value[field] = formatPhoneValue(form.value[field])
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
})

const handleLogoChange = (event) => {
  const file = event.target.files[0]
  logoError.value = ''
  logoFile.value = null
  logoPreview.value = ''

  if (!file) return

  const ext = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(ext)) {
    logoError.value = 'Logo must be a PNG or JPG file.'
    event.target.value = ''
    return
  }
  if (file.type !== 'image/png' && file.type !== 'image/jpeg') {
    logoError.value = 'Logo must be a PNG or JPG file.'
    event.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    logoError.value = 'Logo file size must be under 5MB.'
    event.target.value = ''
    return
  }

  logoFile.value = file
  if (logoPreview.value?.startsWith('blob:')) URL.revokeObjectURL(logoPreview.value)
  logoPreview.value = URL.createObjectURL(file)
}

onUnmounted(() => {
  if (logoPreview.value?.startsWith('blob:')) URL.revokeObjectURL(logoPreview.value)
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

const phoneErrorMap = { phone: phoneError, cell_phone: cellPhoneError, org_phone: orgPhoneError }

const validatePhoneField = (field) => {
  const errorRef = phoneErrorMap[field]
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
  validatePhoneField('phone')
  validatePhoneField('cell_phone')
  validatePhoneField('org_phone')

  const passwordsValid = validatePasswords()

  if (emailError.value || billingEmailError.value || phoneError.value || cellPhoneError.value || orgPhoneError.value) {
    errorMessage.value = 'Please fix the validation errors above.'
    return
  }

  if (passwordError.value || !passwordsValid) {
    showPasswordReq.value = true
    return
  }

  if (logoError.value) {
    errorMessage.value = 'Please fix the validation errors above.'
    return
  }

  saving.value = true
  try {
    const payload = new FormData()
    for (const [key, value] of Object.entries(form.value)) {
      if (value !== null && value !== undefined) {
        payload.append(key, value)
      }
    }
    if (logoFile.value) {
      payload.append('org_logo', logoFile.value)
    }
    await api.post('/api/recruiters/register/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
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
