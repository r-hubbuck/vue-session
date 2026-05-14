<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '../../api'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const registrationId = route.params.id

// ── Top-level state ──────────────────────────────────────────────────────────
const loading = ref(true)
const registration = ref(null)

// ── Section open/loaded state ────────────────────────────────────────────────
const sectionOpen = ref({
  regInfo: false,
  travel: false,
  accommodation: false,
  committee: false,
  guests: false,
})

const sectionLoaded = ref({
  travel: false,
  accommodation: false,
  committee: false,
  guests: false,
})

// ── Per-section saving state ─────────────────────────────────────────────────
const savingSection = ref({
  regInfo: false,
  travel: false,
  accommodation: false,
  committee: false,
})

// ── Per-section error state ──────────────────────────────────────────────────
const sectionErrors = ref({
  regInfo: {},
  travel: {},
  accommodation: {},
  committee: {},
})

// ── Section-specific data ────────────────────────────────────────────────────
const regForm = ref({})
const travel = ref({})
const accommodation = ref({})
const committee = ref({})
const guests = ref([])

// ── Guests state ─────────────────────────────────────────────────────────────
const addingGuest = ref(false)
const newGuestForm = ref({ guest_first_name: '', guest_last_name: '', guest_email: '', guest_phone: '' })
const newGuestErrors = ref({})
const savingGuest = ref(false)
const editingGuestId = ref(null)
const editGuestForm = ref({})
const editGuestErrors = ref({})
const savingEditGuest = ref(false)
const deletingGuestId = ref(null)

// ── Terms email ───────────────────────────────────────────────────────────────
const sendingTermsEmail = ref(false)

// ── Time options ─────────────────────────────────────────────────────────────
const timeOptions = (() => {
  const opts = []
  for (let m = 360; m <= 1380; m += 30) {
    const h = Math.floor(m / 60)
    const min = m % 60
    const period = h < 12 ? 'AM' : 'PM'
    const dh = h > 12 ? h - 12 : (h === 0 ? 12 : h)
    opts.push({ value: m, label: `${dh}:${String(min).padStart(2, '0')} ${period}` })
  }
  return opts
})()

// ── Constants ─────────────────────────────────────────────────────────────────
const STATUS_CHOICES = [
  { value: 'registered', label: 'Registered' },
  { value: 'checked_in', label: 'Checked In' },
  { value: 'cancelled', label: 'Cancelled' },
]

const GUEST_CHOICES = [
  { value: null, label: 'Undecided' },
  { value: true, label: 'Yes' },
  { value: false, label: 'No' },
]

const VISIBILITY_CHOICES = [
  { value: 'none', label: 'None' },
  { value: 'business', label: 'Business' },
  { value: 'graduate_school', label: 'Graduate School' },
  { value: 'both', label: 'Both' },
]

const TRAVEL_METHOD_CHOICES = [
  { value: 'need_booking', label: 'Needs Booking' },
  { value: 'self_booking', label: 'Self Booking' },
  { value: 'driving', label: 'Driving' },
]

const SEAT_CHOICES = [
  { value: 'none', label: 'No Preference' },
  { value: 'window', label: 'Window' },
  { value: 'aisle', label: 'Aisle' },
]

const PACKAGE_CHOICES = [
  { value: 'full', label: 'Full Package' },
  { value: 'partial', label: 'Partial Package' },
  { value: 'commuter', label: 'Commuter' },
  { value: 'custom', label: 'Custom' },
]

const ROOMMATE_CHOICES = [
  { value: 'any', label: 'Any' },
  { value: 'specific', label: 'Specific Person' },
  { value: 'single', label: 'Single' },
]

const ALLERGY_OPTIONS = [
  { value: 'milk', label: 'Milk' },
  { value: 'eggs', label: 'Eggs' },
  { value: 'peanuts', label: 'Peanuts' },
  { value: 'tree_nuts', label: 'Tree Nuts' },
  { value: 'fish', label: 'Fish' },
  { value: 'shellfish', label: 'Shellfish' },
  { value: 'soy', label: 'Soy' },
  { value: 'wheat', label: 'Wheat' },
  { value: 'sesame', label: 'Sesame' },
]

const DIETARY_OPTIONS = [
  { value: 'gluten_free', label: 'Gluten Free' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'kosher', label: 'Kosher' },
  { value: 'halal', label: 'Halal' },
  { value: 'dairy_free', label: 'Dairy Free' },
  { value: 'nut_free', label: 'Nut Free' },
]

const COMMITTEE_FIELDS = [
  'alumni_affairs', 'awards', 'chapter_operations', 'collegiate_chapters',
  'communications', 'constitution', 'engineering_futures', 'membership',
  'public_relations', 'resolutions', 'rituals',
]

const COMMITTEE_PREF_LABELS = { 0: 'No Interest', 1: 'Interested', 2: 'Prefer' }

// ── Computed ──────────────────────────────────────────────────────────────────
const personName = computed(() => {
  if (!registration.value) return ''
  const p = registration.value.person
  const first = p.preferred_first_name || p.first_name
  return `${first} ${p.last_name}`
})

const statusLabel = computed(() => {
  if (!registration.value) return ''
  const s = STATUS_CHOICES.find(c => c.value === registration.value.status_code)
  return s ? s.label : registration.value.status_code
})

function toTitleCase(str) {
  return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

// ── Initial load ─────────────────────────────────────────────────────────────
async function loadRegistration() {
  loading.value = true
  try {
    const res = await api.get(`/api/convention/admin/registrations/${registrationId}/`)
    registration.value = res.data
    regForm.value = {
      status_code: res.data.status_code,
      paid: res.data.paid,
      credentials_received: res.data.credentials_received,
      guest_attending: res.data.guest_attending,
      visible_to_recruiters: res.data.visible_to_recruiters,
      contact_email: res.data.contact_email || '',
      emergency_contact_name: res.data.emergency_contact_name || '',
      emergency_contact_relationship: res.data.emergency_contact_relationship || '',
      emergency_contact_phone: res.data.emergency_contact_phone || '',
    }
  } catch {
    toast.error('Failed to load registration.')
    router.push('/convention-admin')
  } finally {
    loading.value = false
  }
}

// ── Section toggle + lazy load ────────────────────────────────────────────────
async function toggleSection(name) {
  sectionOpen.value[name] = !sectionOpen.value[name]
  if (!sectionOpen.value[name]) return
  if (name === 'travel' && !sectionLoaded.value.travel) await loadTravel()
  if (name === 'accommodation' && !sectionLoaded.value.accommodation) await loadAccommodation()
  if (name === 'committee' && !sectionLoaded.value.committee) await loadCommittee()
  if (name === 'guests' && !sectionLoaded.value.guests) await loadGuests()
}

// ── Travel ────────────────────────────────────────────────────────────────────
async function loadTravel() {
  try {
    const res = await api.get(`/api/convention/admin/registrations/${registrationId}/travel/`)
    travel.value = { ...res.data }
    sectionLoaded.value.travel = true
  } catch {
    toast.error('Failed to load travel data.')
  }
}

async function saveTravel() {
  savingSection.value.travel = true
  sectionErrors.value.travel = {}
  try {
    const res = await api.put(`/api/convention/admin/registrations/${registrationId}/travel/`, travel.value)
    travel.value = { ...res.data }
    toast.success('Travel saved.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      sectionErrors.value.travel = err.response.data
    }
    toast.error('Failed to save travel.')
  } finally {
    savingSection.value.travel = false
  }
}

// ── Accommodation ─────────────────────────────────────────────────────────────
async function loadAccommodation() {
  try {
    const res = await api.get(`/api/convention/admin/registrations/${registrationId}/accommodation/`)
    accommodation.value = { ...res.data }
    sectionLoaded.value.accommodation = true
  } catch {
    toast.error('Failed to load accommodation data.')
  }
}

async function saveAccommodation() {
  savingSection.value.accommodation = true
  sectionErrors.value.accommodation = {}
  try {
    const res = await api.put(`/api/convention/admin/registrations/${registrationId}/accommodation/`, accommodation.value)
    accommodation.value = { ...res.data }
    toast.success('Accommodation saved.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      sectionErrors.value.accommodation = err.response.data
    }
    toast.error('Failed to save accommodation.')
  } finally {
    savingSection.value.accommodation = false
  }
}

// Allergy / dietary checkbox helpers
function toggleAllergy(value) {
  const arr = accommodation.value.food_allergies || []
  const idx = arr.indexOf(value)
  if (idx === -1) arr.push(value)
  else arr.splice(idx, 1)
  accommodation.value.food_allergies = [...arr]
}

function toggleDietary(value) {
  const arr = accommodation.value.dietary_restrictions || []
  const idx = arr.indexOf(value)
  if (idx === -1) arr.push(value)
  else arr.splice(idx, 1)
  accommodation.value.dietary_restrictions = [...arr]
}

function hasAllergy(value) {
  return (accommodation.value.food_allergies || []).includes(value)
}

function hasDietary(value) {
  return (accommodation.value.dietary_restrictions || []).includes(value)
}

// ── Committee Preferences ─────────────────────────────────────────────────────
async function loadCommittee() {
  try {
    const res = await api.get(`/api/convention/admin/registrations/${registrationId}/committee-preferences/`)
    committee.value = { ...res.data }
    sectionLoaded.value.committee = true
  } catch {
    toast.error('Failed to load committee preferences.')
  }
}

async function saveCommittee() {
  savingSection.value.committee = true
  sectionErrors.value.committee = {}
  try {
    const res = await api.put(`/api/convention/admin/registrations/${registrationId}/committee-preferences/`, committee.value)
    committee.value = { ...res.data }
    toast.success('Committee preferences saved.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      sectionErrors.value.committee = err.response.data
    }
    toast.error('Failed to save committee preferences.')
  } finally {
    savingSection.value.committee = false
  }
}

// ── Registration Info ─────────────────────────────────────────────────────────
async function saveRegInfo() {
  savingSection.value.regInfo = true
  sectionErrors.value.regInfo = {}
  try {
    const res = await api.put(`/api/convention/admin/registrations/${registrationId}/`, regForm.value)
    registration.value = { ...registration.value, ...res.data }
    toast.success('Registration info saved.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      sectionErrors.value.regInfo = err.response.data
    }
    toast.error('Failed to save registration info.')
  } finally {
    savingSection.value.regInfo = false
  }
}

// ── Terms email ───────────────────────────────────────────────────────────────
async function sendTermsEmail() {
  sendingTermsEmail.value = true
  try {
    await api.post(`/api/convention/admin/registrations/${registrationId}/send-terms-email/`)
    toast.success('Terms email sent.')
  } catch {
    toast.error('Failed to send terms email.')
  } finally {
    sendingTermsEmail.value = false
  }
}

// ── Guests ────────────────────────────────────────────────────────────────────
async function loadGuests() {
  try {
    const res = await api.get(`/api/convention/admin/registrations/${registrationId}/guests/`)
    guests.value = res.data
    sectionLoaded.value.guests = true
  } catch {
    toast.error('Failed to load guests.')
  }
}

function startAddGuest() {
  addingGuest.value = true
  newGuestForm.value = { guest_first_name: '', guest_last_name: '', guest_email: '', guest_phone: '' }
  newGuestErrors.value = {}
}

function cancelAddGuest() {
  addingGuest.value = false
  newGuestErrors.value = {}
}

async function saveNewGuest() {
  savingGuest.value = true
  newGuestErrors.value = {}
  try {
    const res = await api.post(`/api/convention/admin/registrations/${registrationId}/guests/`, newGuestForm.value)
    guests.value.push(res.data)
    addingGuest.value = false
    toast.success('Guest added.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      newGuestErrors.value = err.response.data
    }
    toast.error('Failed to add guest.')
  } finally {
    savingGuest.value = false
  }
}

function startEditGuest(guest) {
  editingGuestId.value = guest.id
  editGuestForm.value = { ...guest }
  editGuestErrors.value = {}
}

function cancelEditGuest() {
  editingGuestId.value = null
  editGuestErrors.value = {}
}

async function saveEditGuest(guestId) {
  savingEditGuest.value = true
  editGuestErrors.value = {}
  try {
    const res = await api.put(`/api/convention/admin/registrations/${registrationId}/guests/${guestId}/`, editGuestForm.value)
    const idx = guests.value.findIndex(g => g.id === guestId)
    if (idx !== -1) guests.value[idx] = res.data
    editingGuestId.value = null
    toast.success('Guest updated.')
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      editGuestErrors.value = err.response.data
    }
    toast.error('Failed to update guest.')
  } finally {
    savingEditGuest.value = false
  }
}

async function deleteGuest(guestId) {
  if (!confirm('Delete this guest?')) return
  deletingGuestId.value = guestId
  try {
    await api.delete(`/api/convention/admin/registrations/${registrationId}/guests/${guestId}/`)
    guests.value = guests.value.filter(g => g.id !== guestId)
    toast.success('Guest removed.')
  } catch {
    toast.error('Failed to delete guest.')
  } finally {
    deletingGuestId.value = null
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(() => {
  loadRegistration()
})
</script>

<template>
  <div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <div class="mb-2">
          <router-link to="/convention-admin" class="text-muted" style="font-size: 0.875rem;">
            <i class="bi bi-arrow-left me-1"></i>Registration Admin
          </router-link>
        </div>

        <div v-if="loading" class="d-flex align-items-center gap-2">
          <div class="spinner-border spinner-border-sm" role="status"></div>
          <span class="text-muted">Loading registration...</span>
        </div>

        <template v-else-if="registration">
          <h1 class="page-title">{{ personName }}</h1>
          <p class="page-subtitle">
            <span v-if="registration.person.member_id">
              Member #{{ registration.person.member_id }}
            </span>
            <span v-else>Non-member</span>
            <span class="mx-2">·</span>
            <span class="badge rounded-pill"
              :class="{
                'bg-success': registration.status_code === 'checked_in',
                'bg-warning text-dark': registration.status_code === 'registered',
                'bg-secondary': registration.status_code === 'cancelled',
              }">
              {{ statusLabel }}
            </span>
          </p>
        </template>
      </div>
    </div>

    <!-- Content -->
    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border" role="status"></div>
      </div>

      <template v-else-if="registration">

        <!-- ── Person Summary Card ── -->
        <div class="section-card">
          <div class="section-header" style="margin-bottom: 1.25rem; padding-bottom: 1rem;">
            <h2 class="section-title">
              <div class="section-icon">
                <i class="bi bi-person-badge"></i>
              </div>
              Person Summary
            </h2>
          </div>

          <div class="row g-3">
            <div class="col-sm-6 col-lg-3">
              <div class="text-muted" style="font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Full Name</div>
              <div class="fw-500">{{ registration.person.first_name }} {{ registration.person.last_name }}</div>
              <div v-if="registration.person.preferred_first_name" class="text-muted" style="font-size: 0.85rem;">Goes by: {{ registration.person.preferred_first_name }}</div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="text-muted" style="font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Email</div>
              <div>{{ registration.person.email || 'No account' }}</div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="text-muted" style="font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Member ID</div>
              <div v-if="registration.person.member_id">#{{ registration.person.member_id }}</div>
              <div v-else class="text-muted fst-italic">Non-member</div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="text-muted" style="font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Registered</div>
              <div>{{ registration.registration_date ? new Date(registration.registration_date).toLocaleDateString() : '—' }}</div>
            </div>
            <div class="col-sm-6 col-lg-3">
              <div class="text-muted" style="font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Terms Agreed</div>
              <div v-if="registration.terms_agreed" class="text-success">
                <i class="bi bi-check-circle-fill me-1"></i>Agreed
                <span v-if="registration.terms_agreed_at" class="text-muted d-block" style="font-size: 0.8rem;">
                  {{ new Date(registration.terms_agreed_at).toLocaleDateString() }}
                </span>
              </div>
              <div v-else class="d-flex align-items-center gap-2 flex-wrap">
                <span class="text-warning"><i class="bi bi-clock me-1"></i>Pending</span>
                <button
                  v-if="registration.contact_email"
                  class="btn btn-secondary btn-sm"
                  :disabled="sendingTermsEmail"
                  @click="sendTermsEmail"
                >
                  <span v-if="sendingTermsEmail" class="spinner-border spinner-border-sm me-1" role="status"></span>
                  Resend Email
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Registration Info Section ── -->
        <div class="section-card">
          <div class="section-header section-header-toggle" @click="toggleSection('regInfo')">
            <h2 class="section-title">
              <div class="section-icon gold">
                <i class="bi bi-clipboard-check"></i>
              </div>
              Registration Info
            </h2>
            <div class="d-flex align-items-center gap-2">
              <span class="status-badge" :class="registration.status_code === 'checked_in' ? 'status-complete' : 'status-pending'">
                {{ statusLabel }}
              </span>
              <i class="bi" :class="sectionOpen.regInfo ? 'bi-chevron-up' : 'bi-chevron-down'" style="color: #718096;"></i>
            </div>
          </div>

          <div v-if="sectionOpen.regInfo">
            <div class="row g-3">
              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Status</label>
                <select class="form-select" v-model="regForm.status_code"
                  :class="{ 'is-invalid': sectionErrors.regInfo.status_code }">
                  <option v-for="s in STATUS_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
                <div class="invalid-feedback">{{ sectionErrors.regInfo.status_code }}</div>
              </div>

              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Guest Attending</label>
                <select class="form-select" v-model="regForm.guest_attending"
                  :class="{ 'is-invalid': sectionErrors.regInfo.guest_attending }">
                  <option v-for="g in GUEST_CHOICES" :key="String(g.value)" :value="g.value">{{ g.label }}</option>
                </select>
                <div class="invalid-feedback">{{ sectionErrors.regInfo.guest_attending }}</div>
              </div>

              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Recruiter Visibility</label>
                <select class="form-select" v-model="regForm.visible_to_recruiters"
                  :class="{ 'is-invalid': sectionErrors.regInfo.visible_to_recruiters }">
                  <option v-for="v in VISIBILITY_CHOICES" :key="v.value" :value="v.value">{{ v.label }}</option>
                </select>
                <div class="invalid-feedback">{{ sectionErrors.regInfo.visible_to_recruiters }}</div>
              </div>

              <div class="col-sm-6 col-lg-6">
                <label class="form-label">Contact Email</label>
                <input type="email" class="form-control" v-model="regForm.contact_email"
                  :class="{ 'is-invalid': sectionErrors.regInfo.contact_email }" />
                <div class="invalid-feedback">{{ sectionErrors.regInfo.contact_email }}</div>
              </div>

              <div class="col-12 d-flex gap-4 flex-wrap pt-1">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="paid" v-model="regForm.paid" />
                  <label class="form-check-label" for="paid">Paid</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="creds" v-model="regForm.credentials_received" />
                  <label class="form-check-label" for="creds">Credentials Received</label>
                </div>
              </div>

              <div class="col-12">
                <hr class="my-2" />
                <div class="fw-500 mb-3" style="color: #374151;">Emergency Contact</div>
              </div>

              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" v-model="regForm.emergency_contact_name"
                  :class="{ 'is-invalid': sectionErrors.regInfo.emergency_contact_name }" />
                <div class="invalid-feedback">{{ sectionErrors.regInfo.emergency_contact_name }}</div>
              </div>

              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Relationship</label>
                <input type="text" class="form-control" v-model="regForm.emergency_contact_relationship"
                  :class="{ 'is-invalid': sectionErrors.regInfo.emergency_contact_relationship }" />
                <div class="invalid-feedback">{{ sectionErrors.regInfo.emergency_contact_relationship }}</div>
              </div>

              <div class="col-sm-6 col-lg-4">
                <label class="form-label">Phone</label>
                <input type="text" class="form-control" v-model="regForm.emergency_contact_phone"
                  :class="{ 'is-invalid': sectionErrors.regInfo.emergency_contact_phone }" />
                <div class="invalid-feedback">{{ sectionErrors.regInfo.emergency_contact_phone }}</div>
              </div>
            </div>

            <div class="d-flex justify-content-end mt-4">
              <button class="btn btn-primary btn-sm px-4" :disabled="savingSection.regInfo" @click="saveRegInfo">
                <span v-if="savingSection.regInfo" class="spinner-border spinner-border-sm me-2" role="status"></span>
                Save Registration Info
              </button>
            </div>
          </div>
        </div>

        <!-- ── Travel Section ── -->
        <div class="section-card">
          <div class="section-header section-header-toggle" @click="toggleSection('travel')">
            <h2 class="section-title">
              <div class="section-icon">
                <i class="bi bi-airplane"></i>
              </div>
              Travel
            </h2>
            <div class="d-flex align-items-center gap-2">
              <span v-if="sectionLoaded.travel" class="status-badge"
                :class="travel.travel_method ? 'status-complete' : 'status-pending'">
                {{ travel.travel_method ? toTitleCase(travel.travel_method) : 'Not set' }}
              </span>
              <i class="bi" :class="sectionOpen.travel ? 'bi-chevron-up' : 'bi-chevron-down'" style="color: #718096;"></i>
            </div>
          </div>

          <div v-if="sectionOpen.travel">
            <div v-if="!sectionLoaded.travel" class="text-center py-4">
              <div class="spinner-border spinner-border-sm" role="status"></div>
            </div>

            <div v-else>
              <!-- Member-side fields -->
              <div class="row g-3 mb-4">
                <div class="col-sm-6 col-lg-4">
                  <label class="form-label">Travel Method</label>
                  <select class="form-select" v-model="travel.travel_method"
                    :class="{ 'is-invalid': sectionErrors.travel.travel_method }">
                    <option :value="null">— Select —</option>
                    <option v-for="t in TRAVEL_METHOD_CHOICES" :key="t.value" :value="t.value">{{ t.label }}</option>
                  </select>
                  <div class="invalid-feedback">{{ sectionErrors.travel.travel_method }}</div>
                </div>

                <template v-if="travel.travel_method === 'need_booking'">
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Departure Airport (code)</label>
                    <input type="text" class="form-control" maxlength="3" style="text-transform: uppercase;"
                      v-model="travel.departure_airport"
                      :class="{ 'is-invalid': sectionErrors.travel.departure_airport }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.departure_airport }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Departure Date</label>
                    <input type="date" class="form-control" v-model="travel.departure_date"
                      :class="{ 'is-invalid': sectionErrors.travel.departure_date }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.departure_date }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Departure Time Preference</label>
                    <select class="form-select" v-model="travel.departure_time_preference"
                      :class="{ 'is-invalid': sectionErrors.travel.departure_time_preference }">
                      <option :value="null">— Any time —</option>
                      <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                    </select>
                    <div class="invalid-feedback">{{ sectionErrors.travel.departure_time_preference }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Return Airport (code)</label>
                    <input type="text" class="form-control" maxlength="3" style="text-transform: uppercase;"
                      v-model="travel.return_airport"
                      :class="{ 'is-invalid': sectionErrors.travel.return_airport }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_airport }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Return Date</label>
                    <input type="date" class="form-control" v-model="travel.return_date"
                      :class="{ 'is-invalid': sectionErrors.travel.return_date }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_date }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Return Time Preference</label>
                    <select class="form-select" v-model="travel.return_time_preference"
                      :class="{ 'is-invalid': sectionErrors.travel.return_time_preference }">
                      <option :value="null">— Any time —</option>
                      <option v-for="t in timeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
                    </select>
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_time_preference }}</div>
                  </div>

                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Seat Preference</label>
                    <select class="form-select" v-model="travel.seat_preference"
                      :class="{ 'is-invalid': sectionErrors.travel.seat_preference }">
                      <option v-for="s in SEAT_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
                    </select>
                    <div class="invalid-feedback">{{ sectionErrors.travel.seat_preference }}</div>
                  </div>

                  <div class="col-12">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" id="ground_transport" v-model="travel.needs_ground_transportation" />
                      <label class="form-check-label" for="ground_transport">Needs Ground Transportation</label>
                    </div>
                  </div>
                </template>

                <template v-else-if="travel.travel_method">
                  <div class="col-12">
                    <div class="info-alert">
                      <i class="bi bi-info-circle"></i>
                      <div class="info-alert-content">
                        This registrant is {{ travel.travel_method === 'driving' ? 'driving' : 'booking their own flights' }}. No flight booking information is needed.
                      </div>
                    </div>
                  </div>
                </template>
              </div>

              <!-- Staff-only: Booked Flight Details -->
              <div class="staff-subsection">
                <div class="staff-subsection-title">
                  <i class="bi bi-shield-check me-2"></i>Booked Flight Details (Staff)
                </div>

                <div class="row g-3">
                  <div class="col-12">
                    <div class="fw-500 mb-2" style="color: #374151; font-size: 0.9rem;">Outbound Flight</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Airline</label>
                    <input type="text" class="form-control" v-model="travel.outbound_airline"
                      :class="{ 'is-invalid': sectionErrors.travel.outbound_airline }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.outbound_airline }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Flight Number</label>
                    <input type="text" class="form-control" v-model="travel.outbound_flight_number"
                      :class="{ 'is-invalid': sectionErrors.travel.outbound_flight_number }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.outbound_flight_number }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Confirmation</label>
                    <input type="text" class="form-control" v-model="travel.outbound_confirmation"
                      :class="{ 'is-invalid': sectionErrors.travel.outbound_confirmation }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.outbound_confirmation }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Departure Time</label>
                    <input type="datetime-local" class="form-control" v-model="travel.outbound_departure_time"
                      :class="{ 'is-invalid': sectionErrors.travel.outbound_departure_time }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.outbound_departure_time }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Arrival Time</label>
                    <input type="datetime-local" class="form-control" v-model="travel.outbound_arrival_time"
                      :class="{ 'is-invalid': sectionErrors.travel.outbound_arrival_time }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.outbound_arrival_time }}</div>
                  </div>

                  <div class="col-12 pt-2">
                    <div class="fw-500 mb-2" style="color: #374151; font-size: 0.9rem;">Return Flight</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Airline</label>
                    <input type="text" class="form-control" v-model="travel.return_airline"
                      :class="{ 'is-invalid': sectionErrors.travel.return_airline }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_airline }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Flight Number</label>
                    <input type="text" class="form-control" v-model="travel.return_flight_number"
                      :class="{ 'is-invalid': sectionErrors.travel.return_flight_number }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_flight_number }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Confirmation</label>
                    <input type="text" class="form-control" v-model="travel.return_confirmation"
                      :class="{ 'is-invalid': sectionErrors.travel.return_confirmation }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_confirmation }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Departure Time</label>
                    <input type="datetime-local" class="form-control" v-model="travel.return_departure_time"
                      :class="{ 'is-invalid': sectionErrors.travel.return_departure_time }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_departure_time }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Arrival Time</label>
                    <input type="datetime-local" class="form-control" v-model="travel.return_arrival_time"
                      :class="{ 'is-invalid': sectionErrors.travel.return_arrival_time }" />
                    <div class="invalid-feedback">{{ sectionErrors.travel.return_arrival_time }}</div>
                  </div>

                  <div class="col-12">
                    <label class="form-label">Flight Notes</label>
                    <textarea class="form-control" rows="2" v-model="travel.flight_notes"
                      :class="{ 'is-invalid': sectionErrors.travel.flight_notes }"></textarea>
                    <div class="invalid-feedback">{{ sectionErrors.travel.flight_notes }}</div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end mt-4">
                <button class="btn btn-primary btn-sm px-4" :disabled="savingSection.travel" @click="saveTravel">
                  <span v-if="savingSection.travel" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Save Travel
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Accommodation Section ── -->
        <div class="section-card">
          <div class="section-header section-header-toggle" @click="toggleSection('accommodation')">
            <h2 class="section-title">
              <div class="section-icon gold">
                <i class="bi bi-building"></i>
              </div>
              Accommodation
            </h2>
            <div class="d-flex align-items-center gap-2">
              <span v-if="sectionLoaded.accommodation" class="status-badge"
                :class="accommodation.package_choice ? 'status-complete' : 'status-pending'">
                {{ accommodation.package_choice ? toTitleCase(accommodation.package_choice) : 'Not set' }}
              </span>
              <i class="bi" :class="sectionOpen.accommodation ? 'bi-chevron-up' : 'bi-chevron-down'" style="color: #718096;"></i>
            </div>
          </div>

          <div v-if="sectionOpen.accommodation">
            <div v-if="!sectionLoaded.accommodation" class="text-center py-4">
              <div class="spinner-border spinner-border-sm" role="status"></div>
            </div>

            <div v-else>
              <div class="row g-3 mb-4">
                <div class="col-sm-6 col-lg-4">
                  <label class="form-label">Package Choice</label>
                  <select class="form-select" v-model="accommodation.package_choice"
                    :class="{ 'is-invalid': sectionErrors.accommodation.package_choice }">
                    <option :value="null">— Select —</option>
                    <option v-for="p in PACKAGE_CHOICES" :key="p.value" :value="p.value">{{ p.label }}</option>
                  </select>
                  <div class="invalid-feedback">{{ sectionErrors.accommodation.package_choice }}</div>
                </div>

                <div class="col-sm-6 col-lg-4 d-flex align-items-end pb-1">
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="needs_hotel" v-model="accommodation.needs_hotel" />
                    <label class="form-check-label" for="needs_hotel">Needs Hotel</label>
                  </div>
                </div>

                <template v-if="accommodation.needs_hotel">
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Check-In Date</label>
                    <input type="date" class="form-control" v-model="accommodation.check_in_date"
                      :class="{ 'is-invalid': sectionErrors.accommodation.check_in_date }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.check_in_date }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Check-Out Date</label>
                    <input type="date" class="form-control" v-model="accommodation.check_out_date"
                      :class="{ 'is-invalid': sectionErrors.accommodation.check_out_date }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.check_out_date }}</div>
                  </div>
                </template>

                <div class="col-sm-6 col-lg-4">
                  <label class="form-label">Roommate Preference</label>
                  <select class="form-select" v-model="accommodation.roommate_preference"
                    :class="{ 'is-invalid': sectionErrors.accommodation.roommate_preference }">
                    <option :value="null">— Select —</option>
                    <option v-for="r in ROOMMATE_CHOICES" :key="r.value" :value="r.value">{{ r.label }}</option>
                  </select>
                  <div class="invalid-feedback">{{ sectionErrors.accommodation.roommate_preference }}</div>
                </div>

                <template v-if="accommodation.roommate_preference === 'specific'">
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Specific Roommate Name</label>
                    <input type="text" class="form-control" v-model="accommodation.specific_roommate_name"
                      :class="{ 'is-invalid': sectionErrors.accommodation.specific_roommate_name }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.specific_roommate_name }}</div>
                  </div>
                  <div class="col-sm-6 col-lg-4">
                    <label class="form-label">Roommate Chapter</label>
                    <input type="text" class="form-control" v-model="accommodation.specific_roommate_chapter"
                      :class="{ 'is-invalid': sectionErrors.accommodation.specific_roommate_chapter }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.specific_roommate_chapter }}</div>
                  </div>
                </template>

                <div class="col-12">
                  <label class="form-label">Food Allergies</label>
                  <div class="d-flex flex-wrap gap-3">
                    <div v-for="opt in ALLERGY_OPTIONS" :key="opt.value" class="form-check">
                      <input class="form-check-input" type="checkbox" :id="`allergy_${opt.value}`"
                        :checked="hasAllergy(opt.value)" @change="toggleAllergy(opt.value)" />
                      <label class="form-check-label" :for="`allergy_${opt.value}`">{{ opt.label }}</label>
                    </div>
                  </div>
                  <input type="text" class="form-control mt-2" placeholder="Other allergy..."
                    v-model="accommodation.other_allergies"
                    :class="{ 'is-invalid': sectionErrors.accommodation.other_allergies }" />
                  <div class="invalid-feedback">{{ sectionErrors.accommodation.other_allergies }}</div>
                </div>

                <div class="col-12">
                  <label class="form-label">Dietary Restrictions</label>
                  <div class="d-flex flex-wrap gap-3">
                    <div v-for="opt in DIETARY_OPTIONS" :key="opt.value" class="form-check">
                      <input class="form-check-input" type="checkbox" :id="`diet_${opt.value}`"
                        :checked="hasDietary(opt.value)" @change="toggleDietary(opt.value)" />
                      <label class="form-check-label" :for="`diet_${opt.value}`">{{ opt.label }}</label>
                    </div>
                  </div>
                  <input type="text" class="form-control mt-2" placeholder="Other restriction..."
                    v-model="accommodation.dietary_restrictions_other"
                    :class="{ 'is-invalid': sectionErrors.accommodation.dietary_restrictions_other }" />
                  <div class="invalid-feedback">{{ sectionErrors.accommodation.dietary_restrictions_other }}</div>
                </div>

                <div class="col-12">
                  <label class="form-label">Special Requests</label>
                  <textarea class="form-control" rows="3" v-model="accommodation.special_requests"
                    :class="{ 'is-invalid': sectionErrors.accommodation.special_requests }"></textarea>
                  <div class="invalid-feedback">{{ sectionErrors.accommodation.special_requests }}</div>
                </div>
              </div>

              <!-- Staff-only: Room Assignment -->
              <div class="staff-subsection staff-subsection--green">
                <div class="staff-subsection-title staff-subsection-title--green">
                  <i class="bi bi-shield-check me-2"></i>Room Assignment (Staff)
                </div>
                <div class="row g-3">
                  <div class="col-sm-6">
                    <label class="form-label">Room Number</label>
                    <input type="text" class="form-control" v-model="accommodation.room_number"
                      :class="{ 'is-invalid': sectionErrors.accommodation.room_number }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.room_number }}</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label">Room Confirmation</label>
                    <input type="text" class="form-control" v-model="accommodation.room_confirmation"
                      :class="{ 'is-invalid': sectionErrors.accommodation.room_confirmation }" />
                    <div class="invalid-feedback">{{ sectionErrors.accommodation.room_confirmation }}</div>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-end mt-4">
                <button class="btn btn-primary btn-sm px-4" :disabled="savingSection.accommodation" @click="saveAccommodation">
                  <span v-if="savingSection.accommodation" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Save Accommodation
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Committee Preferences Section ── -->
        <div class="section-card">
          <div class="section-header section-header-toggle" @click="toggleSection('committee')">
            <h2 class="section-title">
              <div class="section-icon">
                <i class="bi bi-people"></i>
              </div>
              Committee Preferences
            </h2>
            <i class="bi" :class="sectionOpen.committee ? 'bi-chevron-up' : 'bi-chevron-down'" style="color: #718096;"></i>
          </div>

          <div v-if="sectionOpen.committee">
            <div v-if="!sectionLoaded.committee" class="text-center py-4">
              <div class="spinner-border spinner-border-sm" role="status"></div>
            </div>

            <div v-else>
              <div class="row g-3">
                <div v-for="field in COMMITTEE_FIELDS" :key="field" class="col-sm-6 col-lg-4">
                  <label class="form-label">{{ toTitleCase(field) }}</label>
                  <select class="form-select" v-model="committee[field]"
                    :class="{ 'is-invalid': sectionErrors.committee[field] }">
                    <option v-for="(label, val) in COMMITTEE_PREF_LABELS" :key="val" :value="Number(val)">{{ label }}</option>
                  </select>
                  <div class="invalid-feedback">{{ sectionErrors.committee[field] }}</div>
                </div>
              </div>

              <div class="d-flex justify-content-end mt-4">
                <button class="btn btn-primary btn-sm px-4" :disabled="savingSection.committee" @click="saveCommittee">
                  <span v-if="savingSection.committee" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Save Preferences
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Guests Section ── -->
        <div class="section-card">
          <div class="section-header section-header-toggle" @click="toggleSection('guests')">
            <h2 class="section-title">
              <div class="section-icon gold">
                <i class="bi bi-person-plus"></i>
              </div>
              Guests
            </h2>
            <div class="d-flex align-items-center gap-2">
              <span v-if="sectionLoaded.guests" class="status-badge"
                :class="guests.length > 0 ? 'status-complete' : 'status-pending'">
                {{ guests.length }} guest{{ guests.length !== 1 ? 's' : '' }}
              </span>
              <i class="bi" :class="sectionOpen.guests ? 'bi-chevron-up' : 'bi-chevron-down'" style="color: #718096;"></i>
            </div>
          </div>

          <div v-if="sectionOpen.guests">
            <div v-if="!sectionLoaded.guests" class="text-center py-4">
              <div class="spinner-border spinner-border-sm" role="status"></div>
            </div>

            <div v-else>
              <!-- Guest list -->
              <div v-for="guest in guests" :key="guest.id" class="guest-card mb-3">
                <!-- Edit mode -->
                <template v-if="editingGuestId === guest.id">
                  <div class="row g-3">
                    <div class="col-sm-6">
                      <label class="form-label">First Name *</label>
                      <input type="text" class="form-control" v-model="editGuestForm.guest_first_name"
                        :class="{ 'is-invalid': editGuestErrors.guest_first_name }" />
                      <div class="invalid-feedback">{{ editGuestErrors.guest_first_name }}</div>
                    </div>
                    <div class="col-sm-6">
                      <label class="form-label">Last Name *</label>
                      <input type="text" class="form-control" v-model="editGuestForm.guest_last_name"
                        :class="{ 'is-invalid': editGuestErrors.guest_last_name }" />
                      <div class="invalid-feedback">{{ editGuestErrors.guest_last_name }}</div>
                    </div>
                    <div class="col-sm-6">
                      <label class="form-label">Email</label>
                      <input type="email" class="form-control" v-model="editGuestForm.guest_email"
                        :class="{ 'is-invalid': editGuestErrors.guest_email }" />
                      <div class="invalid-feedback">{{ editGuestErrors.guest_email }}</div>
                    </div>
                    <div class="col-sm-6">
                      <label class="form-label">Phone</label>
                      <input type="text" class="form-control" v-model="editGuestForm.guest_phone"
                        :class="{ 'is-invalid': editGuestErrors.guest_phone }" />
                      <div class="invalid-feedback">{{ editGuestErrors.guest_phone }}</div>
                    </div>
                    <div class="col-12 d-flex gap-2 justify-content-end">
                      <button class="btn btn-secondary btn-sm" @click="cancelEditGuest">Cancel</button>
                      <button class="btn btn-primary btn-sm" :disabled="savingEditGuest" @click="saveEditGuest(guest.id)">
                        <span v-if="savingEditGuest" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        Save
                      </button>
                    </div>
                  </div>
                </template>

                <!-- View mode -->
                <template v-else>
                  <div class="d-flex justify-content-between align-items-start">
                    <div>
                      <div class="fw-600">{{ guest.guest_first_name }} {{ guest.guest_last_name }}</div>
                      <div v-if="guest.guest_email" class="text-muted" style="font-size: 0.875rem;">{{ guest.guest_email }}</div>
                      <div v-if="guest.guest_phone" class="text-muted" style="font-size: 0.875rem;">{{ guest.guest_phone }}</div>
                    </div>
                    <div class="d-flex gap-2">
                      <button class="btn btn-secondary btn-sm" @click="startEditGuest(guest)">
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger"
                        :disabled="deletingGuestId === guest.id"
                        @click="deleteGuest(guest.id)">
                        <span v-if="deletingGuestId === guest.id" class="spinner-border spinner-border-sm" role="status"></span>
                        <i v-else class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                </template>
              </div>

              <div v-if="guests.length === 0 && !addingGuest" class="text-muted fst-italic mb-3">
                No guests added.
              </div>

              <!-- Add Guest inline form -->
              <div v-if="addingGuest" class="guest-card guest-card--add mb-3">
                <div class="fw-600 mb-3" style="color: #374151;">New Guest</div>
                <div class="row g-3">
                  <div class="col-sm-6">
                    <label class="form-label">First Name *</label>
                    <input type="text" class="form-control" v-model="newGuestForm.guest_first_name"
                      :class="{ 'is-invalid': newGuestErrors.guest_first_name }" />
                    <div class="invalid-feedback">{{ newGuestErrors.guest_first_name }}</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label">Last Name *</label>
                    <input type="text" class="form-control" v-model="newGuestForm.guest_last_name"
                      :class="{ 'is-invalid': newGuestErrors.guest_last_name }" />
                    <div class="invalid-feedback">{{ newGuestErrors.guest_last_name }}</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" v-model="newGuestForm.guest_email"
                      :class="{ 'is-invalid': newGuestErrors.guest_email }" />
                    <div class="invalid-feedback">{{ newGuestErrors.guest_email }}</div>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label">Phone</label>
                    <input type="text" class="form-control" v-model="newGuestForm.guest_phone"
                      :class="{ 'is-invalid': newGuestErrors.guest_phone }" />
                    <div class="invalid-feedback">{{ newGuestErrors.guest_phone }}</div>
                  </div>
                  <div class="col-12 d-flex gap-2 justify-content-end">
                    <button class="btn btn-secondary btn-sm" @click="cancelAddGuest">Cancel</button>
                    <button class="btn btn-primary btn-sm" :disabled="savingGuest" @click="saveNewGuest">
                      <span v-if="savingGuest" class="spinner-border spinner-border-sm me-1" role="status"></span>
                      Add Guest
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="!addingGuest">
                <button class="btn btn-secondary btn-sm" @click="startAddGuest">
                  <i class="bi bi-plus me-1"></i>Add Guest
                </button>
              </div>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<style scoped>
.section-header-toggle {
  cursor: pointer;
  user-select: none;
}

.section-header {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-card:has(.section-header-toggle) .section-header {
  padding-bottom: 0;
  border-bottom: none;
}

.section-header-toggle + div {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f1f5f9;
}

.status-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-complete {
  background: #d1fae5;
  color: #065f46;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

.fw-500 {
  font-weight: 500;
}

.fw-600 {
  font-weight: 600;
}

/* Staff subsection - blue tint */
.staff-subsection {
  background: #f0f5ff;
  border: 1px solid #c7d9f8;
  border-radius: 10px;
  padding: 1.25rem;
  margin-top: 0.5rem;
}

.staff-subsection-title {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--brand-blue);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

/* Staff subsection - green tint */
.staff-subsection--green {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.staff-subsection-title--green {
  color: #166534;
}

/* Guest cards */
.guest-card {
  background: #fafbfc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
}

.guest-card--add {
  background: #f0f5ff;
  border-color: #c7d9f8;
}

.btn-outline-danger {
  border: 1.5px solid #fca5a5;
  color: #dc2626;
  background: transparent;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-outline-danger:hover:not(:disabled) {
  background: #fef2f2;
  border-color: #ef4444;
}

.btn-outline-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
