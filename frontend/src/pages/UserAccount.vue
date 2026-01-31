<template>
  <div>
  <!-- Page Header -->
  <div class="page-header">
    <div class="page-header-content">
      <h1 class="page-title">Account Settings</h1>
      <p class="page-subtitle">Manage your contact information and account preferences</p>
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
      <div class="alert alert-danger" style="border-left: 4px solid #ef4444;">
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
            <div class="col-md-6">
              <label for="email" class="form-label">Primary Email</label>
              <input type="email" class="form-control" id="email" :value="accountData.email" disabled />
              <small class="form-text">Primary email cannot be changed</small>
            </div>
            <div class="col-md-6">
              <label for="alt_email" class="form-label">Alternate Email</label>
              <input 
                type="email" 
                class="form-control" 
                id="alt_email" 
                v-model.trim="accountData.alt_email"
                :disabled="accountSaving" 
                placeholder="Enter alternative email (optional)"
                maxlength="254"
                @blur="validateAltEmail"
                :class="{'is-invalid': emailValidationError}"
              />
              <small class="form-text">Used for notifications and recovery</small>
              <div v-if="emailValidationError" class="text-danger mt-2">
                <i class="bi bi-exclamation-circle me-1"></i>{{ emailValidationError }}
              </div>
              <div v-if="accountErrors.alt_email" class="text-danger mt-2">
                <i class="bi bi-exclamation-circle me-1"></i>{{ accountErrors.alt_email[0] }}
              </div>
            </div>
          </div>

          <div v-if="accountError" class="alert alert-danger mt-4" style="border-left: 4px solid #ef4444;">
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

          <div v-if="phoneError" class="alert alert-danger mb-3" style="border-left: 4px solid #ef4444;">
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
                      class="form-control form-control-sm"
                      :placeholder="phone.country_code === '+1' ? '(555) 123-4567' : 'Enter phone number'"
                      :maxlength="phone.country_code === '+1' ? 14 : 20"
                      required 
                      :class="{'is-invalid': phone.validationError}"
                    />
                    <div v-if="phone.validationError" class="text-danger small mt-1">
                      {{ phone.validationError }}
                    </div>
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

          <div class="d-flex justify-content-between mt-4">
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

          <div v-if="addressError" class="alert alert-danger mb-3" style="border-left: 4px solid #ef4444;">
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

          <div class="d-flex justify-content-between mt-4">
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

<script>
import api from '../api'
import { isValidEmail, validatePhone, isValidAddressField } from '../utils/validation'

export default {
  name: 'UserAccount',
  data() {
    return {
      loading: true,
      error: null,
      
      // Account data
      accountData: {
        email: '',
        alt_email: ''
      },
      accountErrors: {},
      accountError: null,
      accountSuccess: null,
      accountSaving: false,
      emailValidationError: null,
      
      // Phone numbers
      phoneNumbers: [],
      originalPhoneNumbers: [],
      primaryPhoneIndex: 0,
      showAddPhoneRow: false,
      phoneError: null,
      phoneSuccess: null,
      phoneSaving: false,
      
      countryCodes: [
        { code: '+1', name: 'United States/Canada', flag: '🇺🇸' },
        { code: '+44', name: 'United Kingdom', flag: '🇬🇧' },
        { code: '+61', name: 'Australia', flag: '🇦🇺' },
        { code: '+49', name: 'Germany', flag: '🇩🇪' },
        { code: '+33', name: 'France', flag: '🇫🇷' },
        { code: '+86', name: 'China', flag: '🇨🇳' },
        { code: '+81', name: 'Japan', flag: '🇯🇵' },
        { code: '+82', name: 'South Korea', flag: '🇰🇷' },
        { code: '+91', name: 'India', flag: '🇮🇳' },
        { code: '+55', name: 'Brazil', flag: '🇧🇷' },
      ],
      
      // Addresses
      addresses: [],
      originalAddresses: [],
      primaryAddressIndex: 0,
      showAddAddressRow: false,
      addressError: null,
      addressSuccess: null,
      addressSaving: false,
      groupedStates: {}
    }
  },
  
  computed: {
    isPhoneFormValid() {
      if (this.phoneNumbers.length === 0) return false
      
      return this.phoneNumbers.every(phone => {
        if (!phone.phone_type || !phone.country_code || !phone.phone_number) return false
        if (phone.validationError) return false
        
        const cleanNumber = this.getCleanPhoneNumber(phone.phone_number)
        if (phone.country_code === '+1') {
          return cleanNumber.length === 10
        }
        return cleanNumber.length >= 6 && cleanNumber.length <= 15
      })
    },
    
    isAddressFormValid() {
      if (this.addresses.length === 0) return false
      
      return this.addresses.every(address => {
        if (!address.add_type || !address.add_line1 || !address.add_city || !address.add_country) {
          return false
        }
        
        // Validate field lengths
        if (address.add_line1.length > 255 || address.add_line2.length > 255) return false
        if (address.add_city.length > 100 || address.add_zip.length > 20) return false
        
        // US addresses require state
        if (address.add_country === 'United States' && !address.add_state) {
          return false
        }
        
        return true
      })
    }
  },
  
  watch: {
    primaryAddressIndex(newIndex) {
      // When user selects a different primary address, update the is_primary flags
      this.addresses.forEach((address, index) => {
        address.is_primary = index === newIndex
      })
    }
  },
  
  async mounted() {
    await this.fetchAccountData()
    await this.fetchPhoneNumbers()
    await this.fetchAddresses()
    await this.fetchStates()
    this.loading = false
  },
  
  methods: {
    isValidEmail,
    
    validateAltEmail() {
      this.emailValidationError = null
      if (this.accountData.alt_email && !this.isValidEmail(this.accountData.alt_email)) {
        this.emailValidationError = 'Please enter a valid email address'
      }
    },
    
    // Validate phone number using libphonenumber-js
    validatePhoneNumber(phone) {
      const result = validatePhone(phone.phone_number, phone.country_code)
      phone.validationError = result.error
      return result.valid
    },
    
    handlePhoneInput(phone, index) {
      this.formatPhoneNumber(phone, index)
      this.validatePhoneNumber(phone)
    },
    
    handleCountryChange(address) {
      // Clear state when switching to non-US/Canada/Australia countries
      if (!['United States', 'Canada', 'Australia'].includes(address.add_country)) {
        address.add_state = ''
      }
    },
    
    async fetchAccountData() {
      try {
        const response = await api.get('/api/accounts/user-account')
        this.accountData = {
          email: response.data.email || '',
          alt_email: response.data.alt_email || ''
        }
      } catch (error) {
        console.error('Error fetching account data:', error)
        this.error = 'Failed to load account information'
      }
    },
    
    async saveAccountInfo() {
      // Validate before sending
      if (this.accountData.alt_email && !this.isValidEmail(this.accountData.alt_email)) {
        this.accountError = 'Please enter a valid alternate email address'
        return
      }
      
      this.accountSaving = true
      this.accountError = null
      this.accountSuccess = null
      this.accountErrors = {}
      
      try {
        // Sanitize and trim data
        const payload = {
          alt_email: this.accountData.alt_email?.trim().substring(0, 100) || ''
        }
        
        await api.put('/api/accounts/user-account', payload)
        this.accountSuccess = 'Account information updated successfully!'
        
        setTimeout(() => {
          this.accountSuccess = null
        }, 3000)
      } catch (error) {
        console.error('Error saving account info:', error)
        this.accountErrors = error.response?.data || {}
        this.accountError = error.response?.data?.detail || 'Failed to save account information'
      } finally {
        this.accountSaving = false
      }
    },
    
    async fetchPhoneNumbers() {
      try {
        const response = await api.get('/api/accounts/phone-numbers/')
        
        this.phoneNumbers = response.data.map(phone => ({
          id: phone.id,
          phone_type: phone.phone_type,
          country_code: phone.country_code || '+1',
          phone_number: phone.formatted_number || phone.phone_number,
          is_primary: phone.is_primary,
          validationError: null
        }))
        
        const primaryIndex = this.phoneNumbers.findIndex(phone => phone.is_primary)
        this.primaryPhoneIndex = primaryIndex >= 0 ? primaryIndex : 0
        
        if (this.phoneNumbers.length > 0 && primaryIndex < 0) {
          this.phoneNumbers[0].is_primary = true
        }
        
        this.originalPhoneNumbers = JSON.parse(JSON.stringify(this.phoneNumbers))
      } catch (error) {
        console.error('Error fetching phone numbers:', error)
      }
    },
    
    getCleanPhoneNumber(phoneNumber) {
      if (!phoneNumber) return ''
      return phoneNumber.replace(/\D/g, '')
    },
    
    formatPhoneNumber(phone, index) {
      if (!phone.phone_number) return
      
      const cleaned = this.getCleanPhoneNumber(phone.phone_number)
      
      if (phone.country_code === '+1' && cleaned.length === 10) {
        phone.phone_number = `(${cleaned.substr(0, 3)}) ${cleaned.substr(3, 3)}-${cleaned.substr(6, 4)}`
      } else {
        phone.phone_number = cleaned
      }
      
      this.validatePhoneNumber(phone)
    },
    
    addNewPhone() {
      if (this.showAddPhoneRow || this.phoneNumbers.length >= 3) return
      
      this.phoneNumbers.push({
        id: null,
        phone_type: '',
        country_code: '+1',
        phone_number: '',
        is_primary: this.phoneNumbers.length === 0,
        validationError: null
      })
      
      if (this.phoneNumbers.length === 1) {
        this.primaryPhoneIndex = 0
      }
      
      this.showAddPhoneRow = true
      this.phoneError = null
    },
    
    async removePhone(index) {
      const removedPhone = this.phoneNumbers[index]
      
      if (removedPhone.id) {
        if (confirm('Are you sure you want to delete this phone number?')) {
          await this.deletePhone(removedPhone.id, index)
        }
      } else {
        this.phoneNumbers.splice(index, 1)
        this.showAddPhoneRow = false
        
        if (this.primaryPhoneIndex === index && this.phoneNumbers.length > 0) {
          this.primaryPhoneIndex = 0
          this.phoneNumbers[0].is_primary = true
        } else if (this.primaryPhoneIndex > index) {
          this.primaryPhoneIndex--
        }
      }
    },
    
    async deletePhone(phoneId, index) {
      this.phoneSaving = true
      this.phoneError = null
      
      try {
        await api.delete(`/api/accounts/phone-numbers/${phoneId}/`)
        
        this.phoneNumbers.splice(index, 1)
        
        if (this.primaryPhoneIndex === index && this.phoneNumbers.length > 0) {
          this.primaryPhoneIndex = 0
        } else if (this.primaryPhoneIndex > index) {
          this.primaryPhoneIndex--
        }
        
        this.phoneSuccess = 'Phone number deleted successfully!'
        setTimeout(() => {
          this.phoneSuccess = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting phone:', error)
        this.phoneError = error.response?.data?.detail || 'Failed to delete phone number'
      } finally {
        this.phoneSaving = false
      }
    },
    
    resetPhoneChanges() {
      this.phoneNumbers = JSON.parse(JSON.stringify(this.originalPhoneNumbers))
      const primaryIndex = this.phoneNumbers.findIndex(phone => phone.is_primary)
      this.primaryPhoneIndex = primaryIndex >= 0 ? primaryIndex : 0
      this.showAddPhoneRow = false
      this.phoneError = null
    },
    
    async saveAllPhones() {
      // Validate all phones before saving
      let hasErrors = false
      this.phoneNumbers.forEach(phone => {
        if (!this.validatePhoneNumber(phone)) {
          hasErrors = true
        }
      })
      
      if (hasErrors) {
        this.phoneError = 'Please fix validation errors before saving'
        return
      }
      
      this.phoneSaving = true
      this.phoneError = null
      this.phoneSuccess = null
      
      try {
        // Mark which phone should be primary
        this.phoneNumbers.forEach((phone, index) => {
          phone.is_primary = index === this.primaryPhoneIndex
        })
        
        // Save each phone
        for (let i = 0; i < this.phoneNumbers.length; i++) {
          const phone = this.phoneNumbers[i]
          
          // Sanitize and validate data
          const cleanNumber = this.getCleanPhoneNumber(phone.phone_number)
          if (!cleanNumber || cleanNumber.length > 20) {
            throw new Error('Invalid phone number')
          }
          
          const payload = {
            phone_type: phone.phone_type,
            country_code: phone.country_code || '+1',
            phone_number: cleanNumber,
            is_primary: phone.is_primary
          }
          
          if (phone.id) {
            await api.put(`/api/accounts/phone-numbers/${phone.id}/`, payload)
          } else {
            const response = await api.post('/api/accounts/phone-numbers/', payload)
            phone.id = response.data.id
          }
        }
        
        // Success - refresh and show message
        await this.fetchPhoneNumbers()
        this.showAddPhoneRow = false
        this.phoneSuccess = 'Phone numbers updated successfully!'
        setTimeout(() => {
          this.phoneSuccess = null
        }, 3000)
        
      } catch (error) {
        console.error('Error saving phones:', error)
        const errorData = error.response?.data
        
        // Extract error message from Django serializer
        if (errorData) {
          if (errorData.phone_type) {
            this.phoneError = Array.isArray(errorData.phone_type) ? errorData.phone_type[0] : errorData.phone_type
          } else if (errorData.is_primary) {
            this.phoneError = Array.isArray(errorData.is_primary) ? errorData.is_primary[0] : errorData.is_primary
          } else if (errorData.phone_number) {
            this.phoneError = Array.isArray(errorData.phone_number) ? errorData.phone_number[0] : errorData.phone_number
          } else if (errorData.country_code) {
            this.phoneError = Array.isArray(errorData.country_code) ? errorData.country_code[0] : errorData.country_code
          } else if (errorData.non_field_errors) {
            this.phoneError = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors
          } else if (errorData.detail) {
            this.phoneError = errorData.detail
          } else if (typeof errorData === 'string') {
            this.phoneError = errorData
          } else {
            this.phoneError = 'Failed to save phone numbers'
          }
        } else {
          this.phoneError = 'Failed to save phone numbers'
        }
      } finally {
        this.phoneSaving = false
      }
    },
    
    async fetchAddresses() {
      try {
        const response = await api.get('/api/accounts/addresses/')
        
        this.addresses = response.data.map(address => ({
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
        
        // Set primaryAddressIndex based on is_primary
        const primaryIndex = this.addresses.findIndex(address => address.is_primary)
        this.primaryAddressIndex = primaryIndex >= 0 ? primaryIndex : 0
        
        // If no primary address is set and we have addresses, mark the first as primary
        if (this.addresses.length > 0 && primaryIndex < 0) {
          this.addresses[0].is_primary = true
          this.primaryAddressIndex = 0
        }
        
        this.originalAddresses = JSON.parse(JSON.stringify(this.addresses))
        
        // Force Vue to update the UI after addresses change
        await this.$nextTick()
      } catch (error) {
        console.error('Error fetching addresses:', error)
      }
    },
    
    async fetchStates() {
      try {
        const response = await api.get('/api/accounts/states-provinces')
        this.groupedStates = response.data
        console.log('States loaded:', this.groupedStates)
      } catch (error) {
        console.error('Error fetching states:', error)
      }
    },
    
    addNewAddress() {
      if (this.showAddAddressRow || this.addresses.length >= 3) return
      
      this.addresses.push({
        id: null,
        add_type: '',
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: 'United States',
        is_primary: this.addresses.length === 0
      })
      
      this.showAddAddressRow = true
      this.addressError = null
    },
    
    removeAddress(index) {
      const removedAddress = this.addresses[index]
      
      if (removedAddress.id) {
        if (confirm('Are you sure you want to delete this address?')) {
          this.deleteAddress(removedAddress.id, index)
        }
      } else {
        this.addresses.splice(index, 1)
        this.showAddAddressRow = false
        
        // Adjust primaryAddressIndex if needed
        if (this.primaryAddressIndex === index) {
          this.primaryAddressIndex = 0
        } else if (this.primaryAddressIndex > index) {
          this.primaryAddressIndex--
        }
      }
    },
    
    async deleteAddress(addressId, index) {
      this.addressSaving = true
      this.addressError = null
      
      try {
        await api.delete(`/api/accounts/addresses/${addressId}/`)
        
        // Refresh addresses to ensure primary state is correct
        await this.fetchAddresses()
        
        this.addressSuccess = 'Address deleted successfully!'
        setTimeout(() => {
          this.addressSuccess = null
        }, 3000)
      } catch (error) {
        console.error('Error deleting address:', error)
        this.addressError = error.response?.data?.detail || 'Failed to delete address'
      } finally {
        this.addressSaving = false
      }
    },
    
    resetAddressChanges() {
      this.addresses = JSON.parse(JSON.stringify(this.originalAddresses))
      this.showAddAddressRow = false
      this.addressError = null
    },
    
    async saveAllAddresses() {
      this.addressSaving = true
      this.addressError = null
      this.addressSuccess = null
      
      try {
        // First, save all addresses
        const savedAddresses = []
        for (const address of this.addresses) {
          // Sanitize and validate data
          const add_line1 = address.add_line1?.trim().substring(0, 255)
          const add_line2 = address.add_line2?.trim().substring(0, 255)
          const add_city = address.add_city?.trim().substring(0, 100)
          const add_zip = address.add_zip?.trim().substring(0, 20)
          
          if (!add_line1 || !add_city) {
            throw new Error('Address line 1 and city are required')
          }

          if (!isValidAddressField(add_line1) || !isValidAddressField(add_line2) || !isValidAddressField(add_city)) {
            throw new Error('Address fields contain invalid characters')
          }
          
          const stateValue = ['United States', 'Canada', 'Australia'].includes(address.add_country)
            ? address.add_state
            : null
          
          const payload = {
            add_type: address.add_type,
            add_line1: add_line1,
            add_line2: add_line2 || '',
            add_city: add_city,
            add_state: stateValue,
            add_zip: add_zip || '',
            add_country: address.add_country
          }
          
          let response
          if (address.id) {
            response = await api.put(`/api/accounts/addresses/${address.id}/`, payload)
          } else {
            response = await api.post('/api/accounts/addresses/', payload)
            address.id = response.data.id
          }
          savedAddresses.push(response.data)
        }
        
        // Then set the primary address using the set_primary endpoint
        const primaryAddress = this.addresses[this.primaryAddressIndex]
        
        if (primaryAddress && primaryAddress.id) {
          await api.post(`/api/accounts/addresses/${primaryAddress.id}/set_primary/`)
        }
        
        await this.fetchAddresses()
        this.showAddAddressRow = false
        this.addressSuccess = 'Addresses updated successfully!'
        setTimeout(() => {
          this.addressSuccess = null
        }, 3000)
      } catch (error) {
        console.error('Error saving addresses:', error)
        const errorData = error.response?.data
        
        if (errorData?.add_type) {
          this.addressError = errorData.add_type[0]
        } else if (errorData?.add_state) {
          this.addressError = errorData.add_state[0] || errorData.add_state
        } else {
          this.addressError = errorData?.detail || error.message || 'Failed to save addresses'
        }
      } finally {
        this.addressSaving = false
      }
    }
  }
}
</script>
