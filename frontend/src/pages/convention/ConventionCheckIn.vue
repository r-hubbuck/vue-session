<template>
  <div>
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Convention Check-In</h1>
        <p class="page-subtitle">Review and check in attendees for the current convention</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-container">
      <!-- Stats Summary - Minimal inline style -->
      <div class="stats-summary" v-if="!loading && registrations.length > 0">
        <p class="stats-text">
          <span><strong>{{ totalRegistrations }}</strong> registered</span>
          <span>•</span>
          <span class="text-success"><strong>{{ checkedInCount }}</strong> checked in</span>
          <span>•</span>
          <span class="text-warning"><strong>{{ pendingCount }}</strong> pending</span>
          <span>•</span>
          <span class="text-danger"><strong>{{ cancelledCount }}</strong> cancelled</span>
        </p>
      </div>

      <!-- Search and Filters -->
      <div class="section-card" v-if="!loading">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Search</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="form-control" 
              placeholder="Search by name, member number, or chapter..."
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">Status Filter</label>
            <select v-model="statusFilter" class="form-select">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="checked_in">Checked In</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Sort By</label>
            <select v-model="sortBy" class="form-select">
              <option value="last_name">Last Name</option>
              <option value="chapter">Chapter</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading registrations...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="section-card">
        <div class="alert alert-danger" style="border-left: 4px solid #ef4444;">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
        </div>
      </div>

      <!-- Registrations Table (no header) -->
      <div v-if="!loading && !error" class="section-card">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Member #</th>
                <th>Name</th>
                <th>Chapter</th>
                <th>Guest</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredRegistrations.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No registrations found
                </td>
              </tr>
              <tr 
                v-for="reg in filteredRegistrations" 
                :key="reg.id"
                :class="getRowClass(reg)"
                class="registration-row"
              >
                <td>
                  <span class="text-muted">#{{ reg.member_number || 'N/A' }}</span>
                </td>
                <td>
                  <strong>{{ reg.first_name }} {{ reg.last_name }}</strong>
                  <div v-if="reg.preferred_first_name && reg.preferred_first_name !== reg.first_name" class="text-muted small">
                    Preferred: {{ reg.preferred_first_name }}
                  </div>
                </td>
                <td>{{ reg.chapter }}</td>
                <td>
                  <span v-if="reg.has_guest" class="badge bg-info">
                    <i class="bi bi-person-plus-fill me-1"></i>
                    {{ reg.guest_count }} Guest{{ reg.guest_count > 1 ? 's' : '' }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(reg.status_code)">
                    {{ getStatusDisplay(reg.status_code) }}
                  </span>
                  <div v-if="reg.checked_in_at" class="text-muted small mt-1">
                    {{ formatDateTime(reg.checked_in_at) }}
                  </div>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button 
                      v-if="reg.status_code !== 'checked_in'"
                      class="btn btn-sm btn-success"
                      @click="openCheckInModal(reg)"
                      title="Check In"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <button 
                      v-if="reg.status_code !== 'cancelled'"
                      class="btn btn-sm btn-danger"
                      @click="cancelRegistration(reg)"
                      title="Cancel"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                    <button 
                      v-if="reg.status_code === 'cancelled'"
                      class="btn btn-sm btn-primary"
                      @click="reactivateRegistration(reg)"
                      title="Reactivate"
                    >
                      <i class="bi bi-arrow-counterclockwise"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Check-In Modal -->
    <div 
      class="modal fade" 
      id="checkInModal" 
      tabindex="-1" 
      aria-labelledby="checkInModalLabel" 
      aria-hidden="true"
      data-bs-backdrop="static"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content" v-if="selectedRegistration">
          <div class="modal-header">
            <h5 class="modal-title" id="checkInModalLabel">
              <i class="bi bi-check-circle me-2"></i>
              Check In: {{ selectedRegistration.first_name }} {{ selectedRegistration.last_name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="closeModal"></button>
          </div>
          
          <div class="modal-body">
            <!-- Member Info Summary -->
            <div class="info-alert mb-4">
              <i class="bi bi-person-badge-fill"></i>
              <div class="info-alert-content">
                <strong>{{ selectedRegistration.first_name }} {{ selectedRegistration.last_name }}</strong> 
                ({{ selectedRegistration.chapter }})
                <span v-if="selectedRegistration.has_guest" class="ms-2">
                  • {{ selectedRegistration.guest_count }} Guest{{ selectedRegistration.guest_count > 1 ? 's' : '' }}
                </span>
              </div>
            </div>

            <!-- Address Review Section -->
            <div class="address-section">
              <h6 class="mb-3">
                <i class="bi bi-geo-alt-fill me-2"></i>
                Primary Mailing Address
              </h6>
              
              <div v-if="!selectedRegistration.primary_address" class="alert alert-warning" style="border-left: 4px solid #f59e0b;">
                <i class="bi bi-exclamation-triangle me-2"></i>
                No primary address on file. Please add an address before checking in.
              </div>

              <div v-else>
                <div v-if="!editingAddress" class="address-display">
                  <div class="card bg-light">
                    <div class="card-body">
                      <p class="mb-2">{{ addressForm.add_line1 }}</p>
                      <p v-if="addressForm.add_line2" class="mb-2">{{ addressForm.add_line2 }}</p>
                      <p class="mb-2">
                        {{ addressForm.add_city }}<span v-if="addressForm.add_state">, {{ addressForm.add_state }}</span> {{ addressForm.add_zip }}
                      </p>
                      <p class="mb-0">{{ addressForm.add_country }}</p>
                    </div>
                  </div>
                  
                  <div class="info-alert mt-3">
                    <i class="bi bi-info-circle-fill"></i>
                    <div class="info-alert-content">
                      Please review the address with the member. Is this information correct and current?
                    </div>
                  </div>

                  <div class="d-flex gap-2 mt-3">
                    <button 
                      class="btn btn-success flex-fill"
                      @click="confirmAddressAndCheckIn"
                      :disabled="savingCheckIn"
                    >
                      <i class="bi bi-check-circle me-2"></i>
                      <span v-if="savingCheckIn">Checking In...</span>
                      <span v-else>Address Correct - Check In</span>
                    </button>
                    <button 
                      class="btn btn-warning"
                      @click="startEditingAddress"
                    >
                      <i class="bi bi-pencil me-2"></i>Edit Address
                    </button>
                  </div>
                </div>

                <div v-else class="address-edit">
                  <form @submit.prevent="saveAddressAndCheckIn">
                    <div class="mb-3">
                      <label class="form-label">Address Line 1 <span class="text-danger">*</span></label>
                      <input
                        v-model="addressForm.add_line1"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': addressErrors.add_line1 }"
                        required
                        maxlength="255"
                      >
                      <div v-if="addressErrors.add_line1" class="invalid-feedback">
                        {{ addressErrors.add_line1 }}
                      </div>
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Address Line 2</label>
                      <input
                        v-model="addressForm.add_line2"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': addressErrors.add_line2 }"
                        maxlength="255"
                      >
                      <div v-if="addressErrors.add_line2" class="invalid-feedback">
                        {{ addressErrors.add_line2 }}
                      </div>
                    </div>

                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label">City <span class="text-danger">*</span></label>
                        <input
                          v-model="addressForm.add_city"
                          type="text"
                          class="form-control"
                          :class="{ 'is-invalid': addressErrors.add_city }"
                          required
                          maxlength="100"
                        >
                        <div v-if="addressErrors.add_city" class="invalid-feedback">
                          {{ addressErrors.add_city }}
                        </div>
                      </div>

                      <div class="col-md-3 mb-3">
                        <label class="form-label">State/Province</label>
                        <input 
                          v-model="addressForm.add_state"
                          type="text"
                          class="form-control"
                          :class="{ 'is-invalid': addressErrors.add_state }"
                          maxlength="100"
                        >
                        <div v-if="addressErrors.add_state" class="invalid-feedback">
                          {{ addressErrors.add_state }}
                        </div>
                      </div>

                      <div class="col-md-3 mb-3">
                        <label class="form-label">Zip/Postal Code</label>
                        <input 
                          v-model="addressForm.add_zip"
                          type="text"
                          class="form-control"
                          :class="{ 'is-invalid': addressErrors.add_zip }"
                          maxlength="20"
                        >
                        <div v-if="addressErrors.add_zip" class="invalid-feedback">
                          {{ addressErrors.add_zip }}
                        </div>
                      </div>
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Country <span class="text-danger">*</span></label>
                      <input
                        v-model="addressForm.add_country"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': addressErrors.add_country }"
                        required
                        maxlength="100"
                      >
                      <div v-if="addressErrors.add_country" class="invalid-feedback">
                        {{ addressErrors.add_country }}
                      </div>
                    </div>

                    <div v-if="addressSaveError" class="alert alert-danger" style="border-left: 4px solid #ef4444;">
                      <i class="bi bi-exclamation-triangle me-2"></i>{{ addressSaveError }}
                    </div>

                    <div class="d-flex gap-2">
                      <button 
                        type="submit" 
                        class="btn btn-success flex-fill"
                        :disabled="savingCheckIn"
                      >
                        <i class="bi bi-save me-2"></i>
                        <span v-if="savingCheckIn">Saving & Checking In...</span>
                        <span v-else>Save Address & Check In</span>
                      </button>
                      <button 
                        type="button"
                        class="btn btn-secondary"
                        @click="cancelEditingAddress"
                        :disabled="savingCheckIn"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api';

export default {
  name: 'ConventionCheckIn',
  
  data() {
    return {
      loading: true,
      error: null,
      registrations: [],
      selectedRegistration: null,
      searchQuery: '',
      statusFilter: '',
      sortBy: 'last_name',
      editingAddress: false,
      savingCheckIn: false,
      addressSaveError: null,
      addressErrors: {},
      addressForm: {
        add_line1: '',
        add_line2: '',
        add_city: '',
        add_state: '',
        add_zip: '',
        add_country: 'United States',
      },
    };
  },

  computed: {
    totalRegistrations() {
      return this.registrations.length;
    },

    checkedInCount() {
      return this.registrations.filter(r => r.status_code === 'checked_in').length;
    },

    pendingCount() {
      return this.registrations.filter(r => 
        r.status_code !== 'checked_in' && r.status_code !== 'cancelled'
      ).length;
    },

    cancelledCount() {
      return this.registrations.filter(r => r.status_code === 'cancelled').length;
    },

    filteredRegistrations() {
      let filtered = [...this.registrations];

      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(reg => 
          reg.first_name.toLowerCase().includes(query) ||
          reg.last_name.toLowerCase().includes(query) ||
          reg.chapter.toLowerCase().includes(query) ||
          (reg.member_number && reg.member_number.toString().includes(query))
        );
      }

      if (this.statusFilter) {
        if (this.statusFilter === 'pending') {
          filtered = filtered.filter(r => 
            r.status_code !== 'checked_in' && r.status_code !== 'cancelled'
          );
        } else {
          filtered = filtered.filter(r => r.status_code === this.statusFilter);
        }
      }

      filtered.sort((a, b) => {
        if (this.sortBy === 'last_name') {
          return a.last_name.localeCompare(b.last_name);
        } else if (this.sortBy === 'chapter') {
          return a.chapter.localeCompare(b.chapter);
        } else if (this.sortBy === 'status') {
          return a.status_code.localeCompare(b.status_code);
        }
        return 0;
      });

      return filtered;
    },
  },

  mounted() {
    this.loadRegistrations();
  },

  methods: {
    async loadRegistrations() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get('/api/convention/check-in/list/');
        
        if (Array.isArray(response.data)) {
          this.registrations = response.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          this.registrations = response.data.results;
        } else {
          console.error('Unexpected response format:', response.data);
          this.registrations = [];
          this.error = 'Unexpected data format received from server.';
        }
      } catch (err) {
        console.error('Error loading registrations:', err);
        this.registrations = [];
        
        if (err.response?.status === 403) {
          this.error = 'Access denied. Staff permissions required.';
        } else if (err.response?.status === 404) {
          this.error = 'No active convention found.';
        } else {
          this.error = err.response?.data?.message || err.response?.data?.detail || 'Failed to load registrations. Please try again.';
        }
      } finally {
        this.loading = false;
      }
    },

    openCheckInModal(registration) {
      this.selectedRegistration = registration;
      this.editingAddress = false;
      this.savingCheckIn = false;
      this.addressSaveError = null;
      this.addressErrors = {};
      
      if (registration.primary_address) {
        this.addressForm = {
          add_line1: registration.primary_address.add_line1 || '',
          add_line2: registration.primary_address.add_line2 || '',
          add_city: registration.primary_address.add_city || '',
          add_state: registration.primary_address.add_state || '',
          add_zip: registration.primary_address.add_zip || '',
          add_country: registration.primary_address.add_country || 'United States',
        };
      }
      
      const modalElement = document.getElementById('checkInModal');
      if (modalElement) {
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = new window.bootstrap.Modal(modalElement);
          modal.show();
        } else {
          if (window.jQuery) {
            window.jQuery(modalElement).modal('show');
          } else {
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
            
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            backdrop.id = 'checkInModalBackdrop';
            document.body.appendChild(backdrop);
          }
        }
      }
    },

    startEditingAddress() {
      this.editingAddress = true;
      this.addressErrors = {};
      this.addressSaveError = null;
    },

    cancelEditingAddress() {
      this.editingAddress = false;
      this.addressErrors = {};
      this.addressSaveError = null;
      
      if (this.selectedRegistration.primary_address) {
        this.addressForm = {
          add_line1: this.selectedRegistration.primary_address.add_line1 || '',
          add_line2: this.selectedRegistration.primary_address.add_line2 || '',
          add_city: this.selectedRegistration.primary_address.add_city || '',
          add_state: this.selectedRegistration.primary_address.add_state || '',
          add_zip: this.selectedRegistration.primary_address.add_zip || '',
          add_country: this.selectedRegistration.primary_address.add_country || 'United States',
        };
      }
    },

    async confirmAddressAndCheckIn() {
      await this.performCheckIn();
    },

    async saveAddressAndCheckIn() {
      this.savingCheckIn = true;
      this.addressErrors = {};
      this.addressSaveError = null;

      try {
        // Updated to use accounts app endpoint which includes database sync
        await api.put(
          `/api/accounts/addresses/${this.selectedRegistration.primary_address.id}/`,
          this.addressForm
        );

        await this.performCheckIn();
      } catch (err) {
        console.error('Error saving address:', err);
        if (err.response?.data) {
          this.addressErrors = err.response.data;
          this.addressSaveError = 'Please correct the errors above and try again.';
        } else {
          this.addressSaveError = 'Failed to save address. Please try again.';
        }
        this.savingCheckIn = false;
      }
    },

    async performCheckIn() {
      try {
        const response = await api.put(
          `/api/convention/check-in/registration/${this.selectedRegistration.id}/status/`,
          {
            status_code: 'checked_in',
            at_convention: true
          }
        );

        const index = this.registrations.findIndex(r => r.id === this.selectedRegistration.id);
        if (index !== -1) {
          this.registrations.splice(index, 1, response.data);
        }

        this.closeModal();
        alert('Successfully checked in!');
      } catch (err) {
        console.error('Error checking in:', err);
        this.addressSaveError = err.response?.data?.message || 'Failed to check in. Please try again.';
      } finally {
        this.savingCheckIn = false;
      }
    },

    closeModal() {
      const modalElement = document.getElementById('checkInModal');
      if (modalElement) {
        if (window.bootstrap && window.bootstrap.Modal) {
          const modal = window.bootstrap.Modal.getInstance(modalElement);
          if (modal) {
            modal.hide();
          }
        } else {
          if (window.jQuery) {
            window.jQuery(modalElement).modal('hide');
          } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
            
            const backdrop = document.getElementById('checkInModalBackdrop');
            if (backdrop) {
              backdrop.remove();
            }
          }
        }
      }
    },

    async cancelRegistration(registration) {
      if (!confirm(`Are you sure you want to cancel the registration for ${registration.first_name} ${registration.last_name}?`)) {
        return;
      }

      try {
        const response = await api.put(
          `/api/convention/check-in/registration/${registration.id}/status/`,
          {
            status_code: 'cancelled',
            at_convention: false
          }
        );

        const index = this.registrations.findIndex(r => r.id === registration.id);
        if (index !== -1) {
          this.registrations.splice(index, 1, response.data);
        }

        alert('Registration cancelled successfully.');
      } catch (err) {
        console.error('Error cancelling registration:', err);
        alert(err.response?.data?.message || 'Failed to cancel registration. Please try again.');
      }
    },

    async reactivateRegistration(registration) {
      if (!confirm(`Reactivate the registration for ${registration.first_name} ${registration.last_name}?`)) {
        return;
      }

      try {
        const response = await api.put(
          `/api/convention/check-in/registration/${registration.id}/status/`,
          {
            status_code: 'registered',
            at_convention: false
          }
        );

        const index = this.registrations.findIndex(r => r.id === registration.id);
        if (index !== -1) {
          this.registrations.splice(index, 1, response.data);
        }

        alert('Registration reactivated successfully.');
      } catch (err) {
        console.error('Error reactivating registration:', err);
        alert(err.response?.data?.message || 'Failed to reactivate registration. Please try again.');
      }
    },

    getRowClass(registration) {
      if (registration.status_code === 'checked_in') {
        return 'table-success';
      } else if (registration.status_code === 'cancelled') {
        return 'table-danger';
      }
      return '';
    },

    getStatusBadgeClass(statusCode) {
      switch (statusCode) {
        case 'checked_in':
          return 'bg-success';
        case 'cancelled':
          return 'bg-danger';
        case 'confirmed':
          return 'bg-info';
        case 'waitlisted':
          return 'bg-warning';
        default:
          return 'bg-secondary';
      }
    },

    getStatusDisplay(statusCode) {
      const statusMap = {
        'registered': 'Registered',
        'confirmed': 'Confirmed',
        'cancelled': 'Cancelled',
        'checked_in': 'Checked In',
        'waitlisted': 'Waitlisted',
      };
      return statusMap[statusCode] || statusCode;
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const date = new Date(dateTimeString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    },
  },
};
</script>

<style scoped>
/* Stats Summary - Minimal inline style */
.stats-summary {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stats-text {
  font-size: 1rem;
  color: #374151;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.stats-text strong {
  font-weight: 700;
  font-size: 1.125rem;
}

/* Table styles */
.registration-row {
  transition: background-color 0.2s;
}

.registration-row:hover {
  background-color: #f9fafb !important;
}

.registration-row.table-success {
  background-color: #d1fae5 !important;
}

.registration-row.table-success:hover {
  background-color: #a7f3d0 !important;
}

.registration-row.table-danger {
  background-color: #fee2e2 !important;
}

.registration-row.table-danger:hover {
  background-color: #fecaca !important;
}

/* Modal styles */
.modal-header {
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  color: white;
  border-bottom: none;
  padding: 1.5rem;
}

.modal-header .btn-close {
  filter: brightness(0) invert(1);
}

.address-display .card {
  border: 1px solid #e5e7eb;
}

.address-display .card-body p {
  margin-bottom: 0.25rem;
  color: #374151;
}
</style>
