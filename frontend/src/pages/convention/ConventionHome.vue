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
                maxlength="100"
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

        <!-- Mobile Phone for Convention Contact -->
        <h6 style="font-weight: 600; margin-bottom: 0.5rem; color: #1a202c;">Mobile Phone Number</h6>
        <p class="text-muted" style="font-size: 0.875rem; margin-bottom: 1rem;">
          This number will be used for travel coordination and voting at the convention.
        </p>
        
        <form @submit.prevent="saveMobilePhone">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Mobile Phone *</label>
              <input 
                v-model="mobilePhone.phone_number" 
                @input="handlePhoneInput"
                type="tel" 
                class="form-control"
                placeholder="(555) 123-4567"
                required
                maxlength="14"
                title="Phone number"
              >
              <small class="form-text text-muted">
                <span v-if="mobilePhone.formatted_number">
                  Current: {{ mobilePhone.formatted_number }}
                </span>
                <span v-else>
                  No mobile phone on file
                </span>
              </small>
            </div>
          </div>
          <button type="submit" class="btn btn-gold mt-3" :disabled="saving">
            <span v-if="saving">
              <span class="spinner-border spinner-border-sm me-2"></span>Saving...
            </span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Mobile Phone</span>
          </button>
        </form>

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

        <!-- Display Booked Flight Information (if available) -->
        <div v-if="travel.has_booked_flight" class="booked-flight-info mb-4" style="background: #f0f9ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 1.5rem;">
          <h5 class="mb-3" style="color: #1e40af; font-weight: 600;">
            <i class="bi bi-check-circle-fill me-2"></i>Your Flight Has Been Booked!
          </h5>
          
          <div class="row g-3">
            <div class="col-md-6">
              <div class="flight-card" style="background: white; border: 1px solid #bfdbfe; border-radius: 6px; padding: 1rem;">
                <h6 class="fw-bold mb-3" style="color: #1e40af;">
                  <i class="bi bi-airplane-fill me-2"></i>Outbound Flight
                </h6>
                <p class="mb-1"><strong>Airline:</strong> {{ travel.outbound_airline }}</p>
                <p class="mb-1"><strong>Flight:</strong> {{ travel.outbound_flight_number }}</p>
                <p class="mb-1" v-if="travel.outbound_departure_time">
                  <strong>Departure:</strong> {{ formatDateTime(travel.outbound_departure_time) }}
                </p>
                <p class="mb-1" v-if="travel.outbound_arrival_time">
                  <strong>Arrival:</strong> {{ formatDateTime(travel.outbound_arrival_time) }}
                </p>
                <p class="mb-0" v-if="travel.outbound_confirmation">
                  <strong>Confirmation:</strong> {{ travel.outbound_confirmation }}
                </p>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="flight-card" style="background: white; border: 1px solid #bfdbfe; border-radius: 6px; padding: 1rem;">
                <h6 class="fw-bold mb-3" style="color: #1e40af;">
                  <i class="bi bi-airplane-fill me-2" style="transform: rotate(90deg); display: inline-block;"></i>Return Flight
                </h6>
                <p class="mb-1"><strong>Airline:</strong> {{ travel.return_airline }}</p>
                <p class="mb-1"><strong>Flight:</strong> {{ travel.return_flight_number }}</p>
                <p class="mb-1" v-if="travel.return_departure_time">
                  <strong>Departure:</strong> {{ formatDateTime(travel.return_departure_time) }}
                </p>
                <p class="mb-1" v-if="travel.return_arrival_time">
                  <strong>Arrival:</strong> {{ formatDateTime(travel.return_arrival_time) }}
                </p>
                <p class="mb-0" v-if="travel.return_confirmation">
                  <strong>Confirmation:</strong> {{ travel.return_confirmation }}
                </p>
              </div>
            </div>
          </div>
          
          <div v-if="travel.flight_notes" class="mt-3 alert alert-light mb-0">
            <strong>Notes:</strong> {{ travel.flight_notes }}
          </div>
        </div>

        <form @submit.prevent="saveTravel">
          <div class="row g-4">
            <!-- Travel Method -->
            <div class="col-12">
              <label class="form-label">Travel Method *</label>
              <select v-model="travel.travel_method" class="form-select" @change="handleTravelMethodChange">
                <option value="need_booking">Need Convention to Book</option>
                <option value="self_booking">Booking My Own</option>
                <option value="driving">Driving</option>
              </select>
            </div>

            <!-- Show flight details only if need_booking -->
            <template v-if="travel.travel_method === 'need_booking'">
              <!-- Seat Preference -->
              <div class="col-md-6">
                <label class="form-label">Seat Preference</label>
                <select v-model="travel.seat_preference" class="form-select">
                  <option value="none">No Preference</option>
                  <option value="window">Window</option>
                  <option value="aisle">Aisle</option>
                </select>
              </div>

              <div class="col-md-6">
                <!-- Spacer for layout -->
              </div>

              <!-- Departure State -->
              <div class="col-md-6">
                <label class="form-label">Departure State *</label>
                <select v-model="departureState" class="form-select" required>
                  <option value="">Select State</option>
                  <option v-for="state in states" :key="state.code" :value="state.code">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <!-- Departure Airport -->
              <div class="col-md-6">
                <label class="form-label">Departure Airport *</label>
                <select v-model="travel.departure_airport" class="form-select" :disabled="!departureState" required>
                  <option value="">Select Airport</option>
                  <option v-for="airport in departureAirports" :key="airport.code" :value="airport.code">
                    {{ airport.code }} - {{ airport.description }}
                  </option>
                </select>
              </div>

              <!-- Departure Date -->
              <div class="col-md-6">
                <label class="form-label">Departure Date *</label>
                <input v-model="travel.departure_date" type="date" class="form-control" required>
              </div>

              <!-- Departure Time -->
              <div class="col-md-6">
                <label class="form-label">Departure Time Preference *</label>
                <select v-model.number="travel.departure_time_preference" class="form-select" required>
                  <option :value="null">Select Time</option>
                  <option v-for="time in timeOptions" :key="time.value" :value="time.value">
                    {{ time.label }}
                  </option>
                </select>
              </div>

              <!-- Return State -->
              <div class="col-md-6">
                <label class="form-label">Return State *</label>
                <select v-model="returnState" class="form-select" required>
                  <option value="">Select State</option>
                  <option v-for="state in states" :key="state.code" :value="state.code">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <!-- Return Airport -->
              <div class="col-md-6">
                <label class="form-label">Return Airport *</label>
                <select v-model="travel.return_airport" class="form-select" :disabled="!returnState" required>
                  <option value="">Select Airport</option>
                  <option v-for="airport in returnAirports" :key="airport.code" :value="airport.code">
                    {{ airport.code }} - {{ airport.description }}
                  </option>
                </select>
              </div>

              <!-- Return Date -->
              <div class="col-md-6">
                <label class="form-label">Return Date *</label>
                <input v-model="travel.return_date" type="date" class="form-control" required>
              </div>

              <!-- Return Time -->
              <div class="col-md-6">
                <label class="form-label">Return Time Preference *</label>
                <select v-model.number="travel.return_time_preference" class="form-select" required>
                  <option :value="null">Select Time</option>
                  <option v-for="time in timeOptions" :key="time.value" :value="time.value">
                    {{ time.label }}
                  </option>
                </select>
              </div>

              <!-- Ground Transportation -->
              <div class="col-12">
                <div class="form-check" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
                  <input v-model="travel.needs_ground_transportation" class="form-check-input" type="checkbox" id="needsGroundTransport">
                  <label class="form-check-label" for="needsGroundTransport" style="font-weight: 500;">
                    I need transportation to/from the convention airport
                  </label>
                </div>
              </div>
            </template>

            <!-- Message for self-booking or driving -->
            <div v-else class="col-12">
              <div class="alert alert-info" style="border-left: 4px solid #3b82f6;">
                <i class="bi bi-info-circle me-2"></i>
                <span v-if="travel.travel_method === 'self_booking'">
                  <strong>Booking Your Own Flight:</strong> No additional information needed. Please arrange your own travel to the convention.
                </span>
                <span v-else-if="travel.travel_method === 'driving'">
                  <strong>Driving to Convention:</strong> No flight information needed. We look forward to seeing you there!
                </span>
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-primary mt-4" :disabled="saving || (travel.travel_method === 'need_booking' && !isValidTravelDates)">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Travel Information</span>
          </button>
          
          <p v-if="travel.travel_method === 'need_booking' && !isValidTravelDates" class="text-danger mt-2 mb-0">
            <i class="bi bi-exclamation-circle me-1"></i>
            Return date must be on or after departure date
          </p>
        </form>
      </div>

      <!-- Accommodation Section -->
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
                  <label class="form-label">First Name *</label>
                  <input v-model="newGuest.guest_first_name" type="text" class="form-control" required maxlength="100">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Last Name *</label>
                  <input v-model="newGuest.guest_last_name" type="text" class="form-control" required maxlength="100">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email</label>
                  <input v-model="newGuest.guest_email" type="email" class="form-control" maxlength="254">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input v-model="newGuest.guest_phone" type="tel" class="form-control" maxlength="20" pattern="[\+]?[0-9\s\-\(\)]+" title="Phone number (numbers, spaces, dashes, parentheses allowed)">
                </div>
                <div class="col-12">
                  <label class="form-label">Dietary Restrictions</label>
                  <input v-model="newGuest.guest_dietary_restrictions" type="text" class="form-control" maxlength="500">
                </div>
                <div class="col-12">
                  <label class="form-label">Special Requests</label>
                  <textarea v-model="newGuest.guest_special_requests" class="form-control" rows="2" maxlength="1000"></textarea>
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
              <label class="form-label">Package Choice *</label>
              <select v-model="accommodation.package_choice" class="form-select" required>
                <option value="full">Full Package - All meals and events</option>
                <option value="partial">Partial Package - Select meals</option>
                <option value="commuter">Commuter Package - No hotel</option>
                <option value="custom">Custom Package</option>
              </select>
            </div>
            
            <div class="col-12">
              <div class="form-check" style="padding: 1rem; background: #fafbfc; border-radius: 8px; border: 1px solid #e2e8f0;">
                <input v-model="accommodation.needs_hotel" class="form-check-input" type="checkbox" id="needsHotel">
                <label class="form-check-label" for="needsHotel" style="font-weight: 500;">
                  I need hotel accommodations
                </label>
              </div>
            </div>

            <div v-if="accommodation.needs_hotel">
              <div class="col-md-6">
                <label class="form-label">Check-In Date *</label>
                <input v-model="accommodation.check_in_date" type="date" class="form-control" :required="accommodation.needs_hotel">
              </div>
              <div class="col-md-6">
                <label class="form-label">Check-Out Date *</label>
                <input v-model="accommodation.check_out_date" type="date" class="form-control" :required="accommodation.needs_hotel">
              </div>

              <div class="col-12">
                <label class="form-label">Roommate Preference *</label>
                <select v-model="accommodation.roommate_preference" class="form-select" :required="accommodation.needs_hotel">
                  <option value="any">Any Roommate</option>
                  <option value="specific">Specific Roommate</option>
                  <option value="single">Single Room</option>
                </select>
              </div>

              <div v-if="accommodation.roommate_preference === 'specific'" class="col-md-6">
                <label class="form-label">Roommate Name *</label>
                <input v-model="accommodation.specific_roommate_name" type="text" class="form-control" maxlength="200" :required="accommodation.roommate_preference === 'specific'">
              </div>
              <div v-if="accommodation.roommate_preference === 'specific'" class="col-md-6">
                <label class="form-label">Roommate Chapter *</label>
                <input v-model="accommodation.specific_roommate_chapter" type="text" class="form-control" maxlength="100" :required="accommodation.roommate_preference === 'specific'">
              </div>
            </div>

            <div class="col-12">
              <label class="form-label">Food Allergies</label>
              <input v-model="accommodation.food_allergies" type="text" class="form-control" maxlength="500">
            </div>
            <div class="col-12">
              <label class="form-label">Dietary Restrictions</label>
              <input v-model="accommodation.dietary_restrictions" type="text" class="form-control" maxlength="500">
            </div>
            <div class="col-12">
              <label class="form-label">Special Requests</label>
              <textarea v-model="accommodation.special_requests" class="form-control" rows="3" maxlength="1000"></textarea>
            </div>
          </div>

          <button type="submit" class="btn btn-primary mt-4" :disabled="saving || !isValidAccommodationDates">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
            <span v-else><i class="bi bi-check2 me-2"></i>Save Accommodation Information</span>
          </button>
          
          <p v-if="!isValidAccommodationDates" class="text-danger mt-2 mb-0">
            <i class="bi bi-exclamation-circle me-1"></i>
            Check-out date must be on or after check-in date
          </p>
        </form>
      </div>
    </div>
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
  </div>
    </div>

</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
const mobilePhone = ref({
  id: null,
  phone_number: '',
  formatted_number: ''
})

// Clean phone number - remove all non-digits
const getCleanPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return ''
  return phoneNumber.replace(/\D/g, '')
}

// Format phone number to match UserAccount.vue formatting
const formatPhoneNumber = (value) => {
  if (!value) return value
  
  const cleaned = getCleanPhoneNumber(value)
  
  // Format US/Canada numbers (10 digits) as (XXX) XXX-XXXX
  if (cleaned.length === 10) {
    return `(${cleaned.substr(0, 3)}) ${cleaned.substr(3, 3)}-${cleaned.substr(6, 4)}`
  }
  
  // For international or incomplete numbers, return cleaned digits
  return cleaned
}

const handlePhoneInput = (event) => {
  const input = event.target.value
  const formatted = formatPhoneNumber(input)
  mobilePhone.value.phone_number = formatted
}

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

// States and Airports
const states = ref([])
const departureAirports = ref([])
const returnAirports = ref([])
const departureState = ref('')
const returnState = ref('')

// Travel
const travel = ref({
  travel_method: 'need_booking',
  departure_airport: '',
  departure_date: null,
  departure_time_preference: null,
  return_airport: '',
  return_date: null,
  return_time_preference: null,
  seat_preference: 'none',
  needs_ground_transportation: true,
  has_booked_flight: false
})

// Time options (minutes from midnight)
const timeOptions = [
  { value: 0, label: '12:00 AM' },
  { value: 30, label: '12:30 AM' },
  { value: 60, label: '01:00 AM' },
  { value: 90, label: '01:30 AM' },
  { value: 120, label: '02:00 AM' },
  { value: 150, label: '02:30 AM' },
  { value: 180, label: '03:00 AM' },
  { value: 210, label: '03:30 AM' },
  { value: 240, label: '04:00 AM' },
  { value: 270, label: '04:30 AM' },
  { value: 300, label: '05:00 AM' },
  { value: 330, label: '05:30 AM' },
  { value: 360, label: '06:00 AM' },
  { value: 390, label: '06:30 AM' },
  { value: 420, label: '07:00 AM' },
  { value: 450, label: '07:30 AM' },
  { value: 480, label: '08:00 AM' },
  { value: 510, label: '08:30 AM' },
  { value: 540, label: '09:00 AM' },
  { value: 570, label: '09:30 AM' },
  { value: 600, label: '10:00 AM' },
  { value: 630, label: '10:30 AM' },
  { value: 660, label: '11:00 AM' },
  { value: 690, label: '11:30 AM' },
  { value: 720, label: '12:00 PM' },
  { value: 750, label: '12:30 PM' },
  { value: 780, label: '01:00 PM' },
  { value: 810, label: '01:30 PM' },
  { value: 840, label: '02:00 PM' },
  { value: 870, label: '02:30 PM' },
  { value: 900, label: '03:00 PM' },
  { value: 930, label: '03:30 PM' },
  { value: 960, label: '04:00 PM' },
  { value: 990, label: '04:30 PM' },
  { value: 1020, label: '05:00 PM' },
  { value: 1050, label: '05:30 PM' },
  { value: 1080, label: '06:00 PM' },
  { value: 1110, label: '06:30 PM' },
  { value: 1140, label: '07:00 PM' },
  { value: 1170, label: '07:30 PM' },
  { value: 1200, label: '08:00 PM' },
  { value: 1230, label: '08:30 PM' },
  { value: 1260, label: '09:00 PM' },
  { value: 1290, label: '09:30 PM' },
  { value: 1320, label: '10:00 PM' },
  { value: 1350, label: '10:30 PM' },
  { value: 1380, label: '11:00 PM' },
  { value: 1410, label: '11:30 PM' }
]

// Accommodation
const accommodation = ref({
  package_choice: 'full',
  needs_hotel: true,
  check_in_date: null,
  check_out_date: null,
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
  return mobilePhone.value.phone_number && memberAddresses.value.length > 0
})

const isCommitteePrefsComplete = computed(() => {
  // Check if user has selected at least one preference (value > 0)
  return Object.values(committeePreferences.value).some(val => val > 0)
})

const isTravelComplete = computed(() => {
  if (!travel.value.travel_method) return false
  
  // For driving or self_booking, just having the travel method selected is complete
  if (travel.value.travel_method === 'driving' || travel.value.travel_method === 'self_booking') {
    return true
  }
  
  // For need_booking, require all flight details
  return travel.value.departure_airport && 
         travel.value.return_airport && 
         travel.value.departure_date && 
         travel.value.return_date
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

// Date validation
const isValidTravelDates = computed(() => {
  if (!travel.value.departure_date || !travel.value.return_date) return true
  return new Date(travel.value.return_date) >= new Date(travel.value.departure_date)
})

const isValidAccommodationDates = computed(() => {
  if (!accommodation.value.check_in_date || !accommodation.value.check_out_date) return true
  return new Date(accommodation.value.check_out_date) >= new Date(accommodation.value.check_in_date)
})

// Email validation helper
const isValidEmail = (email) => {
  if (!email) return true // Optional field
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  const options = { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }
  return date.toLocaleString('en-US', options)
}

// Progress tracking
const sections = computed(() => [
  {
    id: 'personal-info',
    title: 'Personal Information',
    isComplete: isPersonalInfoComplete.value
  },
  {
    id: 'travel-info',
    title: 'Travel',
    isComplete: isTravelComplete.value
  },
  {
    id: 'guest-info',
    title: 'Guest Information',
    isComplete: isGuestInfoComplete.value
  },
  {
    id: 'accommodation',
    title: 'Accommodation',
    isComplete: isAccommodationComplete.value
  },
  {
    id: 'committee-prefs',
    title: 'Committee Preferences',
    isComplete: isCommitteePrefsComplete.value
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
      await loadRegistrationData(response.data)
    }
  } catch (error) {
    console.error('Error fetching registration:', error)
    registration.value = null
  }
}

const loadRegistrationData = async (data) => {
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
    // Extract mobile phone for easy access
    const mobile = data.member_phones.find(phone => phone.phone_type === 'Mobile')
    if (mobile) {
      mobilePhone.value = {
        id: mobile.id,
        phone_number: formatPhoneNumber(mobile.phone_number),
        formatted_number: mobile.formatted_number
      }
    }
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
    
    // If airports are already set, find and set their states
    if (travel.value.departure_airport || travel.value.return_airport) {
      try {
        const response = await api.get('/api/convention/airports/')
        const allAirports = response.data
        
        if (travel.value.departure_airport) {
          const departureAirport = allAirports.find(a => a.code === travel.value.departure_airport)
          if (departureAirport) {
            departureState.value = departureAirport.state
            await fetchAirportsForState(departureAirport.state, true)
          }
        }
        
        if (travel.value.return_airport) {
          const returnAirport = allAirports.find(a => a.code === travel.value.return_airport)
          if (returnAirport) {
            returnState.value = returnAirport.state
            await fetchAirportsForState(returnAirport.state, false)
          }
        }
      } catch (error) {
        console.error('Error loading airport states:', error)
      }
    }
  }

  // Load accommodation
  if (data.accommodation) {
    accommodation.value = { ...data.accommodation }
    
    // Migrate old package_choice values to new valid ones
    const oldToNewMapping = {
      'hotel_only': 'custom',      // Hotel only -> Custom package
      'none': 'commuter'           // No package -> Commuter (no hotel)
    }
    
    if (oldToNewMapping[accommodation.value.package_choice]) {
      accommodation.value.package_choice = oldToNewMapping[accommodation.value.package_choice]
    }
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

const saveMobilePhone = async () => {
  saving.value = true
  try {
    // Clean phone number - send only digits
    const cleanNumber = getCleanPhoneNumber(mobilePhone.value.phone_number)
    
    const response = await api.put('/api/convention/member/update-mobile-phone/', {
      phone_number: cleanNumber
    })
    toast.success('Mobile phone updated!')
    
    // Update the mobile phone data with the response
    if (response.data.phone) {
      mobilePhone.value = {
        id: response.data.phone.id,
        phone_number: formatPhoneNumber(response.data.phone.phone_number),
        formatted_number: response.data.phone.formatted_number
      }
    }
    
    await fetchRegistration()
  } catch (error) {
    console.error('Error saving mobile phone:', error)
    toast.error('Failed to save mobile phone')
  } finally {
    saving.value = false
  }
}

const setPrimaryAddress = async (addressId) => {
  saving.value = true
  try {
    // Updated to use accounts app endpoint which includes database sync
    await api.post(`/api/accounts/addresses/${addressId}/set_primary/`)
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
    // Updated to use accounts app endpoint
    await api.post(`/api/accounts/phone-numbers/${phoneId}/set_primary/`)
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
  // Validate email if provided
  if (newGuest.value.guest_email && !isValidEmail(newGuest.value.guest_email)) {
    toast.error('Please enter a valid email address')
    return
  }
  
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

// Fetch states with airports
const fetchStates = async () => {
  try {
    const response = await api.get('/api/convention/states/')
    states.value = response.data
  } catch (error) {
    console.error('Error fetching states:', error)
  }
}

// Fetch airports for selected state
const fetchAirportsForState = async (state, isDeparture = true) => {
  try {
    const response = await api.get(`/api/convention/airports/?state=${state}`)
    if (isDeparture) {
      departureAirports.value = response.data
    } else {
      returnAirports.value = response.data
    }
  } catch (error) {
    console.error('Error fetching airports:', error)
  }
}

// Watch for state changes to load airports
watch(departureState, (newState) => {
  if (newState) {
    fetchAirportsForState(newState, true)
  } else {
    departureAirports.value = []
    travel.value.departure_airport = ''
  }
})

watch(returnState, (newState) => {
  if (newState) {
    fetchAirportsForState(newState, false)
  } else {
    returnAirports.value = []
    travel.value.return_airport = ''
  }
})

// Handle travel method changes
const handleTravelMethodChange = () => {
  // If switching from need_booking to self_booking or driving, clear flight details
  if (travel.value.travel_method !== 'need_booking') {
    // Clear all flight-related data - use null for cleaner data
    travel.value.departure_airport = ''
    travel.value.departure_date = null
    travel.value.departure_time_preference = null
    travel.value.return_airport = ''
    travel.value.return_date = null
    travel.value.return_time_preference = null
    travel.value.seat_preference = 'none'
    travel.value.needs_ground_transportation = true
    
    // Clear state selections
    departureState.value = ''
    returnState.value = ''
    departureAirports.value = []
    returnAirports.value = []
  }
}

const saveTravel = async () => {
  saving.value = true
  try {
    // Clean the data before sending - convert empty strings to null
    const cleanedData = {
      ...travel.value,
      departure_date: travel.value.departure_date || null,
      return_date: travel.value.return_date || null,
      departure_airport: travel.value.departure_airport || '',
      return_airport: travel.value.return_airport || '',
      departure_time_preference: travel.value.departure_time_preference ?? null,
      return_time_preference: travel.value.return_time_preference ?? null
    }
    
    await api.put(
      `/api/convention/registration/${registration.value.id}/travel/`,
      cleanedData
    )
    toast.success('Travel information saved!')
  } catch (error) {
    console.error('Error saving travel:', error)
    console.error('Response data:', error.response?.data)
    console.error('Travel value being sent:', travel.value)
    
    // Show specific error message if available
    if (error.response?.data) {
      const errors = error.response.data
      const errorMessages = Object.entries(errors)
        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
        .join('\n')
      toast.error(`Validation errors:\n${errorMessages}`)
    } else {
      toast.error('Failed to save travel information')
    }
  } finally {
    saving.value = false
  }
}

const saveAccommodation = async () => {
  saving.value = true
  try {
    // Clean the data before sending - convert empty strings to null for dates
    const cleanedData = {
      ...accommodation.value,
      check_in_date: accommodation.value.check_in_date || null,
      check_out_date: accommodation.value.check_out_date || null
    }
    
    await api.put(
      `/api/convention/registration/${registration.value.id}/accommodation/`,
      cleanedData
    )
    toast.success('Accommodation information saved!')
  } catch (error) {
    console.error('Error saving accommodation:', error)
    console.error('Response data:', error.response?.data)
    console.error('Accommodation value being sent:', accommodation.value)
    
    // Show specific error message if available
    if (error.response?.data) {
      const errors = error.response.data
      const errorMessages = Object.entries(errors)
        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
        .join('\n')
      toast.error(`Validation errors:\n${errorMessages}`)
    } else {
      toast.error('Failed to save accommodation information')
    }
  } finally {
    saving.value = false
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  try {
    await fetchStates()
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
