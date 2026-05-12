<template>
  <div>
  <!-- Page Header -->
  <div class="page-header">
    <div class="page-header-content">
      <div v-if="isAdminMode" class="mb-2">
        <router-link to="/user-management" class="btn btn-sm btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>Back to User Management
        </router-link>
      </div>
      <h1 class="page-title">{{ pageTitle }}</h1>
      <p class="page-subtitle">{{ pageSubtitle }}</p>
    </div>
  </div>

  <!-- Main Content -->
  <div class="content-container">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading account information...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="section-card">
      <div class="alert alert-danger" role="alert" style="border-left: 4px solid #ef4444;">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>
    </div>

    <!-- Main Content -->
    <div v-else>
      <!-- Account Information Section -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-envelope"></i>
            </div>
            Account Information
          </h2>
        </div>

        <form @submit.prevent="saveAccountInfo">
          <div class="row g-4">
            <div class="col-12" v-if="accountData.first_name || accountData.last_name">
              <p class="mb-0 fw-semibold fs-5">{{ accountData.first_name }} {{ accountData.last_name }}</p>
            </div>
            <div class="col-md-6">
              <label for="email" class="form-label">Primary Email</label>
              <input type="email" class="form-control" id="email" :value="accountData.email" disabled />
              <small class="form-text">Primary email cannot be changed. Please contact <a href="mailto:tbp.it@tbp.org">tbp.it@tbp.org</a> with any concerns.</small>
            </div>
            <div class="col-md-6">
              <label for="alt_email" class="form-label">Alternate Email</label>
              <input
                type="email"
                :class="['form-control', { 'is-invalid': emailValidationError || accountErrors.alt_email }]"
                id="alt_email"
                v-model.trim="accountData.alt_email"
                :disabled="accountSaving"
                placeholder="Enter alternative email (optional)"
                maxlength="254"
                @blur="validateAltEmail"
              />
              <div class="invalid-feedback">
                <i class="bi bi-exclamation-circle me-1"></i>{{ emailValidationError || (accountErrors.alt_email && accountErrors.alt_email[0]) }}
              </div>
              <small class="form-text">Used for recovery and optionally for notifications</small>
            </div>
          </div>

          <div v-if="accountError" class="alert alert-danger mt-4" role="alert" style="border-left: 4px solid #ef4444;">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ accountError }}
          </div>

          <div v-if="accountSuccess" class="alert-success-custom mt-4">
            <i class="bi bi-check-circle-fill me-2"></i>{{ accountSuccess }}
          </div>

          <button type="submit" class="btn btn-primary mt-4" :disabled="accountSaving || emailValidationError">
            <span v-if="accountSaving">
              <span class="spinner-border spinner-border-sm me-2"></span>Saving...
            </span>
            <span v-else>
              <i class="bi bi-check2 me-2"></i>Save Account Info
            </span>
          </button>
        </form>
      </div>

      <!-- Change Password Section -->
      <ChangePasswordSection />

      <!-- Phone Numbers Section -->
      <div class="section-card" id="phone-numbers">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon gold">
              <i class="bi bi-telephone"></i>
            </div>
            Phone Numbers
          </h2>
          <button class="btn btn-gold btn-sm" @click="addNewPhone" :disabled="showAddPhoneRow || phoneNumbers.length >= 3">
            <i class="bi bi-plus-lg me-1"></i>Add Phone Number
          </button>
        </div>

        <div v-if="phoneNumbers.length === 0 && !showAddPhoneRow" class="empty-state">
          <i class="bi bi-telephone"></i>
          <p>No phone numbers added yet. Click "Add Phone Number" to get started.</p>
        </div>

        <form @submit.prevent="saveAllPhones" v-else>
          <div v-if="phoneSuccess" class="alert-success-custom mb-3">
            <i class="bi bi-check-circle-fill me-2"></i>{{ phoneSuccess }}
          </div>

          <div v-if="phoneError" class="alert alert-danger mb-3" role="alert" style="border-left: 4px solid #ef4444;">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ phoneError }}
          </div>

          <div class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Country</th>
                  <th>Phone Number</th>
                  <th>Primary</th>
                  <th style="width: 120px;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(phone, index) in phoneNumbers" :key="phone.id || `new-${index}`">
                  <td style="min-width: 120px;">
                    <select v-model="phone.phone_type" class="form-select form-select-sm" required>
                      <option value="">Select type...</option>
                      <option value="Mobile">Mobile</option>
                      <option value="Home">Home</option>
                      <option value="Work">Work</option>
                    </select>
                  </td>
                  <td style="min-width: 200px;">
                    <select 
                      v-model="phone.country_code" 
                      class="form-select form-select-sm" 
                      required
                      @change="formatPhoneNumber(phone, index)"
                    >
                      <option v-for="country in countryCodes" :key="country.code" :value="country.code">
                        {{ country.flag }} {{ country.code }} - {{ country.name }}
                      </option>
                    </select>
                  </td>
                  <td style="min-width: 200px;">
                    <input
                      v-model="phone.phone_number"
                      @input="handlePhoneInput(phone, index)"
                      type="tel"
                      :class="['form-control', 'form-control-sm', { 'is-invalid': phone.validationError }]"
                      :placeholder="phone.country_code === '+1' ? '(555) 123-4567' : 'Enter phone number'"
                      :maxlength="phone.country_code === '+1' ? 14 : 20"
                      required
                    />
                    <div class="invalid-feedback">{{ phone.validationError }}</div>
                  </td>
                  <td class="text-center">
                    <div class="form-check d-inline-block">
                      <input 
                        :value="index" 
                        v-model="primaryPhoneIndex" 
                        class="form-check-input" 
                        type="radio"
                        :id="`primary-${index}`" 
                        name="primaryPhone"
                        style="width: 1.25rem; height: 1.25rem; cursor: pointer;"
                      />
                      <label class="form-check-label ms-2" :for="`primary-${index}`">
                        <span v-if="primaryPhoneIndex === index" class="badge" style="background: #10b981; color: white;">Primary</span>
                      </label>
                    </div>
                  </td>
                  <td>
                    <button 
                      type="button" 
                      class="btn btn-sm" 
                      style="border: 1.5px solid #e2e8f0; color: #ef4444; border-radius: 8px;"
                      @click="removePhone(index)"
                      :disabled="phoneSaving || phoneNumbers.length === 1"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="d-grid gap-2 d-sm-flex justify-content-sm-between mt-4">
            <button type="button" class="btn btn-secondary" @click="resetPhoneChanges" :disabled="phoneSaving">
              <i class="bi bi-arrow-counterclockwise me-2"></i>Reset Changes
            </button>
            <button type="submit" class="btn btn-primary" :disabled="phoneSaving || !isPhoneFormValid">
              <span v-if="phoneSaving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else>
                <i class="bi bi-check2 me-2"></i>Save Phone Numbers
              </span>
            </button>
          </div>
        </form>
      </div>

      <!-- Addresses Section -->
      <div class="section-card" id="addresses">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-geo-alt"></i>
            </div>
            Addresses
          </h2>
          <button class="btn btn-gold btn-sm" @click="addNewAddress" :disabled="showAddAddressRow || addresses.length >= 3">
            <i class="bi bi-plus-lg me-1"></i>Add Address
          </button>
        </div>

        <div v-if="addresses.length === 0 && !showAddAddressRow" class="empty-state">
          <i class="bi bi-geo-alt"></i>
          <p>No addresses added yet. Click "Add Address" to get started.</p>
        </div>

        <form @submit.prevent="saveAllAddresses" v-else>
          <div v-if="addressSuccess" class="alert-success-custom mb-3">
            <i class="bi bi-check-circle-fill me-2"></i>{{ addressSuccess }}
          </div>

          <div v-if="addressError" class="alert alert-danger mb-3" role="alert" style="border-left: 4px solid #ef4444;">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ addressError }}
          </div>

          <div class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th style="width: 12%;">Type</th>
                  <th style="width: 28%;">Address</th>
                  <th style="width: 15%;">City</th>
                  <th style="width: 12%;">State/Province</th>
                  <th style="width: 10%;">Zip/Postal</th>
                  <th style="width: 13%;">Country</th>
                  <th style="width: 8%;">Primary</th>
                  <th style="width: 10%;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(address, index) in addresses" :key="address.id || `new-${index}`">
                  <td>
                    <select v-model="address.add_type" class="form-select form-select-sm" required>
                      <option value="">Select...</option>
                      <option value="Home">Home</option>
                      <option value="Work">Work</option>
                      <option value="School">School</option>
                    </select>
                  </td>
                  <td>
                    <input 
                      v-model.trim="address.add_line1" 
                      type="text" 
                      class="form-control form-control-sm mb-1" 
                      placeholder="Address Line 1" 
                      required
                      maxlength="255"
                    />
                    <input 
                      v-model.trim="address.add_line2" 
                      type="text" 
                      class="form-control form-control-sm" 
                      placeholder="Address Line 2 (optional)"
                      maxlength="255"
                    />
                  </td>
                  <td>
                    <input 
                      v-model.trim="address.add_city" 
                      type="text" 
                      class="form-control form-control-sm" 
                      placeholder="City" 
                      required
                      maxlength="100"
                    />
                  </td>
                  <td>
                    <select 
                      v-if="['United States', 'Canada', 'Australia'].includes(address.add_country)"
                      v-model="address.add_state" 
                      class="form-select form-select-sm"
                      :required="address.add_country === 'United States'"
                    >
                      <option value="">Select...</option>
                      <optgroup 
                        v-for="(states, country) in groupedStates" 
                        :key="country" 
                        :label="country"
                        v-show="country === address.add_country"
                      >
                        <option 
                          v-for="state in states" 
                          :key="state.id" 
                          :value="state.abbrev"
                        >
                          {{ state.name }}
                        </option>
                      </optgroup>
                    </select>
                    <input 
                      v-else
                      v-model.trim="address.add_state" 
                      type="text" 
                      class="form-control form-control-sm" 
                      placeholder="Province/Region"
                      maxlength="100"
                    />
                  </td>
                  <td>
                    <input 
                      v-model.trim="address.add_zip" 
                      type="text" 
                      class="form-control form-control-sm" 
                      placeholder="Postal Code"
                      maxlength="20"
                    />
                  </td>
                  <td>
                    <select 
                      v-model="address.add_country" 
                      class="form-select form-select-sm"
                      required
                      @change="handleCountryChange(address)"
                    >
                      <option value="United States">United States</option>
                      <option value="Canada">Canada</option>
                      <option value="Australia">Australia</option>
                      <option value="Other">Other</option>
                    </select>
                  </td>
                  <td class="text-center">
                    <div class="form-check d-inline-block">
                      <input 
                        :checked="index === primaryAddressIndex"
                        @change="primaryAddressIndex = index"
                        class="form-check-input" 
                        type="radio"
                        :id="`primary-address-${index}`" 
                        name="primaryAddress"
                        style="width: 1.25rem; height: 1.25rem; cursor: pointer;"
                      />
                      <label class="form-check-label ms-2" :for="`primary-address-${index}`">
                        <span v-if="primaryAddressIndex === index" class="badge" style="background: #10b981; color: white;">Primary</span>
                      </label>
                    </div>
                  </td>
                  <td>
                    <button 
                      type="button" 
                      class="btn btn-sm" 
                      style="border: 1.5px solid #e2e8f0; color: #ef4444; border-radius: 8px;"
                      @click="removeAddress(index)"
                      :disabled="addressSaving"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="d-grid gap-2 d-sm-flex justify-content-sm-between mt-4">
            <button type="button" class="btn btn-secondary" @click="resetAddressChanges" :disabled="addressSaving">
              <i class="bi bi-arrow-counterclockwise me-2"></i>Reset Changes
            </button>
            <button type="submit" class="btn btn-primary" :disabled="addressSaving || !isAddressFormValid">
              <span v-if="addressSaving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else>
                <i class="bi bi-check2 me-2"></i>Save Addresses
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import { isValidEmail, validatePhone, isValidAddressField } from '../utils/validation'
import ChangePasswordSection from '../components/ChangePasswordSection.vue'

const route = useRoute()

// State
const loading = ref(true)
const error = ref(null)

const accountData = ref({ email: '', alt_email: '', first_name: '', last_name: '' })
const accountErrors = ref({})
const accountError = ref(null)
const accountSuccess = ref(null)
const accountSaving = ref(false)
const emailValidationError = ref(null)

const phoneNumbers = ref([])
const originalPhoneNumbers = ref([])
const primaryPhoneIndex = ref(0)
const showAddPhoneRow = ref(false)
const phoneError = ref(null)
const phoneSuccess = ref(null)
const phoneSaving = ref(false)

const countryCodes = [
  { code: '+1',  name: 'United States/Canada', flag: '🇺🇸' },
  { code: '+44', name: 'United Kingdom',        flag: '🇬🇧' },
  { code: '+61', name: 'Australia',             flag: '🇦🇺' },
  { code: '+49', name: 'Germany',               flag: '🇩🇪' },
  { code: '+33', name: 'France',                flag: '🇫🇷' },
  { code: '+86', name: 'China',                 flag: '🇨🇳' },
  { code: '+81', name: 'Japan',                 flag: '🇯🇵' },
  { code: '+82', name: 'South Korea',           flag: '🇰🇷' },
  { code: '+91', name: 'India',                 flag: '🇮🇳' },
  { code: '+55', name: 'Brazil',                flag: '🇧🇷' },
]

const addresses = ref([])
const originalAddresses = ref([])
const primaryAddressIndex = ref(0)
const showAddAddressRow = ref(false)
const addressError = ref(null)
const addressSuccess = ref(null)
const addressSaving = ref(false)
const groupedStates = ref({})

// Computed
const adminUserId = computed(() => {
  const id = route.params.userId
  return id ? parseInt(id) : null
})
const isAdminMode = computed(() => !!adminUserId.value)
const apiBase = computed(() =>
  isAdminMode.value ? `/api/accounts/admin/users/${adminUserId.value}` : '/api/accounts'
)
const pageTitle = computed(() => {
  if (isAdminMode.value && accountData.value.first_name) {
    return `${accountData.value.first_name} ${accountData.value.last_name}`
  }
  return 'Account Settings'
})
const pageSubtitle = computed(() =>
  isAdminMode.value
    ? 'Viewing and editing on behalf of this user'
    : 'Manage your contact information and account settings'
)
const isPhoneFormValid = computed(() => {
  if (phoneNumbers.value.length === 0) return false
  return phoneNumbers.value.every(phone => {
    if (!phone.phone_type || !phone.country_code || !phone.phone_number) return false
    if (phone.validationError) return false
    const clean = getCleanPhoneNumber(phone.phone_number)
    return phone.country_code === '+1' ? clean.length === 10 : clean.length >= 6 && clean.length <= 15
  })
})
const isAddressFormValid = computed(() => {
  if (addresses.value.length === 0) return false
  return addresses.value.every(address => {
    if (!address.add_type || !address.add_line1 || !address.add_city || !address.add_country) return false
    if ((address.add_line1?.length ?? 0) > 255 || (address.add_line2?.length ?? 0) > 255) return false
    if (address.add_city.length > 100 || address.add_zip.length > 20) return false
    if (address.add_country === 'United States' && !address.add_state) return false
    return true
  })
})

// Watcher
watch(primaryAddressIndex, newIndex => {
  addresses.value.forEach((address, index) => { address.is_primary = index === newIndex })
})

// Lifecycle
onMounted(async () => {
  await fetchAccountData()
  await fetchPhoneNumbers()
  await fetchAddresses()
  await fetchStates()
  loading.value = false
})

// Account
function validateAltEmail() {
  emailValidationError.value = accountData.value.alt_email && !isValidEmail(accountData.value.alt_email)
    ? 'Please enter a valid email address'
    : null
}

async function fetchAccountData() {
  try {
    const response = await api.get(`${apiBase.value}/user-account`)
    accountData.value = {
      email:      response.data.email      || '',
      alt_email:  response.data.alt_email  || '',
      first_name: response.data.first_name || '',
      last_name:  response.data.last_name  || '',
    }
  } catch {
    error.value = 'Failed to load account information'
  }
}

async function saveAccountInfo() {
  if (accountData.value.alt_email && !isValidEmail(accountData.value.alt_email)) {
    accountError.value = 'Please enter a valid alternate email address'
    return
  }
  accountSaving.value = true
  accountError.value = null
  accountSuccess.value = null
  accountErrors.value = {}
  try {
    await api.put(`${apiBase.value}/user-account`, {
      alt_email: accountData.value.alt_email?.trim() || ''
    })
    accountSuccess.value = 'Account information updated successfully!'
    setTimeout(() => { accountSuccess.value = null }, 3000)
  } catch (err) {
    accountErrors.value = err.response?.data || {}
    accountError.value = err.response?.data?.detail || 'Failed to save account information'
  } finally {
    accountSaving.value = false
  }
}

// Phone numbers
function getCleanPhoneNumber(phoneNumber) {
  return phoneNumber ? phoneNumber.replace(/\D/g, '') : ''
}

function validatePhoneNumber(phone) {
  const result = validatePhone(phone.phone_number, phone.country_code)
  phone.validationError = result.error
  return result.valid
}

function handlePhoneInput(phone, index) {
  formatPhoneNumber(phone, index)
  validatePhoneNumber(phone)
}

function formatPhoneNumber(phone, index) {
  if (!phone.phone_number) return
  const cleaned = getCleanPhoneNumber(phone.phone_number)
  phone.phone_number = (phone.country_code === '+1' && cleaned.length === 10)
    ? `(${cleaned.substr(0, 3)}) ${cleaned.substr(3, 3)}-${cleaned.substr(6, 4)}`
    : cleaned
  validatePhoneNumber(phone)
}

async function fetchPhoneNumbers() {
  try {
    const response = await api.get(`${apiBase.value}/phone-numbers/`)
    phoneNumbers.value = response.data.map(phone => ({
      id: phone.id,
      phone_type: phone.phone_type,
      country_code: phone.country_code || '+1',
      phone_number: phone.formatted_number || phone.phone_number,
      is_primary: phone.is_primary,
      validationError: null
    }))
    const primaryIdx = phoneNumbers.value.findIndex(p => p.is_primary)
    primaryPhoneIndex.value = primaryIdx >= 0 ? primaryIdx : 0
    if (phoneNumbers.value.length > 0 && primaryIdx < 0) phoneNumbers.value[0].is_primary = true
    originalPhoneNumbers.value = JSON.parse(JSON.stringify(phoneNumbers.value))
  } catch {
    // silent — phones stay empty
  }
}

function addNewPhone() {
  if (showAddPhoneRow.value || phoneNumbers.value.length >= 3) return
  phoneNumbers.value.push({ id: null, phone_type: '', country_code: '+1', phone_number: '', is_primary: phoneNumbers.value.length === 0, validationError: null })
  if (phoneNumbers.value.length === 1) primaryPhoneIndex.value = 0
  showAddPhoneRow.value = true
  phoneError.value = null
}

async function removePhone(index) {
  const phone = phoneNumbers.value[index]
  if (phone.id) {
    if (confirm('Are you sure you want to delete this phone number?')) await deletePhone(phone.id, index)
  } else {
    phoneNumbers.value.splice(index, 1)
    showAddPhoneRow.value = false
    if (primaryPhoneIndex.value === index && phoneNumbers.value.length > 0) {
      primaryPhoneIndex.value = 0
      phoneNumbers.value[0].is_primary = true
    } else if (primaryPhoneIndex.value > index) {
      primaryPhoneIndex.value--
    }
  }
}

async function deletePhone(phoneId, index) {
  phoneSaving.value = true
  phoneError.value = null
  try {
    await api.delete(`${apiBase.value}/phone-numbers/${phoneId}/`)
    phoneNumbers.value.splice(index, 1)
    if (primaryPhoneIndex.value === index && phoneNumbers.value.length > 0) primaryPhoneIndex.value = 0
    else if (primaryPhoneIndex.value > index) primaryPhoneIndex.value--
    phoneSuccess.value = 'Phone number deleted successfully!'
    setTimeout(() => { phoneSuccess.value = null }, 3000)
  } catch (err) {
    phoneError.value = err.response?.data?.detail || 'Failed to delete phone number'
  } finally {
    phoneSaving.value = false
  }
}

function resetPhoneChanges() {
  phoneNumbers.value = JSON.parse(JSON.stringify(originalPhoneNumbers.value))
  const primaryIdx = phoneNumbers.value.findIndex(p => p.is_primary)
  primaryPhoneIndex.value = primaryIdx >= 0 ? primaryIdx : 0
  showAddPhoneRow.value = false
  phoneError.value = null
}

async function saveAllPhones() {
  let hasErrors = false
  phoneNumbers.value.forEach(phone => { if (!validatePhoneNumber(phone)) hasErrors = true })
  if (hasErrors) { phoneError.value = 'Please fix validation errors before saving'; return }

  phoneSaving.value = true
  phoneError.value = null
  phoneSuccess.value = null
  try {
    phoneNumbers.value.forEach((phone, index) => { phone.is_primary = index === primaryPhoneIndex.value })
    for (const phone of phoneNumbers.value) {
      const cleanNumber = getCleanPhoneNumber(phone.phone_number)
      if (!cleanNumber || cleanNumber.length > 20) throw new Error('Invalid phone number')
      const payload = { phone_type: phone.phone_type, country_code: phone.country_code || '+1', phone_number: cleanNumber, is_primary: phone.is_primary }
      if (phone.id) {
        await api.put(`${apiBase.value}/phone-numbers/${phone.id}/`, payload)
      } else {
        const response = await api.post(`${apiBase.value}/phone-numbers/`, payload)
        phone.id = response.data.id
      }
    }
    await fetchPhoneNumbers()
    showAddPhoneRow.value = false
    phoneSuccess.value = 'Phone numbers updated successfully!'
    setTimeout(() => { phoneSuccess.value = null }, 3000)
  } catch (err) {
    await fetchPhoneNumbers()
    const errorData = err.response?.data
    if (errorData && typeof errorData === 'object') {
      phoneError.value = Object.values(errorData).flat().join(' ') || 'Failed to save phone numbers'
    } else {
      phoneError.value = typeof errorData === 'string' ? errorData : 'Failed to save phone numbers'
    }
  } finally {
    phoneSaving.value = false
  }
}

// Addresses
function handleCountryChange(address) {
  if (!['United States', 'Canada', 'Australia'].includes(address.add_country)) address.add_state = ''
}

async function fetchAddresses() {
  try {
    const response = await api.get(`${apiBase.value}/addresses/`)
    addresses.value = response.data.map(address => ({
      id: address.id,
      add_type: address.add_type,
      add_line1: address.add_line1,
      add_line2: address.add_line2 || '',
      add_city: address.add_city,
      add_state: address.add_state || '',
      add_zip: address.add_zip,
      add_country: address.add_country || 'United States',
      is_primary: address.is_primary
    }))
    const primaryIdx = addresses.value.findIndex(a => a.is_primary)
    primaryAddressIndex.value = primaryIdx >= 0 ? primaryIdx : 0
    if (addresses.value.length > 0 && primaryIdx < 0) {
      addresses.value[0].is_primary = true
      primaryAddressIndex.value = 0
    }
    originalAddresses.value = JSON.parse(JSON.stringify(addresses.value))
    await nextTick()
  } catch {
    // silent — addresses stay empty
  }
}

async function fetchStates() {
  try {
    const response = await api.get('/api/accounts/states-provinces')
    groupedStates.value = response.data
  } catch {
    // non-critical reference data
  }
}

function addNewAddress() {
  if (showAddAddressRow.value || addresses.value.length >= 3) return
  addresses.value.push({ id: null, add_type: '', add_line1: '', add_line2: '', add_city: '', add_state: '', add_zip: '', add_country: 'United States', is_primary: addresses.value.length === 0 })
  showAddAddressRow.value = true
  addressError.value = null
}

function removeAddress(index) {
  const addr = addresses.value[index]
  if (addr.id) {
    if (confirm('Are you sure you want to delete this address?')) deleteAddress(addr.id, index)
  } else {
    addresses.value.splice(index, 1)
    showAddAddressRow.value = false
    if (primaryAddressIndex.value === index) primaryAddressIndex.value = 0
    else if (primaryAddressIndex.value > index) primaryAddressIndex.value--
  }
}

async function deleteAddress(addressId, index) {
  addressSaving.value = true
  addressError.value = null
  try {
    await api.delete(`${apiBase.value}/addresses/${addressId}/`)
    await fetchAddresses()
    addressSuccess.value = 'Address deleted successfully!'
    setTimeout(() => { addressSuccess.value = null }, 3000)
  } catch (err) {
    addressError.value = err.response?.data?.detail || 'Failed to delete address'
  } finally {
    addressSaving.value = false
  }
}

function resetAddressChanges() {
  addresses.value = JSON.parse(JSON.stringify(originalAddresses.value))
  showAddAddressRow.value = false
  addressError.value = null
}

async function saveAllAddresses() {
  addressSaving.value = true
  addressError.value = null
  addressSuccess.value = null
  try {
    for (const address of addresses.value) {
      const add_line1 = address.add_line1?.trim().substring(0, 255)
      const add_line2 = address.add_line2?.trim().substring(0, 255)
      const add_city  = address.add_city?.trim().substring(0, 100)
      const add_zip   = address.add_zip?.trim().substring(0, 20)
      if (!add_line1 || !add_city) throw new Error('Address line 1 and city are required')
      if (!isValidAddressField(add_line1) || !isValidAddressField(add_line2) || !isValidAddressField(add_city)) {
        throw new Error('Address fields contain invalid characters')
      }
      const stateValue = ['United States', 'Canada', 'Australia'].includes(address.add_country) ? address.add_state : null
      const payload = { add_type: address.add_type, add_line1, add_line2: add_line2 || '', add_city, add_state: stateValue, add_zip: add_zip || '', add_country: address.add_country }
      if (address.id) {
        await api.put(`${apiBase.value}/addresses/${address.id}/`, payload)
      } else {
        const response = await api.post(`${apiBase.value}/addresses/`, payload)
        address.id = response.data.id
      }
    }
    const primaryAddress = addresses.value[primaryAddressIndex.value]
    if (primaryAddress?.id) await api.post(`${apiBase.value}/addresses/${primaryAddress.id}/set_primary/`)
    await fetchAddresses()
    showAddAddressRow.value = false
    addressSuccess.value = 'Addresses updated successfully!'
    setTimeout(() => { addressSuccess.value = null }, 3000)
  } catch (err) {
    await fetchAddresses()
    const errorData = err.response?.data
    if (errorData?.add_type) addressError.value = errorData.add_type[0]
    else if (errorData?.add_state) addressError.value = errorData.add_state[0] || errorData.add_state
    else addressError.value = errorData?.detail || err.message || 'Failed to save addresses'
  } finally {
    addressSaving.value = false
  }
}
</script>
