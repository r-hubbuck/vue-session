<template>
  <div class="address-list-container">
    <h1>My Addresses</h1>
    
    <div v-if="loading" class="loading">
      Loading addresses...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="addresses.length === 0" class="no-addresses">
      <p>You don't have any addresses saved yet.</p>
      <button @click="$router.push('/')" class="btn-primary">Go Back Home</button>
    </div>
    
    <div v-else class="addresses-grid">
      <div v-for="address in addresses" :key="address.id" class="address-card" @click="editAddress(address)">
        <h3>{{ address.add_type }}</h3>
        <div class="address-details">
          <p><strong>Street:</strong> {{ address.add_line1 }} <span v-if="address.add_line2">, {{ address.add_line2 }}</span></p>
          <p><strong>City:</strong> {{ address.add_city }}</p>
          <p><strong>State:</strong> {{ address.add_state }}</p>
          <p><strong>ZIP:</strong> {{ address.add_zip }}</p>
          <p v-if="address.add_country"><strong>Country:</strong> {{ address.add_country }}</p>
        </div>
        <div class="card-overlay">
          <span>Click to edit</span>
        </div>
      </div>
    </div>
    
    <!-- Address Form Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ isEditing ? 'Edit Address' : 'Add New Address' }}</h2>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>
        
        <form @submit.prevent="saveAddress" class="address-form">
          <div class="form-group">
            <label for="add_type">Address Type:</label>
            <select v-model="formData.add_type" id="add_type" required>
              <option value="">Select type...</option>
              <option value="Home">Home</option>
              <option value="Work">Work</option>
              <option value="School">School</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="add_line1">Street Address:</label>
            <input v-model="formData.add_line1" type="text" id="add_line1" required>
          </div>
          
          <div class="form-group">
            <label for="add_line2">Address Line 2 (Optional):</label>
            <input v-model="formData.add_line2" type="text" id="add_line2">
          </div>
          
          <div class="form-group">
            <label for="add_city">City:</label>
            <input v-model="formData.add_city" type="text" id="add_city" required>
          </div>
          
          <div class="form-group">
            <label for="add_state">State:</label>
            <input v-model="formData.add_state" type="text" id="add_state" required>
          </div>
          
          <div class="form-group">
            <label for="add_zip">ZIP Code:</label>
            <input v-model="formData.add_zip" type="text" id="add_zip" required>
          </div>
          
          <div class="form-group">
            <label for="add_country">Country (Optional):</label>
            <input v-model="formData.add_country" type="text" id="add_country">
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button v-if="isEditing" type="button" @click="deleteAddress" class="btn-delete">Delete</button>
            <button type="submit" class="btn-save" :disabled="saving">
              {{ saving ? 'Saving...' : (isEditing ? 'Update' : 'Add') }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <div class="actions">
      <button @click="$router.push('/')" class="btn-secondary">Back to Home</button>
      <button @click="addNewAddress" class="btn-add">Add New Address</button>
      <button @click="refreshAddresses" class="btn-primary">Refresh</button>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../store/auth.js'
import { getCSRFToken } from '../store/auth.js'

export default {
  name: 'AddressList',
  setup() {
    const authStore = useAuthStore()
    return {
      authStore
    }
  },
  data() {
    return {
      addresses: [],
      loading: true,
      error: null,
      modalError: null,
      showModal: false,
      isEditing: false,
      saving: false,
      currentAddress: null,
      formData: {
        add_type: '',
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: ''
      }
    }
  },
  async mounted() {
    await this.fetchAddresses()
  },
  methods: {
    async fetchAddresses() {
      this.loading = true
      this.error = null
      
      try {
        // First ensure user is authenticated
        if (!this.authStore.isAuthenticated) {
          await this.authStore.fetchUser()
        }
        
        if (!this.authStore.isAuthenticated) {
          this.$router.push('/login')
          return
        }
        
        // Fetch addresses from the API
        const response = await fetch('http://localhost:9000/api/addresses/', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          }
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            // User is not authenticated
            this.$router.push('/login')
            return
          } else if (response.status === 403) {
            this.error = 'You do not have permission to view addresses.'
            return
          } else {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
        }
        
        const data = await response.json()
        this.addresses = data
      } catch (error) {
        console.error('Error fetching addresses:', error)
        
        // Error handling is now done above in the response check
        // This catch block handles network errors or other exceptions
        this.error = 'Failed to load addresses. Please try again later.'
      } finally {
        this.loading = false
      }
    },
    
    async refreshAddresses() {
      await this.fetchAddresses()
    },
    
    addNewAddress() {
      this.isEditing = false
      this.currentAddress = null
      this.modalError = null
      this.formData = {
        add_type: '',
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: ''
      }
      this.showModal = true
    },
    
    editAddress(address) {
      this.isEditing = true
      this.currentAddress = address
      this.modalError = null
      this.formData = {
        add_type: address.add_type || '',
        add_line1: address.add_line1 || '',
        add_line2: address.add_line2 || '',
        add_city: address.add_city || '',
        add_state: address.add_state || '',
        add_zip: address.add_zip || '',
        add_country: address.add_country || ''
      }
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.isEditing = false
      this.currentAddress = null
      this.saving = false
      this.modalError = null
      this.formData = {
        add_type: '',
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: ''
      }
    },
    
    async saveAddress() {
      this.saving = true
      this.error = null
      this.modalError = null
      
      try {
        const url = this.isEditing 
          ? `http://localhost:9000/api/addresses/${this.currentAddress.id}/`
          : 'http://localhost:9000/api/addresses/'
        
        const method = this.isEditing ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method: method,
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
          },
          body: JSON.stringify(this.formData)
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            this.$router.push('/login')
            return
          } else if (response.status === 403) {
            this.modalError = 'You do not have permission to modify addresses.'
            return
          } else if (response.status === 400) {
            // Handle validation errors (like duplicate address type)
            const errorData = await response.json()
            if (errorData.detail) {
              this.modalError = errorData.detail
            } else if (errorData.non_field_errors) {
              this.modalError = errorData.non_field_errors[0]
            } else if (errorData.add_type) {
              this.modalError = errorData.add_type[0]
            } else {
              this.modalError = 'Invalid data provided. Please check your input.'
            }
            return
          } else {
            const errorData = await response.json()
            this.modalError = errorData.detail || `HTTP error! status: ${response.status}`
            return
          }
        }
        
        // Success - refresh the addresses list and close modal
        await this.fetchAddresses()
        this.closeModal()
        
      } catch (error) {
        console.error('Error saving address:', error)
        this.modalError = error.message || 'Failed to save address. Please try again.'
      } finally {
        this.saving = false
      }
    },
    
    async deleteAddress() {
      if (!confirm('Are you sure you want to delete this address?')) {
        return
      }
      
      this.saving = true
      this.error = null
      
      try {
        const response = await fetch(`http://localhost:9000/api/addresses/${this.currentAddress.id}/`, {
          method: 'DELETE',
          credentials: 'include',
          headers: {
            'X-CSRFToken': getCSRFToken()
          }
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            this.$router.push('/login')
            return
          } else if (response.status === 403) {
            this.error = 'You do not have permission to delete addresses.'
            return
          } else {
            throw new Error(`HTTP error! status: ${response.status}`)
          }
        }
        
        // Success - refresh the addresses list and close modal
        await this.fetchAddresses()
        this.closeModal()
        
      } catch (error) {
        console.error('Error deleting address:', error)
        this.error = 'Failed to delete address. Please try again.'
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.address-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.loading, .error, .no-addresses {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.no-addresses {
  color: #6c757d;
}

.addresses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.address-card {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s ease;
  cursor: pointer;
  position: relative;
}

.address-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.address-card:hover .card-overlay {
  opacity: 1;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 123, 255, 0.9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  border-radius: 8px;
  font-weight: bold;
}

.address-card h3 {
  margin: 0 0 15px 0;
  color: #007bff;
  text-transform: capitalize;
}

.address-details p {
  margin: 8px 0;
  line-height: 1.5;
}

.address-details strong {
  color: #333;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-add {
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.btn-add:hover {
  background-color: #218838;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.modal-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 12px 20px;
  margin: 0 20px 20px 20px;
  font-size: 14px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.address-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.btn-save {
  background-color: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.btn-save:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-save:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.btn-cancel:hover {
  background-color: #545b62;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.btn-delete:hover {
  background-color: #c82333;
}
</style>