<template>
  <div class="container-fluid py-4">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col">
        <h1 class="h2">Convention Registration</h1>
        <p v-if="convention" class="text-muted mb-0">
          {{ convention.name }} - {{ convention.year }} | {{ convention.location }}
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading convention information...</p>
    </div>

    <!-- No Convention -->
    <div v-else-if="!convention" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      No active convention found at this time.
    </div>

    <!-- Main Content -->
    <div v-else-if="registration">
      <!-- Personal Information Section -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0"><i class="bi bi-person-badge me-2"></i>Personal Information</h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveMemberInfo">
            <div class="alert alert-info">
              <small><i class="bi bi-info-circle me-2"></i>
                Your badge will display: <strong>{{ memberInfo.badge_name }}</strong>
              </small>
            </div>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Legal First Name</label>
                <input 
                  :value="memberInfo.first_name" 
                  type="text" 
                  class="form-control"
                  disabled
                >
                <small class="text-muted">From your member record</small>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Preferred First Name (for badge)</label>
                <input 
                  v-model="memberInfo.preferred_first_name" 
                  type="text" 
                  class="form-control"
                  placeholder="Leave blank to use legal first name"
                >
                <small class="text-muted">Optional - only if you prefer a different name</small>
              </div>
            </div>
            
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else><i class="bi bi-save me-2"></i>Save Badge Name</span>
            </button>
          </form>

          <hr class="my-4">

          <!-- Primary Phone -->
          <h6>Primary Contact Phone</h6>
          <div v-if="memberPhones.length > 0" class="mb-3">
            <div v-for="phone in memberPhones" :key="phone.id" class="form-check">
              <input 
                class="form-check-input" 
                type="radio" 
                :id="'phone-' + phone.id"
                :checked="phone.is_primary"
                @change="setPrimaryPhone(phone.id)"
              >
              <label class="form-check-label" :for="'phone-' + phone.id">
                {{ phone.phone_type }}: {{ phone.formatted_number }}
                <span v-if="phone.is_primary" class="badge bg-success ms-2">Primary</span>
              </label>
            </div>
            <router-link :to="{ name: 'account' }" class="btn btn-sm btn-link mt-2">
              <i class="bi bi-pencil me-1"></i>Manage Phone Numbers
            </router-link>
          </div>
          <div v-else class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            No phone numbers on file. 
            <router-link :to="{ name: 'account' }">Add a phone number</router-link>
          </div>

          <hr class="my-3">

          <!-- Primary Address -->
          <h6>Primary Mailing Address</h6>
          <div v-if="memberAddresses.length > 0" class="mb-3">
            <div v-for="address in memberAddresses" :key="address.id" class="form-check mb-2">
              <input 
                class="form-check-input" 
                type="radio" 
                :id="'address-' + address.id"
                :checked="address.is_primary"
                @change="setPrimaryAddress(address.id)"
              >
              <label class="form-check-label" :for="'address-' + address.id">
                <strong>{{ address.add_type }}:</strong>
                {{ address.add_line1 }}<span v-if="address.add_line2">, {{ address.add_line2 }}</span>,
                {{ address.add_city }}, {{ address.add_state }} {{ address.add_zip }}
                <span v-if="address.is_primary" class="badge bg-success ms-2">Primary</span>
              </label>
            </div>
            <router-link :to="{ name: 'account' }" class="btn btn-sm btn-link mt-2">
              <i class="bi bi-pencil me-1"></i>Manage Addresses
            </router-link>
          </div>
          <div v-else class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            No addresses on file. 
            <router-link :to="{ name: 'account' }">Add an address</router-link>
          </div>
        </div>
      </div>

      <!-- Committee Preferences Section -->
      <div class="card mb-4">
        <div class="card-header bg-success text-white">
          <h5 class="mb-0"><i class="bi bi-people me-2"></i>Committee Preferences</h5>
        </div>
        <div class="card-body">
          <p class="text-muted">Please indicate your interest level for each committee:</p>
          <form @submit.prevent="saveCommitteePreferences">
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Committee</th>
                    <th class="text-center">No Interest</th>
                    <th class="text-center">Interested</th>
                    <th class="text-center">Prefer</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="committee in committees" :key="committee.field">
                    <td>{{ committee.label }}</td>
                    <td class="text-center">
                      <input 
                        type="radio" 
                        :name="committee.field" 
                        :value="0" 
                        v-model.number="committeePreferences[committee.field]"
                        class="form-check-input"
                      >
                    </td>
                    <td class="text-center">
                      <input 
                        type="radio" 
                        :name="committee.field" 
                        :value="1" 
                        v-model.number="committeePreferences[committee.field]"
                        class="form-check-input"
                      >
                    </td>
                    <td class="text-center">
                      <input 
                        type="radio" 
                        :name="committee.field" 
                        :value="2" 
                        v-model.number="committeePreferences[committee.field]"
                        class="form-check-input"
                      >
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <button type="submit" class="btn btn-success" :disabled="saving">
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else><i class="bi bi-save me-2"></i>Save Committee Preferences</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Guest Section -->
      <div class="card mb-4">
        <div class="card-header bg-info text-white">
          <h5 class="mb-0"><i class="bi bi-person-plus me-2"></i>Guest Information</h5>
        </div>
        <div class="card-body">
          <div class="form-check mb-3">
            <input 
              v-model="bringingGuest" 
              class="form-check-input" 
              type="checkbox" 
              id="bringingGuest"
            >
            <label class="form-check-label" for="bringingGuest">
              I will be bringing a guest
            </label>
          </div>

          <div v-if="bringingGuest">
            <!-- Existing Guests -->
            <div v-if="guests.length > 0" class="mb-3">
              <h6>Registered Guests:</h6>
              <div v-for="guest in guests" :key="guest.id" class="border rounded p-3 mb-2">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <strong>{{ guest.guest_first_name }} {{ guest.guest_last_name }}</strong>
                    <div class="text-muted small">
                      <div v-if="guest.guest_email">Email: {{ guest.guest_email }}</div>
                      <div v-if="guest.guest_phone">Phone: {{ guest.guest_phone }}</div>
                      <div v-if="guest.guest_dietary_restrictions">
                        Dietary: {{ guest.guest_dietary_restrictions }}
                      </div>
                    </div>
                  </div>
                  <button 
                    @click="removeGuest(guest.id)" 
                    class="btn btn-sm btn-outline-danger"
                    :disabled="saving"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Add New Guest Form -->
            <div class="border rounded p-3 bg-light">
              <h6>Add Guest</h6>
              <form @submit.prevent="addGuest">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">First Name *</label>
                    <input 
                      v-model="newGuest.guest_first_name" 
                      type="text" 
                      class="form-control"
                      required
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Last Name *</label>
                    <input 
                      v-model="newGuest.guest_last_name" 
                      type="text" 
                      class="form-control"
                      required
                    >
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Email</label>
                    <input 
                      v-model="newGuest.guest_email" 
                      type="email" 
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Phone</label>
                    <input 
                      v-model="newGuest.guest_phone" 
                      type="tel" 
                      class="form-control"
                    >
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Dietary Restrictions</label>
                  <textarea 
                    v-model="newGuest.guest_dietary_restrictions" 
                    class="form-control"
                    rows="2"
                  ></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Special Requests</label>
                  <textarea 
                    v-model="newGuest.guest_special_requests" 
                    class="form-control"
                    rows="2"
                  ></textarea>
                </div>
                <button type="submit" class="btn btn-info" :disabled="saving">
                  <span v-if="saving">
                    <span class="spinner-border spinner-border-sm me-2"></span>Adding...
                  </span>
                  <span v-else><i class="bi bi-plus-circle me-2"></i>Add Guest</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Travel Section -->
      <div class="card mb-4">
        <div class="card-header bg-warning text-dark">
          <h5 class="mb-0"><i class="bi bi-airplane me-2"></i>Travel Information</h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveTravel">
            <div class="mb-3">
              <label class="form-label">Travel Method</label>
              <div class="form-check">
                <input 
                  v-model="travel.travel_method" 
                  class="form-check-input" 
                  type="radio" 
                  value="driving"
                  id="driving"
                >
                <label class="form-check-label" for="driving">
                  I will be driving
                </label>
              </div>
              <div class="form-check">
                <input 
                  v-model="travel.travel_method" 
                  class="form-check-input" 
                  type="radio" 
                  value="self_booking"
                  id="self_booking"
                >
                <label class="form-check-label" for="self_booking">
                  I will book my own flight
                </label>
              </div>
              <div class="form-check">
                <input 
                  v-model="travel.travel_method" 
                  class="form-check-input" 
                  type="radio" 
                  value="need_booking"
                  id="need_booking"
                >
                <label class="form-check-label" for="need_booking">
                  I need TBP to book my flight
                </label>
              </div>
            </div>

            <!-- Flight Request Information (if need_booking) -->
            <div v-if="travel.travel_method === 'need_booking'" class="border rounded p-3 mb-3">
              <h6>Flight Request Details</h6>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Departure Airport Code</label>
                  <input 
                    v-model="travel.departure_airport" 
                    type="text" 
                    class="form-control"
                    placeholder="e.g., JFK"
                    maxlength="10"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Preferred Departure Date</label>
                  <input 
                    v-model="travel.departure_date" 
                    type="date" 
                    class="form-control"
                  >
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Departure Time Preference</label>
                <input 
                  v-model="travel.departure_time_preference" 
                  type="text" 
                  class="form-control"
                  placeholder="e.g., Morning, Afternoon, Evening"
                >
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Return Airport Code</label>
                  <input 
                    v-model="travel.return_airport" 
                    type="text" 
                    class="form-control"
                    placeholder="e.g., JFK"
                    maxlength="10"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Preferred Return Date</label>
                  <input 
                    v-model="travel.return_date" 
                    type="date" 
                    class="form-control"
                  >
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Return Time Preference</label>
                <input 
                  v-model="travel.return_time_preference" 
                  type="text" 
                  class="form-control"
                  placeholder="e.g., Morning, Afternoon, Evening"
                >
              </div>
            </div>

            <!-- Booked Flight Information (if staff has booked) -->
            <div v-if="travel.has_booked_flight" class="alert alert-success">
              <h6><i class="bi bi-check-circle me-2"></i>Your Flight Has Been Booked!</h6>
              <div class="row mt-3">
                <div class="col-md-6">
                  <strong>Outbound Flight:</strong>
                  <div>{{ travel.outbound_airline }} {{ travel.outbound_flight_number }}</div>
                  <div>Departure: {{ formatDateTime(travel.outbound_departure_time) }}</div>
                  <div>Arrival: {{ formatDateTime(travel.outbound_arrival_time) }}</div>
                  <div>Confirmation: {{ travel.outbound_confirmation }}</div>
                </div>
                <div class="col-md-6">
                  <strong>Return Flight:</strong>
                  <div>{{ travel.return_airline }} {{ travel.return_flight_number }}</div>
                  <div>Departure: {{ formatDateTime(travel.return_departure_time) }}</div>
                  <div>Arrival: {{ formatDateTime(travel.return_arrival_time) }}</div>
                  <div>Confirmation: {{ travel.return_confirmation }}</div>
                </div>
              </div>
            </div>

            <button type="submit" class="btn btn-warning" :disabled="saving">
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else><i class="bi bi-save me-2"></i>Save Travel Info</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Hotel and Package Section -->
      <div class="card mb-4">
        <div class="card-header bg-danger text-white">
          <h5 class="mb-0"><i class="bi bi-building me-2"></i>Hotel & Package Selection</h5>
        </div>
        <div class="card-body">
          <form @submit.prevent="saveAccommodation">
            <div class="mb-3">
              <label class="form-label">Package Selection</label>
              <select v-model="accommodation.package_choice" class="form-select">
                <option value="full">Full Package - All meals and events</option>
                <option value="partial">Partial Package - Select meals</option>
                <option value="commuter">Commuter Package - No hotel</option>
                <option value="custom">Custom Package</option>
              </select>
            </div>

            <div class="form-check mb-3">
              <input 
                v-model="accommodation.needs_hotel" 
                class="form-check-input" 
                type="checkbox" 
                id="needsHotel"
              >
              <label class="form-check-label" for="needsHotel">
                I need hotel accommodations
              </label>
            </div>

            <div v-if="accommodation.needs_hotel">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Check-in Date</label>
                  <input 
                    v-model="accommodation.check_in_date" 
                    type="date" 
                    class="form-control"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Check-out Date</label>
                  <input 
                    v-model="accommodation.check_out_date" 
                    type="date" 
                    class="form-control"
                  >
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Roommate Preference</label>
                <select v-model="accommodation.roommate_preference" class="form-select">
                  <option value="single">I prefer a single room</option>
                  <option value="specific">I have a specific roommate in mind</option>
                  <option value="any">Any roommate is fine</option>
                </select>
              </div>

              <div v-if="accommodation.roommate_preference === 'specific'" class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Roommate Name</label>
                  <input 
                    v-model="accommodation.specific_roommate_name" 
                    type="text" 
                    class="form-control"
                    placeholder="First and Last Name"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Roommate Chapter</label>
                  <input 
                    v-model="accommodation.specific_roommate_chapter" 
                    type="text" 
                    class="form-control"
                    placeholder="Chapter name"
                  >
                </div>
              </div>

              <!-- Room Assignment (if assigned) -->
              <div v-if="accommodation.has_room_assignment" class="alert alert-info">
                <h6><i class="bi bi-door-open me-2"></i>Your Room Has Been Assigned!</h6>
                <div>Room Number: <strong>{{ accommodation.room_number }}</strong></div>
                <div v-if="accommodation.room_confirmation">
                  Confirmation: {{ accommodation.room_confirmation }}
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Food Allergies</label>
              <textarea 
                v-model="accommodation.food_allergies" 
                class="form-control"
                rows="2"
                placeholder="List any food allergies"
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Dietary Restrictions</label>
              <textarea 
                v-model="accommodation.dietary_restrictions" 
                class="form-control"
                rows="2"
                placeholder="Vegetarian, vegan, gluten-free, etc."
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Other Allergies or Medical Concerns</label>
              <textarea 
                v-model="accommodation.other_allergies" 
                class="form-control"
                rows="2"
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Special Requests</label>
              <textarea 
                v-model="accommodation.special_requests" 
                class="form-control"
                rows="3"
                placeholder="Any other special requests or needs"
              ></textarea>
            </div>

            <button type="submit" class="btn btn-danger" :disabled="saving">
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>Saving...
              </span>
              <span v-else><i class="bi bi-save me-2"></i>Save Accommodation Info</span>
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- No Registration Yet -->
    <div v-else-if="!loading && convention && !registration">
      <div class="card">
        <div class="card-body text-center py-5">
          <i class="bi bi-clipboard-check display-1 text-muted mb-3"></i>
          <h3>You haven't registered yet</h3>
          <p class="text-muted mb-4">Click below to begin your registration for {{ convention.name }}</p>
          <button @click="createRegistration" class="btn btn-primary btn-lg" :disabled="saving">
            <span v-if="saving">
              <span class="spinner-border spinner-border-sm me-2"></span>Creating Registration...
            </span>
            <span v-else><i class="bi bi-plus-circle me-2"></i>Start Registration</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { useToast } from 'vue-toastification'
import api from '../../api'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// State
const loading = ref(true)
const saving = ref(false)
const convention = ref(null)
const registration = ref(null)

// Member Info (from Member model)
const memberInfo = ref({
  first_name: '',
  last_name: '',
  preferred_first_name: '',
  badge_name: '',
  chapter: ''
})

const memberAddresses = ref([])
const memberPhones = ref([])

// Committee Preferences
const committees = [
  { field: 'advisors', label: 'Advisors' },
  { field: 'alumni_chapters', label: 'Alumni Chapters' },
  { field: 'awards', label: 'Awards' },
  { field: 'chapter_association_finance', label: 'Chapter & Association Finance' },
  { field: 'constitution_bylaws', label: 'Constitution & Bylaws' },
  { field: 'convention_site', label: ' Convention Site' },
  { field: 'diversity_equity_inclusion', label: 'Diversity Equity and Inclusion' },
  { field: 'nest', label: 'NEST' },
  { field: 'petitions', label: 'Petitions' },
  { field: 'program_review', label: 'Program Review' },
  { field: 'public_relations', label: 'Public Relations' },
  { field: 'resolutions', label: 'Resolutions' },
  { field: 'rituals', label: 'Rituals' }
]

const committeePreferences = ref({
  alumni_affairs: 0,
  awards: 0,
  chapter_operations: 0,
  collegiate_chapters: 0,
  communications: 0,
  constitution: 0,
  engineering_futures: 0,
  membership: 0
})

// Guests
const bringingGuest = ref(false)
const guests = ref([])
const newGuest = ref({
  guest_first_name: '',
  guest_last_name: '',
  guest_email: '',
  guest_phone: '',
  guest_dietary_restrictions: '',
  guest_special_requests: ''
})

// Travel
const travel = ref({
  travel_method: 'need_booking',
  departure_airport: '',
  departure_date: '',
  departure_time_preference: '',
  return_airport: '',
  return_date: '',
  return_time_preference: '',
  has_booked_flight: false
})

// Accommodation
const accommodation = ref({
  package_choice: 'full',
  needs_hotel: true,
  check_in_date: '',
  check_out_date: '',
  roommate_preference: 'any',
  specific_roommate_name: '',
  specific_roommate_chapter: '',
  food_allergies: '',
  dietary_restrictions: '',
  other_allergies: '',
  special_requests: '',
  has_room_assignment: false
})

// Methods
const fetchConvention = async () => {
  try {
    const response = await api.get('/api/convention/current/')
    convention.value = response.data
  } catch (error) {
    console.error('Error fetching convention:', error)
    if (error.response?.status !== 404) {
      toast.error('Failed to load convention information')
    }
  }
}

const fetchRegistration = async () => {
  try {
    const response = await api.get('/api/convention/my-registration/')
    if (response.data.has_registration === false) {
      registration.value = null
    } else {
      registration.value = response.data
      loadRegistrationData(response.data)
    }
  } catch (error) {
    console.error('Error fetching registration:', error)
    registration.value = null
  }
}

const loadRegistrationData = (data) => {
  // Load member info
  if (data.member_info) {
    memberInfo.value = { ...data.member_info }
  }

  // Load addresses and phones
  if (data.member_addresses) {
    memberAddresses.value = data.member_addresses
  }
  if (data.member_phones) {
    memberPhones.value = data.member_phones
  }

  // Load committee preferences
  if (data.committee_preferences) {
    committeePreferences.value = { ...data.committee_preferences }
  }

  // Load guests
  if (data.guest_details && data.guest_details.length > 0) {
    guests.value = data.guest_details
    bringingGuest.value = true
  }

  // Load travel
  if (data.travel) {
    travel.value = { ...data.travel }
  }

  // Load accommodation
  if (data.accommodation) {
    accommodation.value = { ...data.accommodation }
  }
}

const createRegistration = async () => {
  saving.value = true
  try {
    const response = await api.post('/api/convention/my-registration/')
    registration.value = response.data
    loadRegistrationData(response.data)
    toast.success('Registration created successfully!')
  } catch (error) {
    console.error('Error creating registration:', error)
    toast.error(error.response?.data?.message || 'Failed to create registration')
  } finally {
    saving.value = false
  }
}

const saveMemberInfo = async () => {
  saving.value = true
  try {
    await api.put('/api/convention/member/update-info/', {
      preferred_first_name: memberInfo.value.preferred_first_name
    })
    toast.success('Badge name saved!')
    
    // Refresh registration to get updated badge_name
    await fetchRegistration()
  } catch (error) {
    console.error('Error saving member info:', error)
    toast.error('Failed to save badge name')
  } finally {
    saving.value = false
  }
}

const setPrimaryAddress = async (addressId) => {
  saving.value = true
  try {
    await api.put(`/api/convention/member/address/${addressId}/set-primary/`)
    toast.success('Primary address updated!')
    
    // Update local state
    memberAddresses.value.forEach(addr => {
      addr.is_primary = addr.id === addressId
    })
  } catch (error) {
    console.error('Error setting primary address:', error)
    toast.error('Failed to update primary address')
  } finally {
    saving.value = false
  }
}

const setPrimaryPhone = async (phoneId) => {
  saving.value = true
  try {
    await api.put(`/api/convention/member/phone/${phoneId}/set-primary/`)
    toast.success('Primary phone updated!')
    
    // Update local state
    memberPhones.value.forEach(phone => {
      phone.is_primary = phone.id === phoneId
    })
  } catch (error) {
    console.error('Error setting primary phone:', error)
    toast.error('Failed to update primary phone')
  } finally {
    saving.value = false
  }
}

const saveCommitteePreferences = async () => {
  saving.value = true
  try {
    await api.put(
      `/api/convention/registration/${registration.value.id}/committee-preferences/`,
      committeePreferences.value
    )
    toast.success('Committee preferences saved!')
  } catch (error) {
    console.error('Error saving committee preferences:', error)
    toast.error('Failed to save committee preferences')
  } finally {
    saving.value = false
  }
}

const addGuest = async () => {
  saving.value = true
  try {
    const response = await api.post(
      `/api/convention/registration/${registration.value.id}/guests/`,
      newGuest.value
    )
    guests.value.push(response.data)
    // Reset form
    newGuest.value = {
      guest_first_name: '',
      guest_last_name: '',
      guest_email: '',
      guest_phone: '',
      guest_dietary_restrictions: '',
      guest_special_requests: ''
    }
    toast.success('Guest added successfully!')
  } catch (error) {
    console.error('Error adding guest:', error)
    toast.error('Failed to add guest')
  } finally {
    saving.value = false
  }
}

const removeGuest = async (guestId) => {
  if (!confirm('Are you sure you want to remove this guest?')) return
  
  saving.value = true
  try {
    await api.delete(
      `/api/convention/registration/${registration.value.id}/guests/${guestId}/`
    )
    guests.value = guests.value.filter(g => g.id !== guestId)
    toast.success('Guest removed successfully!')
  } catch (error) {
    console.error('Error removing guest:', error)
    toast.error('Failed to remove guest')
  } finally {
    saving.value = false
  }
}

const saveTravel = async () => {
  saving.value = true
  try {
    await api.put(
      `/api/convention/registration/${registration.value.id}/travel/`,
      travel.value
    )
    toast.success('Travel information saved!')
  } catch (error) {
    console.error('Error saving travel:', error)
    toast.error('Failed to save travel information')
  } finally {
    saving.value = false
  }
}

const saveAccommodation = async () => {
  saving.value = true
  try {
    await api.put(
      `/api/convention/registration/${registration.value.id}/accommodation/`,
      accommodation.value
    )
    toast.success('Accommodation information saved!')
  } catch (error) {
    console.error('Error saving accommodation:', error)
    toast.error('Failed to save accommodation information')
  } finally {
    saving.value = false
  }
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    await fetchConvention()
    if (convention.value) {
      await fetchRegistration()
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.card-header {
  font-weight: 600;
}

.table th {
  background-color: #f8f9fa;
}

.form-label {
  font-weight: 500;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}
</style>
