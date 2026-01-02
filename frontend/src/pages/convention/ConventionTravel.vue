<template>
  <div class="convention-travel-admin">
    <div class="page-header">
      <h1>Convention Travel Management</h1>
      <p class="text-muted">Review and manage member travel arrangements</p>
    </div>

    <!-- Filters -->
    <div class="filters-section card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Travel Method</label>
            <select v-model="filters.travelMethod" class="form-select" @change="loadTravelData">
              <option value="">All Methods</option>
              <option value="need_booking">Need Flight Booked</option>
              <option value="self_booking">Booking Own Flight</option>
              <option value="driving">Driving</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Booking Status</label>
            <select v-model="filters.bookingStatus" class="form-select" @change="loadTravelData">
              <option value="">All Statuses</option>
              <option value="false">Pending Booking</option>
              <option value="true">Flight Booked</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="form-control" 
              placeholder="Search by name or chapter..."
            >
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle"></i> {{ error }}
    </div>

    <!-- Travel List -->
    <div v-if="!loading && !error" class="travel-list">
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Chapter</th>
                  <th>Travel Method</th>
                  <th>Departure</th>
                  <th>Return</th>
                  <th>Seat Pref</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredTravels.length === 0">
                  <td colspan="8" class="text-center text-muted py-4">
                    No travel records found
                  </td>
                </tr>
                <tr v-for="travel in filteredTravels" :key="travel.id">
                  <td>
                    <strong>{{ travel.first_name }} {{ travel.last_name }}</strong>
                    <br>
                    <small class="text-muted">Member #{{ travel.member_number }}</small>
                  </td>
                  <td>{{ travel.chapter }}</td>
                  <td>
                    <span class="badge" :class="getTravelMethodClass(travel.travel_method)">
                      {{ travel.travel_method_display }}
                    </span>
                  </td>
                  <td>
                    <div v-if="travel.departure_airport">
                      <strong>{{ travel.departure_airport }}</strong> ({{ travel.departure_state }})
                      <br>
                      <small class="text-muted">
                        {{ formatDate(travel.departure_date) }}
                        <span v-if="travel.departure_time_formatted"> at {{ travel.departure_time_formatted }}</span>
                      </small>
                    </div>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>
                    <div v-if="travel.return_airport">
                      <strong>{{ travel.return_airport }}</strong> ({{ travel.return_state }})
                      <br>
                      <small class="text-muted">
                        {{ formatDate(travel.return_date) }}
                        <span v-if="travel.return_time_formatted"> at {{ travel.return_time_formatted }}</span>
                      </small>
                    </div>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>{{ travel.seat_preference_display }}</td>
                  <td>
                    <span 
                      class="badge" 
                      :class="travel.has_booked_flight ? 'bg-success' : 'bg-warning'"
                    >
                      {{ travel.has_booked_flight ? 'Booked' : 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <button 
                      class="btn btn-sm btn-primary"
                      @click="openTravelDetail(travel.id)"
                    >
                      <i class="bi bi-pencil"></i> Edit
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>


    <!-- Travel Detail Modal -->
    <div 
      class="modal fade" 
      id="travelDetailModal" 
      tabindex="-1" 
      aria-labelledby="travelDetailModalLabel" 
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content" v-if="selectedTravel">
          <div class="modal-header">
            <h5 class="modal-title" id="travelDetailModalLabel">
              Flight Booking Details - {{ selectedTravel.member.first_name }} {{ selectedTravel.member.last_name }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              data-bs-dismiss="modal" 
              aria-label="Close"
            ></button>
          </div>
          
          <div class="modal-body">
            <!-- Member Info Section -->
            <div class="member-info-section mb-4">
              <h6 class="fw-bold mb-3">Member Information</h6>
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-1"><strong>Name:</strong> {{ selectedTravel.member.first_name }} {{ selectedTravel.member.last_name }}</p>
                  <p class="mb-1"><strong>Member #:</strong> {{ selectedTravel.member.member_number }}</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1"><strong>Chapter:</strong> {{ selectedTravel.member.chapter }}</p>
                </div>
              </div>
            </div>

            <hr>

            <!-- Travel Preferences Section -->
            <div class="travel-preferences-section mb-4">
              <h6 class="fw-bold mb-3">Travel Preferences</h6>
              
              <div class="row mb-3">
                <div class="col-md-12">
                  <p class="mb-1"><strong>Travel Method:</strong> {{ selectedTravel.travel.travel_method_display }}</p>
                  <p class="mb-1"><strong>Seat Preference:</strong> {{ selectedTravel.travel.seat_preference_display }}</p>
                  <p class="mb-1">
                    <strong>Ground Transportation:</strong> 
                    {{ selectedTravel.travel.needs_ground_transportation ? 'Yes' : 'No' }}
                  </p>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="card bg-light">
                    <div class="card-body">
                      <h6 class="card-subtitle mb-2 text-muted">Departure Preferences</h6>
                      <p class="mb-1" v-if="selectedTravel.departure_airport_info">
                        <strong>Airport:</strong><br>
                        {{ selectedTravel.departure_airport_info.code }} - {{ selectedTravel.departure_airport_info.description }}
                      </p>
                      <p class="mb-1"><strong>Date:</strong> {{ formatDate(selectedTravel.travel.departure_date) }}</p>
                      <p class="mb-0">
                        <strong>Time Preference:</strong> 
                        {{ selectedTravel.travel.departure_time_formatted || 'No preference' }}
                      </p>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="card bg-light">
                    <div class="card-body">
                      <h6 class="card-subtitle mb-2 text-muted">Return Preferences</h6>
                      <p class="mb-1" v-if="selectedTravel.return_airport_info">
                        <strong>Airport:</strong><br>
                        {{ selectedTravel.return_airport_info.code }} - {{ selectedTravel.return_airport_info.description }}
                      </p>
                      <p class="mb-1"><strong>Date:</strong> {{ formatDate(selectedTravel.travel.return_date) }}</p>
                      <p class="mb-0">
                        <strong>Time Preference:</strong> 
                        {{ selectedTravel.travel.return_time_formatted || 'No preference' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <hr>

            <!-- Booked Flight Information Form -->
            <div class="booked-flight-section">
              <h6 class="fw-bold mb-3">Booked Flight Information</h6>
              <form @submit.prevent="saveFlightBooking">
                <div class="row mb-4">
                  <div class="col-md-6">
                    <div class="card border-primary">
                      <div class="card-header bg-primary text-white">
                        <strong>Outbound Flight</strong>
                      </div>
                      <div class="card-body">
                        <div class="mb-3">
                          <label class="form-label">Airline *</label>
                          <input 
                            v-model="flightBookingForm.outbound_airline"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.outbound_airline}"
                            placeholder="e.g., Delta"
                            maxlength="100"
                            @blur="validateField('outbound_airline')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.outbound_airline">
                            {{ validationErrors.outbound_airline }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Flight Number *</label>
                          <input 
                            v-model="flightBookingForm.outbound_flight_number"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.outbound_flight_number}"
                            placeholder="e.g., DL1234"
                            maxlength="20"
                            @blur="validateField('outbound_flight_number')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.outbound_flight_number">
                            {{ validationErrors.outbound_flight_number }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Departure Time</label>
                          <input 
                            v-model="flightBookingForm.outbound_departure_time"
                            type="datetime-local" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.outbound_departure_time}"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.outbound_departure_time">
                            {{ validationErrors.outbound_departure_time }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Arrival Time</label>
                          <input 
                            v-model="flightBookingForm.outbound_arrival_time"
                            type="datetime-local" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.outbound_arrival_time}"
                            @blur="validateField('outbound_arrival_time')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.outbound_arrival_time">
                            {{ validationErrors.outbound_arrival_time }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Confirmation Number</label>
                          <input 
                            v-model="flightBookingForm.outbound_confirmation"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.outbound_confirmation}"
                            placeholder="Confirmation #"
                            maxlength="50"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.outbound_confirmation">
                            {{ validationErrors.outbound_confirmation }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="card border-success">
                      <div class="card-header bg-success text-white">
                        <strong>Return Flight</strong>
                      </div>
                      <div class="card-body">
                        <div class="mb-3">
                          <label class="form-label">Airline *</label>
                          <input 
                            v-model="flightBookingForm.return_airline"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.return_airline}"
                            placeholder="e.g., Delta"
                            maxlength="100"
                            @blur="validateField('return_airline')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.return_airline">
                            {{ validationErrors.return_airline }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Flight Number *</label>
                          <input 
                            v-model="flightBookingForm.return_flight_number"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.return_flight_number}"
                            placeholder="e.g., DL5678"
                            maxlength="20"
                            @blur="validateField('return_flight_number')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.return_flight_number">
                            {{ validationErrors.return_flight_number }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Departure Time</label>
                          <input 
                            v-model="flightBookingForm.return_departure_time"
                            type="datetime-local" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.return_departure_time}"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.return_departure_time">
                            {{ validationErrors.return_departure_time }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Arrival Time</label>
                          <input 
                            v-model="flightBookingForm.return_arrival_time"
                            type="datetime-local" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.return_arrival_time}"
                            @blur="validateField('return_arrival_time')"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.return_arrival_time">
                            {{ validationErrors.return_arrival_time }}
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Confirmation Number</label>
                          <input 
                            v-model="flightBookingForm.return_confirmation"
                            type="text" 
                            class="form-control"
                            :class="{'is-invalid': validationErrors.return_confirmation}"
                            placeholder="Confirmation #"
                            maxlength="50"
                          >
                          <div class="invalid-feedback" v-if="validationErrors.return_confirmation">
                            {{ validationErrors.return_confirmation }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label">Flight Notes</label>
                  <textarea 
                    v-model="flightBookingForm.flight_notes"
                    class="form-control"
                    :class="{'is-invalid': validationErrors.flight_notes}"
                    rows="3"
                    placeholder="Additional notes about the booking..."
                    maxlength="1000"
                  ></textarea>
                  <div class="invalid-feedback" v-if="validationErrors.flight_notes">
                    {{ validationErrors.flight_notes }}
                  </div>
                </div>

                <div class="alert alert-info">
                  <i class="bi bi-info-circle"></i>
                  Once you save the flight booking information, it will be visible to the member on their convention dashboard.
                </div>
              </form>
            </div>
          </div>

          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              data-bs-dismiss="modal"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="saveFlightBooking"
              :disabled="savingFlight || !isFlightBookingValid"
            >
              <span v-if="savingFlight">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Saving...
              </span>
              <span v-else>
                <i class="bi bi-check-circle"></i> Save Flight Booking
              </span>
            </button>
          </div>
          
          <!-- Validation warning -->
          <div v-if="!isFlightBookingValid" class="modal-footer bg-warning-subtle">
            <div class="alert alert-warning mb-0 w-100">
              <i class="bi bi-exclamation-triangle"></i>
              Please ensure both outbound and return flights are complete before saving.
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
  name: 'ConventionTravel',
  data() {
    return {
      travels: [],
      selectedTravel: null,
      loading: false,
      error: null,
      searchQuery: '',
      filters: {
        travelMethod: '',
        bookingStatus: ''
      },
      flightBookingForm: {
        outbound_airline: '',
        outbound_flight_number: '',
        outbound_departure_time: '',
        outbound_arrival_time: '',
        outbound_confirmation: '',
        return_airline: '',
        return_flight_number: '',
        return_departure_time: '',
        return_arrival_time: '',
        return_confirmation: '',
        flight_notes: ''
      },
      savingFlight: false,
      validationErrors: {}
    };
  },
  computed: {
    filteredTravels() {
      if (!this.travels) return [];
      
      return this.travels.filter(travel => {
        // Search filter
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase();
          const fullName = `${travel.first_name} ${travel.last_name}`.toLowerCase();
          const chapter = (travel.chapter || '').toLowerCase();
          
          if (!fullName.includes(query) && !chapter.includes(query)) {
            return false;
          }
        }
        
        return true;
      });
    },
    
    isFlightBookingValid() {
      const form = this.flightBookingForm;
      
      // If either flight number is filled, both required
      const hasOutbound = form.outbound_flight_number?.trim();
      const hasReturn = form.return_flight_number?.trim();
      
      if (hasOutbound || hasReturn) {
        // Both flights required
        if (!hasOutbound || !hasReturn) return false;
        
        // Both airlines required
        if (!form.outbound_airline?.trim() || !form.return_airline?.trim()) return false;
        
        // Validate times if provided
        if (form.outbound_departure_time && form.outbound_arrival_time) {
          if (form.outbound_arrival_time <= form.outbound_departure_time) return false;
        }
        
        if (form.return_departure_time && form.return_arrival_time) {
          if (form.return_arrival_time <= form.return_departure_time) return false;
        }
      }
      
      return true;
    }
  },
  mounted() {
    this.loadTravelData();
  },
  methods: {
    async loadTravelData() {
      this.loading = true;
      this.error = null;
      
      try {
        const params = {};
        if (this.filters.travelMethod) {
          params.travel_method = this.filters.travelMethod;
        }
        if (this.filters.bookingStatus) {
          params.booked = this.filters.bookingStatus;
        }
        
        const response = await api.get('/api/convention/admin/travel/', { params });
        this.travels = response.data;
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to load travel data';
        console.error('Error loading travel data:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async openTravelDetail(travelId) {
      try {
        const response = await api.get(`/api/convention/admin/travel/${travelId}/`);
        this.selectedTravel = response.data;
        
        // Populate form with existing booking data
        const travel = response.data.travel;
        this.flightBookingForm = {
          outbound_airline: travel.outbound_airline || '',
          outbound_flight_number: travel.outbound_flight_number || '',
          outbound_departure_time: this.formatDateTimeForInput(travel.outbound_departure_time),
          outbound_arrival_time: this.formatDateTimeForInput(travel.outbound_arrival_time),
          outbound_confirmation: travel.outbound_confirmation || '',
          return_airline: travel.return_airline || '',
          return_flight_number: travel.return_flight_number || '',
          return_departure_time: this.formatDateTimeForInput(travel.return_departure_time),
          return_arrival_time: this.formatDateTimeForInput(travel.return_arrival_time),
          return_confirmation: travel.return_confirmation || '',
          flight_notes: travel.flight_notes || ''
        };
        
        // Show Bootstrap modal
        this.$nextTick(() => {
          const modalElement = document.getElementById('travelDetailModal');
          const modal = new bootstrap.Modal(modalElement);
          modal.show();
        });
      } catch (err) {
        alert('Failed to load travel details: ' + (err.response?.data?.message || err.message));
        console.error('Error loading travel detail:', err);
      }
    },
    
    async saveFlightBooking() {
      if (!this.selectedTravel) return;
      
      // Clear previous errors
      this.validationErrors = {};
      
      // Validate before submitting
      if (!this.isFlightBookingValid) {
        alert('Please correct validation errors before saving');
        return;
      }
      
      this.savingFlight = true;
      
      try {
        // Trim and normalize all fields
        const payload = {
          outbound_airline: this.flightBookingForm.outbound_airline?.trim() || '',
          outbound_flight_number: this.flightBookingForm.outbound_flight_number?.trim().toUpperCase() || '',
          outbound_departure_time: this.flightBookingForm.outbound_departure_time || null,
          outbound_arrival_time: this.flightBookingForm.outbound_arrival_time || null,
          outbound_confirmation: this.flightBookingForm.outbound_confirmation?.trim().toUpperCase() || '',
          return_airline: this.flightBookingForm.return_airline?.trim() || '',
          return_flight_number: this.flightBookingForm.return_flight_number?.trim().toUpperCase() || '',
          return_departure_time: this.flightBookingForm.return_departure_time || null,
          return_arrival_time: this.flightBookingForm.return_arrival_time || null,
          return_confirmation: this.flightBookingForm.return_confirmation?.trim().toUpperCase() || '',
          flight_notes: this.flightBookingForm.flight_notes?.trim() || '',
        };
        
        await api.put(`/api/convention/admin/travel/${this.selectedTravel.id}/`, payload);
        
        // Reload the travel list to reflect changes
        await this.loadTravelData();
        
        // Close Bootstrap modal
        const modalElement = document.getElementById('travelDetailModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
          modal.hide();
        }
        
        // Clear selected travel
        this.selectedTravel = null;
        
        // Show success message
        alert('Flight booking saved successfully!');
      } catch (err) {
        // Handle validation errors from backend
        if (err.response?.data && typeof err.response.data === 'object') {
          this.validationErrors = err.response.data;
          
          // Build error message
          const errorMessages = Object.entries(err.response.data)
            .map(([field, msgs]) => {
              const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
              const messages = Array.isArray(msgs) ? msgs.join(', ') : msgs;
              return `${fieldName}: ${messages}`;
            })
            .join('\n');
          
          alert('Validation errors:\n\n' + errorMessages);
        } else {
          alert('Failed to save flight booking: ' + (err.response?.data?.message || err.message));
        }
        console.error('Error saving flight booking:', err);
      } finally {
        this.savingFlight = false;
      }
    },
    
    validateField(fieldName) {
      // Clear previous error for this field
      this.validationErrors = { ...this.validationErrors };
      delete this.validationErrors[fieldName];
      
      const form = this.flightBookingForm;
      
      // Validate based on field
      if (fieldName === 'outbound_airline' || fieldName === 'return_airline') {
        const hasOutbound = form.outbound_flight_number?.trim();
        const hasReturn = form.return_flight_number?.trim();
        
        if ((hasOutbound || hasReturn) && !form[fieldName]?.trim()) {
          this.validationErrors[fieldName] = 'Airline is required when booking flights';
        }
      }
      
      if (fieldName === 'outbound_flight_number' || fieldName === 'return_flight_number') {
        const hasOutbound = form.outbound_flight_number?.trim();
        const hasReturn = form.return_flight_number?.trim();
        
        if (hasOutbound && !hasReturn) {
          this.validationErrors.return_flight_number = 'Both outbound and return flights required';
        } else if (hasReturn && !hasOutbound) {
          this.validationErrors.outbound_flight_number = 'Both outbound and return flights required';
        }
      }
      
      if (fieldName === 'outbound_arrival_time') {
        if (form.outbound_departure_time && form.outbound_arrival_time) {
          if (form.outbound_arrival_time <= form.outbound_departure_time) {
            this.validationErrors.outbound_arrival_time = 'Arrival must be after departure';
          }
        }
      }
      
      if (fieldName === 'return_arrival_time') {
        if (form.return_departure_time && form.return_arrival_time) {
          if (form.return_arrival_time <= form.return_departure_time) {
            this.validationErrors.return_arrival_time = 'Arrival must be after departure';
          }
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    },
    
    formatDateTimeForInput(dateTimeString) {
      if (!dateTimeString) return '';
      // Convert ISO datetime to datetime-local format (YYYY-MM-DDTHH:mm)
      const date = new Date(dateTimeString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    
    getTravelMethodClass(method) {
      const classes = {
        'need_booking': 'bg-warning',
        'self_booking': 'bg-info',
        'driving': 'bg-secondary'
      };
      return classes[method] || 'bg-secondary';
    }
  }
};
</script>

<style scoped>
.convention-travel-admin {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.filters-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.travel-list .card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.modal-lg {
  max-width: 900px;
}

.member-info-section,
.travel-preferences-section,
.booked-flight-section {
  padding: 1rem 0;
}

.card.bg-light {
  border: 1px solid #e9ecef;
}

.card.border-primary {
  border-width: 2px;
}

.card.border-success {
  border-width: 2px;
}

@media (max-width: 768px) {
  .convention-travel-admin {
    padding: 1rem;
  }
  
  .table-responsive {
    font-size: 0.875rem;
  }
}
</style>
