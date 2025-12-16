<template>
    <div>

  <!-- Page Header -->
  <div class="page-header">
    <div class="page-header-content">
      <h1 class="page-title">Convention Registration</h1>
      <p v-if="convention" class="page-subtitle">
        {{ convention.year }} | {{ convention.location }}
      </p>
      <p v-else class="page-subtitle">Loading convention information...</p>
      
      <!-- Progress Section -->
      <div v-if="registration" class="progress-section">
        <div class="progress-header">
          <span class="progress-label">Registration Progress</span>
          <span class="progress-percentage">{{ completionPercentage }}% Complete</span>
        </div>
        <div class="progress-bar-wrapper">
          <div class="progress-bar-fill" :style="{ width: completionPercentage + '%' }"></div>
        </div>
        
        <!-- Section Status Cards -->
        <div class="section-status-grid">
          <a 
            v-for="section in sections" 
            :key="section.id"
            :href="'#' + section.id"
            class="status-card"
            :class="{ 'complete': section.isComplete, 'incomplete': !section.isComplete }"
            @click.prevent="scrollToSection(section.id)"
          >
            <div class="status-icon">
              <i v-if="section.isComplete" class="bi bi-check-circle-fill"></i>
              <i v-else class="bi bi-circle"></i>
            </div>
            <div class="status-content">
              <div class="status-title">{{ section.title }}</div>
              <div class="status-label">
                <span v-if="section.isComplete" class="badge-complete">Complete</span>
                <span v-else class="badge-pending">Pending</span>
              </div>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div class="content-container">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading convention information...</p>
    </div>

    <!-- No Convention -->
    <div v-else-if="!convention" class="section-card">
      <div class="alert alert-warning" style="border-left: 4px solid #f59e0b;">
        <i class="bi bi-exclamation-triangle me-2"></i>
        No active convention found at this time.
      </div>
    </div>

    <!-- Registration Not Started -->
    <div v-else-if="!registration" class="section-card text-center py-5">
      <i class="bi bi-calendar-event" style="font-size: 4rem; color: var(--brand-blue); opacity: 0.3;"></i>
      <h3 class="mt-4">Start Your Convention Registration</h3>
      <p class="text-muted">Click below to begin your registration for {{ convention.name }}</p>
      <button @click="createRegistration" class="btn btn-primary mt-3" :disabled="saving">
        <i class="bi bi-plus-circle me-2"></i>
        <span v-if="saving">Creating...</span>
        <span v-else>Start Registration</span>
      </button>
    </div>

    <!-- Main Registration Content -->
    <div v-else>
      <!-- Personal Information Section -->
      <div id="personal-info" class="section-card scroll-target">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-person-badge"></i>
            </div>
            Personal Information
          </h2>
          <span class="status-badge" :class="isPersonalInfoComplete ? 'status-complete' : 'status-pending'">
            {{ isPersonalInfoComplete ? 'Complete' : 'Pending' }}
          </span>
        </div>

        <form @submit.prevent="saveMemberInfo">
          <div class="info-alert">
            <i class="bi bi-info-circle-fill"></i>
            <div class="info-alert-content">
              Your badge will display: <strong>{{ memberInfo.badge_name }}</strong>
            </div>
          </div>
          
          <div class="row g-4">
            <div class="col-md-6">
              <label class="form-label">Legal First Name</label>
              <input 
                :value="memberInfo.first_name" 
                type="text" 
                class="form-control"
                disabled
              >
              <small class="form-text">From your member record</small>
            </div>
            <div class="col-md-6">
              <label class="form-label">Preferred First Name (for badge)</label>
              <input 
                v-model="memberInfo.preferred_first_name" 
                type="text" 
                class="form-control"
                placeholder="Leave blank to use legal first name"
              >
              <small class="form-text">Optional - only if you prefer a different name</small>
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary mt-4" :disabled="saving">
            <span v-if="saving">
              <span class="spinner-border spinner-border-sm me-2"></span>Saving...
            </span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Badge Name</span>
          </button>
        </form>

        <hr class="my-4" style="border-color: #e2e8f0;">

        <!-- Primary Phone -->
        <h6 style="font-weight: 600; margin-bottom: 1rem; color: #1a202c;">Primary Contact Phone</h6>
        <div v-if="memberPhones.length > 0" class="mb-3">
          <div v-for="phone in memberPhones" :key="phone.id" class="form-check mb-2" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <input 
              class="form-check-input" 
              type="radio" 
              :id="'phone-' + phone.id"
              :checked="phone.is_primary"
              @change="setPrimaryPhone(phone.id)"
            >
            <label class="form-check-label" :for="'phone-' + phone.id" style="font-weight: 500;">
              {{ phone.phone_type }}: {{ phone.formatted_number }}
              <span v-if="phone.is_primary" class="badge" style="background: #10b981; color: white; margin-left: 0.5rem;">Primary</span>
            </label>
          </div>
          <router-link :to="{ name: 'account' }" class="btn btn-outline-custom btn-sm mt-2">
            <i class="bi bi-pencil me-1"></i>Manage Phone Numbers
          </router-link>
        </div>
        <div v-else class="alert alert-warning" style="border-left: 4px solid #f59e0b;">
          <i class="bi bi-exclamation-triangle me-2"></i>
          No phone numbers on file. 
          <router-link :to="{ name: 'account' }">Add a phone number</router-link>
        </div>

        <hr class="my-4" style="border-color: #e2e8f0;">

        <!-- Primary Address -->
        <h6 style="font-weight: 600; margin-bottom: 1rem; color: #1a202c;">Primary Mailing Address</h6>
        <p class="text-danger fw-bold">&ast; This address will be used for the mailing of reimbursement checks, so please ensure it is accurate.</p>
        <div v-if="memberAddresses.length > 0" class="mb-3">
          <div v-for="address in memberAddresses" :key="address.id" class="form-check mb-2" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <input 
              class="form-check-input" 
              type="radio" 
              :id="'address-' + address.id"
              :checked="address.is_primary"
              @change="setPrimaryAddress(address.id)"
            >
            <label class="form-check-label" :for="'address-' + address.id" style="font-weight: 500;">
              <strong>{{ address.add_type }}:</strong>
              {{ address.add_line1 }}<span v-if="address.add_line2">, {{ address.add_line2 }}</span>,
              {{ address.add_city }}, {{ address.add_state }} {{ address.add_zip }}
              <span v-if="address.is_primary" class="badge" style="background: #10b981; color: white; margin-left: 0.5rem;">Primary</span>
            </label>
          </div>
          <router-link :to="{ name: 'account' }" class="btn btn-outline-custom btn-sm mt-2">
            <i class="bi bi-pencil me-1"></i>Manage Addresses
          </router-link>
        </div>
        <div v-else class="alert alert-warning" style="border-left: 4px solid #f59e0b;">
          <i class="bi bi-exclamation-triangle me-2"></i>
          No addresses on file. 
          <router-link :to="{ name: 'account' }">Add an address</router-link>
        </div>
      </div>

      <!-- Committee Preferences Section -->
      <div id="committee-prefs" class="section-card scroll-target">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon gold">
              <i class="bi bi-people"></i>
            </div>
            Committee Preferences
          </h2>
          <span class="status-badge" :class="isCommitteePrefsComplete ? 'status-complete' : 'status-pending'">
            {{ isCommitteePrefsComplete ? 'Complete' : 'Pending' }}
          </span>
        </div>

        <p style="color: #64748b; margin-bottom: 1.5rem;">Please indicate your committee preference. If you agree to serve on a committee, you <strong>must</strong> select a level of interest in at least one committee. A summary of committee business is available <a href="#">here</a>. </p>
        
        <form @submit.prevent="saveCommitteePreferences">
          <div class="table-responsive">
            <table class="table table-custom">
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
                  <td style="font-weight: 500;">{{ committee.label }}</td>
                  <td class="text-center">
                    <input 
                      type="radio" 
                      :name="committee.field" 
                      :value="0" 
                      v-model.number="committeePreferences[committee.field]"
                      class="form-check-input"
                      style="width: 1.25rem; height: 1.25rem; cursor: pointer;"
                    >
                  </td>
                  <td class="text-center">
                    <input 
                      type="radio" 
                      :name="committee.field" 
                      :value="1" 
                      v-model.number="committeePreferences[committee.field]"
                      class="form-check-input"
                      style="width: 1.25rem; height: 1.25rem; cursor: pointer;"
                    >
                  </td>
                  <td class="text-center">
                    <input 
                      type="radio" 
                      :name="committee.field" 
                      :value="2" 
                      v-model.number="committeePreferences[committee.field]"
                      class="form-check-input"
                      style="width: 1.25rem; height: 1.25rem; cursor: pointer;"
                    >
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <button type="submit" class="btn btn-gold mt-3" :disabled="saving">
            <span v-if="saving">
              <span class="spinner-border spinner-border-sm me-2"></span>Saving...
            </span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Preferences</span>
          </button>
        </form>
      </div>

      <!-- Guest Section -->
      <div id="guest-info" class="section-card scroll-target">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-person-plus"></i>
            </div>
            Guest Information
          </h2>
          <button v-if="bringingGuest" @click="bringingGuest = true" class="btn btn-gold btn-sm">
            <i class="bi bi-plus-lg me-1"></i>Add Guest
          </button>
        </div>

        <div class="form-check mb-4" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
          <input 
            v-model="bringingGuest" 
            class="form-check-input" 
            type="checkbox" 
            id="bringingGuest"
          >
          <label class="form-check-label" for="bringingGuest" style="font-weight: 500;">
            I will be bringing a guest to the convention
          </label>
        </div>

        <div v-if="bringingGuest">
          <!-- Existing Guests -->
          <div v-if="guests.length > 0" class="mb-4">
            <h6 style="font-weight: 600; margin-bottom: 1rem;">Registered Guests:</h6>
            <div v-for="guest in guests" :key="guest.id" class="border rounded p-3 mb-3" style="border: 1px solid #e2e8f0 !important; border-radius: 12px;">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <strong style="font-size: 1.05rem;">{{ guest.guest_first_name }} {{ guest.guest_last_name }}</strong>
                  <div class="text-muted small mt-1">
                    <div v-if="guest.guest_email"><i class="bi bi-envelope me-1"></i>{{ guest.guest_email }}</div>
                    <div v-if="guest.guest_phone"><i class="bi bi-telephone me-1"></i>{{ guest.guest_phone }}</div>
                    <div v-if="guest.guest_dietary_restrictions">
                      <i class="bi bi-info-circle me-1"></i>Dietary: {{ guest.guest_dietary_restrictions }}
                    </div>
                  </div>
                </div>
                <button 
                  @click="removeGuest(guest.id)" 
                  class="btn btn-sm"
                  style="border: 1.5px solid #e2e8f0; color: #ef4444; border-radius: 8px;"
                  :disabled="saving"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Add New Guest Form -->
          <div class="border rounded p-4" style="background: #fafbfc; border: 1px solid #e2e8f0 !important; border-radius: 12px;">
            <h6 style="font-weight: 600; margin-bottom: 1.25rem;">Add New Guest:</h6>
            <form @submit.prevent="addGuest">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">First Name</label>
                  <input v-model="newGuest.guest_first_name" type="text" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Last Name</label>
                  <input v-model="newGuest.guest_last_name" type="text" class="form-control" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input v-model="newGuest.guest_email" type="email" class="form-control">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input v-model="newGuest.guest_phone" type="tel" class="form-control">
                </div>
                <div class="col-12">
                  <label class="form-label">Dietary Restrictions</label>
                  <input v-model="newGuest.guest_dietary_restrictions" type="text" class="form-control">
                </div>
                <div class="col-12">
                  <label class="form-label">Special Requests</label>
                  <textarea v-model="newGuest.guest_special_requests" class="form-control" rows="2"></textarea>
                </div>
              </div>
              <button type="submit" class="btn btn-primary mt-3" :disabled="saving">
                <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Adding...</span>
                <span v-else><i class="bi bi-plus-circle me-2"></i>Add Guest</span>
              </button>
            </form>
          </div>
        </div>
        <div v-else class="info-alert" style="background: #f8fafc; border-left-color: #94a3b8;">
          <i class="bi bi-info-circle" style="color: #64748b;"></i>
          <div class="info-alert-content" style="color: #475569;">
            No guests registered. Check the box above to add a guest.
          </div>
        </div>
      </div>

      <!-- Travel Section -->
      <div id="travel-info" class="section-card scroll-target">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-airplane"></i>
            </div>
            Travel Information
          </h2>
          <span class="status-badge" :class="isTravelComplete ? 'status-complete' : 'status-pending'">
            {{ isTravelComplete ? 'Complete' : 'Pending' }}
          </span>
        </div>

        <form @submit.prevent="saveTravel">
          <div class="row g-4">
            <div class="col-md-6">
              <label class="form-label">Travel Method</label>
              <select v-model="travel.travel_method" class="form-select">
                <option value="need_booking">Need Convention to Book</option>
                <option value="self_booking">Booking My Own</option>
                <option value="not_flying">Not Flying</option>
              </select>
            </div>
            <div class="col-md-6">
              <div class="form-check" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
                <input v-model="travel.has_booked_flight" class="form-check-input" type="checkbox" id="hasBookedFlight">
                <label class="form-check-label" for="hasBookedFlight" style="font-weight: 500;">
                  I have already booked my flight
                </label>
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Departure Airport</label>
              <input v-model="travel.departure_airport" type="text" class="form-control" placeholder="e.g., TYS">
            </div>
            <div class="col-md-6">
              <label class="form-label">Return Airport</label>
              <input v-model="travel.return_airport" type="text" class="form-control" placeholder="e.g., TYS">
            </div>

            <div class="col-md-6">
              <label class="form-label">Departure Date</label>
              <input v-model="travel.departure_date" type="date" class="form-control">
            </div>
            <div class="col-md-6">
              <label class="form-label">Return Date</label>
              <input v-model="travel.return_date" type="date" class="form-control">
            </div>
          </div>

          <button type="submit" class="btn btn-primary mt-4" :disabled="saving">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Travel Information</span>
          </button>
        </form>
      </div>

      <!-- Accommodation Section -->
      <div id="accommodation" class="section-card scroll-target">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon gold">
              <i class="bi bi-building"></i>
            </div>
            Accommodation
          </h2>
          <span class="status-badge" :class="isAccommodationComplete ? 'status-complete' : 'status-pending'">
            {{ isAccommodationComplete ? 'Complete' : 'Pending' }}
          </span>
        </div>

        <form @submit.prevent="saveAccommodation">
          <div class="row g-4">
            <div class="col-md-6">
              <label class="form-label">Package Choice</label>
              <select v-model="accommodation.package_choice" class="form-select">
                <option value="full">Full Package (Hotel + Meals)</option>
                <option value="hotel_only">Hotel Only</option>
                <option value="none">No Package</option>
              </select>
            </div>
            <div class="col-md-6">
              <div class="form-check" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
                <input v-model="accommodation.needs_hotel" class="form-check-input" type="checkbox" id="needsHotel">
                <label class="form-check-label" for="needsHotel" style="font-weight: 500;">
                  I need hotel accommodations
                </label>
              </div>
            </div>

            <div v-if="accommodation.needs_hotel">
              <div class="col-md-6">
                <label class="form-label">Check-In Date</label>
                <input v-model="accommodation.check_in_date" type="date" class="form-control">
              </div>
              <div class="col-md-6">
                <label class="form-label">Check-Out Date</label>
                <input v-model="accommodation.check_out_date" type="date" class="form-control">
              </div>

              <div class="col-12">
                <label class="form-label">Roommate Preference</label>
                <select v-model="accommodation.roommate_preference" class="form-select">
                  <option value="any">Any Roommate</option>
                  <option value="specific">Specific Roommate</option>
                  <option value="single">Single Room</option>
                </select>
              </div>

              <div v-if="accommodation.roommate_preference === 'specific'" class="col-md-6">
                <label class="form-label">Roommate Name</label>
                <input v-model="accommodation.specific_roommate_name" type="text" class="form-control">
              </div>
              <div v-if="accommodation.roommate_preference === 'specific'" class="col-md-6">
                <label class="form-label">Roommate Chapter</label>
                <input v-model="accommodation.specific_roommate_chapter" type="text" class="form-control">
              </div>
            </div>

            <div class="col-12">
              <label class="form-label">Food Allergies</label>
              <input v-model="accommodation.food_allergies" type="text" class="form-control">
            </div>
            <div class="col-12">
              <label class="form-label">Dietary Restrictions</label>
              <input v-model="accommodation.dietary_restrictions" type="text" class="form-control">
            </div>
            <div class="col-12">
              <label class="form-label">Special Requests</label>
              <textarea v-model="accommodation.special_requests" class="form-control" rows="3"></textarea>
            </div>
          </div>

          <button type="submit" class="btn btn-primary mt-4" :disabled="saving">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Accommodation Information</span>
          </button>
        </form>
      </div>
    </div>
  </div>
    </div>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()

// State
const loading = ref(false)
const saving = ref(false)
const convention = ref(null)
const registration = ref(null)

// Member Info
const memberInfo = ref({
  first_name: '',
  preferred_first_name: '',
  badge_name: ''
})

const memberAddresses = ref([])
const memberPhones = ref([])

// Committees
const committees = [
  { field: 'alumni_affairs', label: 'Alumni Affairs' },
  { field: 'awards', label: 'Awards' },
  { field: 'chapter_operations', label: 'Chapter Operations' },
  { field: 'collegiate_chapters', label: 'Collegiate Chapters' },
  { field: 'communications', label: 'Communications' },
  { field: 'constitution', label: 'Constitution' },
  { field: 'engineering_futures', label: 'Engineering Futures' },
  { field: 'membership', label: 'Membership' },
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
  membership: 0,
  public_relations: 0,
  resolutions: 0,
  rituals: 0
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

// Computed - Section Completion Status
const isPersonalInfoComplete = computed(() => {
  return memberPhones.value.length > 0 && memberAddresses.value.length > 0
})

const isCommitteePrefsComplete = computed(() => {
  // Check if user has selected at least one preference (value > 0)
  return Object.values(committeePreferences.value).some(val => val > 0)
})

const isTravelComplete = computed(() => {
  return travel.value.travel_method && 
         (travel.value.travel_method === 'not_flying' || 
          (travel.value.departure_airport && travel.value.return_airport))
})

const isAccommodationComplete = computed(() => {
  return accommodation.value.package_choice && 
         (!accommodation.value.needs_hotel || 
          (accommodation.value.check_in_date && accommodation.value.check_out_date))
})

const isGuestInfoComplete = computed(() => {
  // Guest section is optional, so it's complete if user has made a choice
  return !bringingGuest.value || guests.value.length > 0
})

// Progress tracking
const sections = computed(() => [
  {
    id: 'personal-info',
    title: 'Personal Information',
    isComplete: isPersonalInfoComplete.value
  },
  {
    id: 'committee-prefs',
    title: 'Committee Preferences',
    isComplete: isCommitteePrefsComplete.value
  },
  {
    id: 'guest-info',
    title: 'Guest Information',
    isComplete: isGuestInfoComplete.value
  },
  {
    id: 'travel-info',
    title: 'Travel',
    isComplete: isTravelComplete.value
  },
  {
    id: 'accommodation',
    title: 'Accommodation',
    isComplete: isAccommodationComplete.value
  }
])

const completionPercentage = computed(() => {
  const completedCount = sections.value.filter(s => s.isComplete).length
  return Math.round((completedCount / sections.value.length) * 100)
})

// Methods
const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    const offset = 100 // Account for sticky header
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    const offsetPosition = elementPosition - offset
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

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
/* Progress Section */
.progress-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.progress-label {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.875rem;
}

.progress-percentage {
  font-weight: 700;
  color: var(--brand-blue);
  font-size: 1.125rem;
}

.progress-bar-wrapper {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand-blue), var(--brand-gold));
  transition: width 0.5s ease;
  border-radius: 4px;
}

/* Section Status Grid */
.section-status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #fafbfc;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
}

.status-card:hover {
  border-color: var(--brand-blue);
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 64, 128, 0.1);
}

.status-card.complete {
  border-color: #10b981;
  background: #f0fdf4;
}

.status-card.complete:hover {
  background: #dcfce7;
}

.status-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.status-card.complete .status-icon {
  color: #10b981;
}

.status-card.incomplete .status-icon {
  color: #cbd5e1;
}

.status-content {
  flex: 1;
  min-width: 0;
}

.status-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: #1a202c;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge-complete {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #10b981;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-pending {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #f59e0b;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Smooth scroll offset */
.scroll-target {
  scroll-margin-top: 100px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .section-status-grid {
    grid-template-columns: 1fr;
  }
  
  .progress-section {
    padding: 1rem;
  }
  
  .status-card {
    padding: 0.875rem;
  }
  
  .status-icon {
    font-size: 1.25rem;
  }
}

/* Component-specific styles */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}
</style>
