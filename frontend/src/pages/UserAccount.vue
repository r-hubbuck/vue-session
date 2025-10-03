<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-12">
        <h1 class="text-center mb-4">My Account</h1>
        
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        
        <div v-else>
          <!-- Account Information Card -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">Account Information</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="saveAccountInfo">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="email" class="form-label">Primary Email</label>
                      <input
                        type="email"
                        class="form-control"
                        id="email"
                        :value="accountData.email"
                        disabled
                      />
                      <div class="form-text">Primary email cannot be changed</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="alt_email" class="form-label">Alternative Email</label>
                      <input
                        type="email"
                        class="form-control"
                        id="alt_email"
                        v-model="accountData.alt_email"
                        :disabled="accountSaving"
                        placeholder="Enter alternative email (optional)"
                      />
                      <div v-if="accountErrors.alt_email" class="text-danger mt-2">
                        {{ accountErrors.alt_email[0] }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="accountError" class="alert alert-danger">
                  {{ accountError }}
                </div>
                
                <div v-if="accountSuccess" class="alert alert-success">
                  {{ accountSuccess }}
                </div>
                
                <button type="submit" class="btn btn-primary" :disabled="accountSaving">
                  {{ accountSaving ? 'Saving...' : 'Save Account Info' }}
                </button>
              </form>
            </div>
          </div>
          
          <!-- Phone Numbers Card -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Phone Numbers</h5>
              <button class="btn btn-success btn-sm" @click="addNewPhone" :disabled="showAddPhoneRow">
                Add Phone Number
              </button>
            </div>
            <div class="card-body">
              <div v-if="phoneNumbers.length === 0 && !showAddPhoneRow" class="text-muted text-center py-3">
                No phone numbers added yet. Click "Add Phone Number" to get started.
              </div>
              
              <form @submit.prevent="saveAllPhones" v-else>
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Country</th>
                        <th>Phone Number</th>
                        <th>Primary</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(phone, index) in phoneNumbers" :key="phone.id || `new-${index}`">
                        <td>
                          <select 
                            v-model="phone.phone_type" 
                            class="form-select form-select-sm"
                            required
                          >
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
                            <option 
                              v-for="country in countryCodes" 
                              :key="country.code" 
                              :value="country.code"
                            >
                              {{ country.flag }} {{ country.code }} - {{ country.name }}
                            </option>
                          </select>
                        </td>
                        <td style="min-width: 200px;">
                          <input 
                            v-model="phone.phone_number" 
                            @input="formatPhoneNumber(phone, index)"
                            type="tel" 
                            class="form-control form-control-sm"
                            :placeholder="phone.country_code === '+1' ? '(555) 123-4567' : 'Enter phone number'"
                            required
                          />
                        </td>
                        <td>
                          <div class="form-check">
                            <input 
                              :value="index"
                              v-model="primaryPhoneIndex"
                              class="form-check-input" 
                              type="radio" 
                              :id="`primary-${index}`"
                              name="primaryPhone"
                            />
                            <label class="form-check-label" :for="`primary-${index}`">
                              <span v-if="primaryPhoneIndex === index" class="badge bg-primary">Primary</span>
                            </label>
                          </div>
                        </td>
                        <td>
                          <button 
                            type="button"
                            class="btn btn-outline-danger btn-sm" 
                            @click="removePhone(index)"
                            :disabled="phoneSaving || phoneNumbers.length === 1"
                          >
                            Remove
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <div v-if="phoneError" class="alert alert-danger mt-3">
                  {{ phoneError }}
                </div>
                
                <div class="d-flex justify-content-between mt-3">
                  <button 
                    type="button" 
                    class="btn btn-secondary" 
                    @click="resetPhoneChanges"
                    :disabled="phoneSaving"
                  >
                    Reset Changes
                  </button>
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="phoneSaving || !isPhoneFormValid"
                  >
                    {{ phoneSaving ? 'Saving...' : 'Save Phone Numbers' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <!-- Addresses Card -->
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Addresses</h5>
              <button class="btn btn-success btn-sm" @click="addNewAddress" :disabled="showAddAddressRow">
                Add Address
              </button>
            </div>
            <div class="card-body">
              <div v-if="addresses.length === 0 && !showAddAddressRow" class="text-muted text-center py-3">
                No addresses added yet. Click "Add Address" to get started.
              </div>
              
              <form @submit.prevent="saveAllAddresses" v-else>
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Country</th>
                        <th>Street Address</th>
                        <th>City</th>
                        <th>State/Province</th>
                        <th>Zip/Postal Code</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(address, index) in addresses" :key="address.id || `new-addr-${index}`">
                        <td>
                          <select 
                            v-model="address.add_type" 
                            class="form-select form-select-sm"
                            required
                          >
                            <option value="">Select type...</option>
                            <option value="Home">Home</option>
                            <option value="Work">Work</option>
                            <option value="School">School</option>
                          </select>
                        </td>
                        <td style="min-width: 180px;">
                          <select 
                            v-model="address.add_country" 
                            class="form-select form-select-sm"
                            required
                          >
                            <option 
                              v-for="country in countries" 
                              :key="country" 
                              :value="country"
                            >
                              {{ country }}
                            </option>
                          </select>
                        </td>
                        <td style="min-width: 250px;">
                          <input 
                            v-model="address.add_line1" 
                            type="text" 
                            class="form-control form-control-sm"
                            placeholder="123 Main Street"
                            required
                          />
                          <input 
                            v-model="address.add_line2" 
                            type="text" 
                            class="form-control form-control-sm mt-1"
                            placeholder="Apt, Suite, etc. (optional)"
                          />
                        </td>
                        <td>
                          <input 
                            v-model="address.add_city" 
                            type="text" 
                            class="form-control form-control-sm"
                            placeholder="City"
                            required
                          />
                        </td>
                        <td>
                          <select 
                            v-if="['United States', 'Canada', 'Australia'].includes(address.add_country)"
                            v-model="address.add_state" 
                            class="form-select form-select-sm"
                            required
                          >
                            <option value="">Select...</option>
                            <optgroup :label="address.add_country">
                              <option 
                                v-for="state in getStatesForCountry(address.add_country)" 
                                :key="state.id" 
                                :value="state.abbrev"
                              >
                                {{ state.name }} ({{ state.abbrev }})
                              </option>
                            </optgroup>
                          </select>
                          <input 
                            v-else
                            v-model="address.add_state" 
                            type="text" 
                            class="form-control form-control-sm"
                            placeholder="Province (optional)"
                          />
                        </td>
                        <td>
                          <input 
                            v-model="address.add_zip" 
                            type="text" 
                            class="form-control form-control-sm"
                            :placeholder="address.add_country === 'United States' ? '12345 (optional)' : 'Postal Code (optional)'"
                          />
                        </td>
                        <td>
                          <button 
                            type="button"
                            class="btn btn-outline-danger btn-sm" 
                            @click="removeAddress(index)"
                            :disabled="addressSaving"
                          >
                            Remove
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <div v-if="addressError" class="alert alert-danger mt-3">
                  {{ addressError }}
                </div>
                
                <div class="d-flex justify-content-between mt-3">
                  <button 
                    type="button" 
                    class="btn btn-secondary" 
                    @click="resetAddressChanges"
                    :disabled="addressSaving"
                  >
                    Reset Changes
                  </button>
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="addressSaving || !isAddressFormValid"
                  >
                    {{ addressSaving ? 'Saving...' : 'Save Addresses' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
        
        <!-- Back to Home -->
        <div class="text-center mt-4">
          <button @click="$router.push('/')" class="btn btn-secondary">Back to Home</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth.js'
import { getCSRFToken } from '../store/auth.js'
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000'

export default {
  name: 'UserAccount',
  setup() {
    const authStore = useAuthStore()
    return {
      authStore
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      accountData: {
        email: '',
        alt_email: ''
      },
      phoneNumbers: [],
      originalPhoneNumbers: [],
      primaryPhoneIndex: 0,
      
      addresses: [],
      originalAddresses: [],
      
      // Countries list for addresses
      countries: [
        'United States',
        'Canada',
        'United Kingdom',
        'Australia',
        'Germany',
        'France',
        'Italy',
        'Spain',
        'Mexico',
        'Brazil',
        'Japan',
        'China',
        'India',
        'South Korea',
        'Russia',
        'South Africa',
        'United Arab Emirates',
        'Saudi Arabia'
      ],
      
      // Account form state
      accountSaving: false,
      accountError: null,
      accountSuccess: null,
      accountErrors: {},
      
      // Phone form state
      showAddPhoneRow: false,
      phoneSaving: false,
      phoneError: null,
      
      // Address form state
      showAddAddressRow: false,
      addressSaving: false,
      addressError: null,
      
      // States and provinces data
      statesProvinces: {},
      statesProvincesLoaded: false,
      
      // Country codes list
      countryCodes: [
        { code: '+1', name: 'United States/Canada', flag: '🇺🇸' },
        { code: '+44', name: 'United Kingdom', flag: '🇬🇧' },
        { code: '+61', name: 'Australia', flag: '🇦🇺' },
        { code: '+81', name: 'Japan', flag: '🇯🇵' },
        { code: '+86', name: 'China', flag: '🇨🇳' },
        { code: '+91', name: 'India', flag: '🇮🇳' },
        { code: '+49', name: 'Germany', flag: '🇩🇪' },
        { code: '+33', name: 'France', flag: '🇫🇷' },
        { code: '+39', name: 'Italy', flag: '🇮🇹' },
        { code: '+34', name: 'Spain', flag: '🇪🇸' },
        { code: '+52', name: 'Mexico', flag: '🇲🇽' },
        { code: '+55', name: 'Brazil', flag: '🇧🇷' },
        { code: '+7', name: 'Russia', flag: '🇷🇺' },
        { code: '+82', name: 'South Korea', flag: '🇰🇷' },
        { code: '+27', name: 'South Africa', flag: '🇿🇦' },
        { code: '+971', name: 'United Arab Emirates', flag: '🇦🇪' },
        { code: '+966', name: 'Saudi Arabia', flag: '🇸🇦' }
      ]
    }
  },
  computed: {
    isPhoneFormValid() {
      return this.phoneNumbers.length > 0 && 
             this.phoneNumbers.every(phone => 
               phone.phone_type && 
               phone.country_code && 
               phone.phone_number && 
               this.getCleanPhoneNumber(phone.phone_number).length > 0
             ) &&
             this.primaryPhoneIndex !== null
    },
    isAddressFormValid() {
      if (this.addresses.length === 0) {
        return true;
      }
      
      return this.addresses.every(address => {
        // Basic required fields (zip is optional)
        const hasBasicFields = address.add_type && address.add_line1 && 
                              address.add_city && address.add_country;
        
        if (!hasBasicFields) {
          console.log('Missing basic fields:', address);
          return false;
        }
        
        // State is required only for United States, Canada, and Australia
        const requiresState = ['United States', 'Canada', 'Australia'].includes(address.add_country);
        
        if (requiresState && !address.add_state) {
          console.log('State required but missing:', address);
          return false;
        }
        
        return true;
      });
    },
    // Get states/provinces for selected country
    getStatesForCountry() {
      return (country) => {
        return this.statesProvinces[country] || [];
      }
    }
  },
  watch: {
    addresses: {
      handler(newVal) {
        console.log('Addresses changed:', newVal);
        console.log('Form valid:', this.isAddressFormValid);
      },
      deep: true
    }
  },
  async mounted() {
    await this.fetchStatesProvinces()
    await this.fetchAccountData()
  },
  methods: {
    async fetchStatesProvinces() {
      try {
        const response = await fetch(`${apiUrl}/api/states-provinces`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          this.statesProvinces = await response.json()
          this.statesProvincesLoaded = true
        }
      } catch (error) {
        console.error('Error fetching states/provinces:', error)
      }
    },
    
    async fetchAccountData() {
      this.loading = true
      this.error = null
      
      try {
        if (!this.authStore.isAuthenticated) {
          await this.authStore.fetchUser()
        }
        
        if (!this.authStore.isAuthenticated) {
          this.$router.push('/login')
          return
        }
        
        const response = await fetch(`${apiUrl}/api/user-account`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          }
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            this.$router.push('/login')
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        this.accountData = {
          email: data.email,
          alt_email: data.alt_email || ''
        }
        
        // Set up phone numbers for editing with formatted display
        this.phoneNumbers = (data.phone_numbers || []).map(phone => ({
          id: phone.id,
          phone_type: phone.phone_type,
          country_code: phone.country_code || '+1',
          phone_number: phone.formatted_number || phone.phone_number,
          is_primary: phone.is_primary
        }))
        
        this.originalPhoneNumbers = JSON.parse(JSON.stringify(this.phoneNumbers))
        
        const primaryIndex = this.phoneNumbers.findIndex(phone => phone.is_primary)
        this.primaryPhoneIndex = primaryIndex >= 0 ? primaryIndex : 0
        
        await this.fetchAddresses()
        
      } catch (error) {
        console.error('Error fetching account data:', error)
        this.error = 'Failed to load account data. Please try again later.'
      } finally {
        this.loading = false
      }
    },
    
    async saveAccountInfo() {
      this.accountSaving = true
      this.accountError = null
      this.accountSuccess = null
      this.accountErrors = {}
      
      try {
        const response = await fetch(`${apiUrl}/api/user-account`, {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify({
            alt_email: this.accountData.alt_email
          })
        })
        
        if (response.ok) {
          this.accountSuccess = 'Account information updated successfully!'
          setTimeout(() => {
            this.accountSuccess = null
          }, 3000)
        } else {
          const errorData = await response.json()
          if (response.status === 400) {
            this.accountErrors = errorData
          } else {
            this.accountError = errorData.detail || 'Failed to update account information'
          }
        }
      } catch (error) {
        console.error('Error saving account info:', error)
        this.accountError = 'Failed to save account information. Please try again.'
      } finally {
        this.accountSaving = false
      }
    },
    
    formatPhoneNumber(phone, index) {
      const countryCode = phone.country_code || '+1';
      let value = phone.phone_number;
      
      // Remove all non-digit characters
      const cleaned = value.replace(/\D/g, '');
      
      // Format based on country code
      if (countryCode === '+1') {
        // US/Canada format: (XXX) XXX-XXXX
        if (cleaned.length === 0) {
          phone.phone_number = '';
        } else if (cleaned.length <= 3) {
          phone.phone_number = cleaned;
        } else if (cleaned.length <= 6) {
          phone.phone_number = `(${cleaned.slice(0, 3)}) ${cleaned.slice(3)}`;
        } else {
          phone.phone_number = `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6, 10)}`;
        }
      } else {
        // For other countries, just clean the input (no special formatting)
        phone.phone_number = cleaned;
      }
    },
    
    getCleanPhoneNumber(formattedNumber) {
      // Remove all non-digit characters for API submission
      return formattedNumber.replace(/\D/g, '');
    },
    
    addNewPhone() {
      if (this.showAddPhoneRow) return
      
      this.phoneNumbers.push({
        id: null,
        phone_type: '',
        country_code: '+1', // Default to US
        phone_number: '',
        is_primary: false
      })
      
      this.showAddPhoneRow = true
      this.phoneError = null
    },
    
    removePhone(index) {
      if (this.phoneNumbers.length <= 1) {
        this.phoneError = 'You must have at least one phone number.'
        return
      }
      
      const removedPhone = this.phoneNumbers[index]
      
      if (!removedPhone.id) {
        this.showAddPhoneRow = false
      }
      
      this.phoneNumbers.splice(index, 1)
      
      if (this.primaryPhoneIndex === index) {
        this.primaryPhoneIndex = 0
      } else if (this.primaryPhoneIndex > index) {
        this.primaryPhoneIndex--
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
      this.phoneSaving = true
      this.phoneError = null
      
      try {
        // Set primary status based on radio button selection
        this.phoneNumbers.forEach((phone, index) => {
          phone.is_primary = index === this.primaryPhoneIndex
        })
        
        // First, unset all phones as primary to avoid conflicts
        const unsetPromises = this.phoneNumbers
          .filter(phone => phone.id)
          .map(phone => 
            fetch(`${apiUrl}/api/phone-numbers/${phone.id}/`, {
              method: 'PUT',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify({
                phone_type: phone.phone_type,
                country_code: phone.country_code || '+1',
                phone_number: this.getCleanPhoneNumber(phone.phone_number),
                is_primary: false
              })
            })
          )
        
        await Promise.all(unsetPromises)
        
        // Then update/create all phones with correct primary status
        const updatePromises = this.phoneNumbers.map(async (phone) => {
          const payload = {
            phone_type: phone.phone_type,
            country_code: phone.country_code || '+1',
            phone_number: this.getCleanPhoneNumber(phone.phone_number),
            is_primary: phone.is_primary
          }
          
          if (phone.id) {
            return fetch(`${apiUrl}/api/phone-numbers/${phone.id}/`, {
              method: 'PUT',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify(payload)
            })
          } else {
            return fetch(`${apiUrl}/api/phone-numbers/`, {
              method: 'POST',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify(payload)
            })
          }
        })
        
        const responses = await Promise.all(updatePromises)
        const allSuccess = responses.every(response => response.ok)
        
        if (allSuccess) {
          await this.fetchAccountData()
          this.showAddPhoneRow = false
        } else {
          const errorResponse = responses.find(response => !response.ok)
          const errorData = await errorResponse.json()
          this.phoneError = errorData.detail || 'Failed to save phone numbers'
        }
      } catch (error) {
        console.error('Error saving phones:', error)
        this.phoneError = 'Failed to save phone numbers. Please try again.'
      } finally {
        this.phoneSaving = false
      }
    },
    
    async fetchAddresses() {
      try {
        const response = await fetch(`${apiUrl}/api/addresses/`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          this.addresses = data.map(address => ({
            id: address.id,
            add_type: address.add_type,
            add_line1: address.add_line1,
            add_line2: address.add_line2 || '',
            add_city: address.add_city,
            add_state: address.add_state || '',
            add_zip: address.add_zip,
            add_country: address.add_country || 'United States'
          }))
          
          this.originalAddresses = JSON.parse(JSON.stringify(this.addresses))
        }
      } catch (error) {
        console.error('Error fetching addresses:', error)
      }
    },
    
    addNewAddress() {
      if (this.showAddAddressRow) return
      
      this.addresses.push({
        id: null,
        add_type: '',
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: 'United States'
      })
      
      this.showAddAddressRow = true
      this.addressError = null
    },
    
    removeAddress(index) {
      const removedAddress = this.addresses[index]
      
      if (!removedAddress.id) {
        this.showAddAddressRow = false
      }
      
      this.addresses.splice(index, 1)
    },
    
    resetAddressChanges() {
      this.addresses = JSON.parse(JSON.stringify(this.originalAddresses))
      this.showAddAddressRow = false
      this.addressError = null
    },
    
    async saveAllAddresses() {
      this.addressSaving = true
      this.addressError = null
      
      try {
        const promises = this.addresses.map(async (address) => {
          // Determine if state should be sent based on country
          const stateValue = ['United States', 'Canada', 'Australia'].includes(address.add_country) 
            ? address.add_state 
            : null;
          
          const payload = {
            add_type: address.add_type,
            add_line1: address.add_line1,
            add_line2: address.add_line2,
            add_city: address.add_city,
            add_state: stateValue,
            add_zip: address.add_zip || '',
            add_country: address.add_country
          };
          
          if (address.id) {
            return fetch(`${apiUrl}/api/addresses/${address.id}/`, {
              method: 'PUT',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify(payload)
            })
          } else {
            return fetch(`${apiUrl}/api/addresses/`, {
              method: 'POST',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
              },
              body: JSON.stringify(payload)
            })
          }
        })
        
        const responses = await Promise.all(promises)
        const allSuccess = responses.every(response => response.ok)
        
        if (allSuccess) {
          await this.fetchAddresses()
          this.showAddAddressRow = false
        } else {
          const errorResponse = responses.find(response => !response.ok)
          const errorData = await errorResponse.json()
          
          if (errorData.add_type) {
            this.addressError = errorData.add_type[0]
          } else if (errorData.add_state) {
            this.addressError = errorData.add_state[0] || errorData.add_state
          } else {
            this.addressError = errorData.detail || 'Failed to save addresses'
          }
        }
      } catch (error) {
        console.error('Error saving addresses:', error)
        this.addressError = 'Failed to save addresses. Please try again.'
      } finally {
        this.addressSaving = false
      }
    }
  }
}
</script>