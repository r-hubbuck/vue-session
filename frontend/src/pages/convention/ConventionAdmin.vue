<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '../../api'

const router = useRouter()

const toast = useToast()

// ── State ──────────────────────────────────────────────────────────────────
const registrations = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const searchQuery = ref('')
const statusFilter = ref('')

// Edit modal
const selectedRegistration = ref(null)
const editForm = ref({})
const editErrors = ref({})
const savingEdit = ref(false)
const loadingDetail = ref(false)
const sendingTermsEmail = ref(false)

// Create modal
const createTab = ref('search') // 'search' | 'new-person'
const personSearchQuery = ref('')
const personSearchResults = ref([])
const personSearchLoading = ref(false)
const selectedPerson = ref(null)
const createStatusCode = ref('registered')
const newPersonForm = ref({ first_name: '', last_name: '', preferred_first_name: '', contact_email: '', status_code: 'registered' })
const newPersonErrors = ref({})
const creating = ref(false)

let personSearchTimeout = null

const STATUS_CHOICES = [
  { value: 'registered', label: 'Registered' },
  { value: 'checked_in', label: 'Checked In' },
  { value: 'cancelled',  label: 'Cancelled' },
]

const VISIBILITY_CHOICES = [
  { value: 'none',            label: 'None' },
  { value: 'business',        label: 'Business' },
  { value: 'graduate_school', label: 'Graduate School' },
  { value: 'both',            label: 'Both' },
]

// ── Computed ───────────────────────────────────────────────────────────────
const filteredRegistrations = computed(() => {
  let list = registrations.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    list = list.filter(r => {
      const name = `${r.person.first_name} ${r.person.last_name}`.toLowerCase()
      const memberId = String(r.person.member_id ?? '').toLowerCase()
      const email = (r.person.email ?? '').toLowerCase()
      return name.includes(q) || memberId.includes(q) || email.includes(q)
    })
  }
  if (statusFilter.value) {
    list = list.filter(r => r.status_code === statusFilter.value)
  }
  return list.slice().sort((a, b) => {
    const la = a.person.last_name.toLowerCase()
    const lb = b.person.last_name.toLowerCase()
    return la < lb ? -1 : la > lb ? 1 : 0
  })
})

// ── Load ───────────────────────────────────────────────────────────────────
async function loadRegistrations() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/api/convention/admin/registrations/')
    registrations.value = res.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load registrations.'
  } finally {
    loading.value = false
  }
}

onMounted(loadRegistrations)

// ── Helpers ────────────────────────────────────────────────────────────────
function getStatusBadgeClass(status) {
  return {
    registered: 'bg-primary',
    checked_in: 'bg-info text-dark',
    cancelled:  'bg-secondary',
  }[status] || 'bg-secondary'
}

function getRowClass(status) {
  if (status === 'checked_in') return 'table-success'
  if (status === 'cancelled')  return 'table-secondary'
  return ''
}

function displayName(person) {
  const first = person.preferred_first_name || person.first_name
  return `${first} ${person.last_name}`
}

function showModal(id) {
  nextTick(() => {
    const el = document.getElementById(id)
    if (!el) return
    const m = window.bootstrap?.Modal?.getInstance(el) || new window.bootstrap.Modal(el)
    m.show()
  })
}

function hideModal(id) {
  const el = document.getElementById(id)
  if (!el) return
  window.bootstrap?.Modal?.getInstance(el)?.hide()
}

// ── Edit modal ─────────────────────────────────────────────────────────────
async function openEditModal(reg) {
  editErrors.value = {}
  savingEdit.value = false
  selectedRegistration.value = null
  loadingDetail.value = true
  showModal('editRegistrationModal')

  try {
    const res = await api.get(`/api/convention/admin/registrations/${reg.id}/`)
    selectedRegistration.value = res.data
    editForm.value = {
      status_code:                    res.data.status_code,
      paid:                           res.data.paid,
      credentials_received:           res.data.credentials_received,
      visible_to_recruiters:          res.data.visible_to_recruiters,
      guest_attending:                res.data.guest_attending,
      contact_email:                  res.data.contact_email || '',
      emergency_contact_name:         res.data.emergency_contact_name || '',
      emergency_contact_relationship: res.data.emergency_contact_relationship || '',
      emergency_contact_phone:        res.data.emergency_contact_phone || '',
    }
  } catch (err) {
    toast.error('Failed to load registration details.')
    hideModal('editRegistrationModal')
  } finally {
    loadingDetail.value = false
  }
}

async function saveEdit() {
  if (!selectedRegistration.value) return
  savingEdit.value = true
  editErrors.value = {}
  try {
    await api.put(`/api/convention/admin/registrations/${selectedRegistration.value.id}/`, editForm.value)
    toast.success('Registration updated.')
    hideModal('editRegistrationModal')
    await loadRegistrations()
  } catch (err) {
    if (err.response?.data && typeof err.response.data === 'object') {
      editErrors.value = err.response.data
    } else {
      toast.error(err.response?.data?.error || 'Failed to save changes.')
    }
  } finally {
    savingEdit.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
async function deleteRegistration(reg, event) {
  event.stopPropagation()
  if (!confirm('Delete this registration? This cannot be undone.')) return
  try {
    await api.delete(`/api/convention/admin/registrations/${reg.id}/`)
    registrations.value = registrations.value.filter(r => r.id !== reg.id)
    toast.success('Registration deleted.')
  } catch (err) {
    toast.error(err.response?.data?.error || 'Failed to delete registration.')
  }
}

// ── Create modal ───────────────────────────────────────────────────────────
function openCreateModal() {
  createTab.value = 'search'
  personSearchQuery.value = ''
  personSearchResults.value = []
  selectedPerson.value = null
  createStatusCode.value = 'registered'
  newPersonForm.value = { first_name: '', last_name: '', preferred_first_name: '', contact_email: '', status_code: 'registered' }
  newPersonErrors.value = {}
  creating.value = false
  showModal('createRegistrationModal')
}

function onPersonSearchInput() {
  selectedPerson.value = null
  clearTimeout(personSearchTimeout)
  if (personSearchQuery.value.trim().length < 2) {
    personSearchResults.value = []
    return
  }
  personSearchTimeout = setTimeout(async () => {
    personSearchLoading.value = true
    try {
      const res = await api.get('/api/convention/admin/person-search/', {
        params: { q: personSearchQuery.value.trim() }
      })
      personSearchResults.value = res.data
    } catch {
      personSearchResults.value = []
    } finally {
      personSearchLoading.value = false
    }
  }, 350)
}

function selectPerson(person) {
  selectedPerson.value = person
  personSearchQuery.value = `${person.first_name} ${person.last_name}`
  personSearchResults.value = []
}

async function createFromExistingPerson() {
  if (!selectedPerson.value) return
  creating.value = true
  try {
    const res = await api.post('/api/convention/admin/registrations/', {
      person_id: selectedPerson.value.id,
      status_code: createStatusCode.value,
    })
    registrations.value.push(res.data)
    toast.success('Registration created.')
    hideModal('createRegistrationModal')
  } catch (err) {
    toast.error(err.response?.data?.error || 'Failed to create registration.')
  } finally {
    creating.value = false
  }
}

async function createNewPerson() {
  newPersonErrors.value = {}
  const { first_name, last_name, preferred_first_name, contact_email, status_code } = newPersonForm.value
  if (!first_name.trim()) { newPersonErrors.value.first_name = 'First name is required.'; return }
  if (!last_name.trim())  { newPersonErrors.value.last_name  = 'Last name is required.';  return }
  creating.value = true
  try {
    const res = await api.post('/api/convention/admin/registrations/', {
      is_new_person: true,
      first_name: first_name.trim(),
      last_name: last_name.trim(),
      preferred_first_name: preferred_first_name.trim(),
      contact_email: contact_email.trim(),
      status_code,
    })
    registrations.value.push(res.data)
    toast.success('Registration created.')
    hideModal('createRegistrationModal')
  } catch (err) {
    toast.error(err.response?.data?.error || 'Failed to create registration.')
  } finally {
    creating.value = false
  }
}

// ── Terms email ────────────────────────────────────────────────────────────
async function sendTermsEmail() {
  if (!selectedRegistration.value) return
  sendingTermsEmail.value = true
  try {
    await api.post(`/api/convention/admin/registrations/${selectedRegistration.value.id}/send-terms-email/`)
    toast.success('Terms agreement email sent.')
  } catch (err) {
    toast.error(err.response?.data?.error || 'Failed to send email.')
  } finally {
    sendingTermsEmail.value = false
  }
}

// ── Accordion helpers ──────────────────────────────────────────────────────
function formatStatus(code) {
  const s = code.replace('_', ' ')
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function travelMethodLabel(method) {
  return { driving: 'Driving', self_booking: 'Self-booking', need_booking: 'Needs HQ booking' }[method] || method
}
</script>

<template>
  <div>
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Registration Admin</h1>
        <p class="page-subtitle">View, manage, and create convention registrations.</p>
      </div>
    </div>

    <div class="content-container">

      <!-- Alerts -->
      <div v-if="error" class="alert alert-danger alert-dismissible mb-3" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>
      <div v-if="success" class="alert alert-success alert-dismissible mb-3" role="alert">
        {{ success }}
        <button type="button" class="btn-close" @click="success = ''"></button>
      </div>

      <!-- Toolbar -->
      <div class="d-flex flex-wrap gap-2 align-items-center mb-3">
        <input
          v-model="searchQuery"
          type="search"
          class="form-control"
          style="max-width: 280px;"
          placeholder="Search name, member ID, email…"
        />
        <select v-model="statusFilter" class="form-select" style="max-width: 180px;">
          <option value="">All Statuses</option>
          <option v-for="s in STATUS_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
        <span class="text-muted small ms-1">{{ filteredRegistrations.length }} registration{{ filteredRegistrations.length !== 1 ? 's' : '' }}</span>
        <button class="btn btn-primary ms-auto" @click="openCreateModal">
          <i class="bi bi-plus-lg me-1"></i>Register Person
        </button>
      </div>

      <!-- Table -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else-if="filteredRegistrations.length === 0" class="text-center py-5 text-muted">
        <i class="bi bi-person-x fs-1 d-block mb-2"></i>
        No registrations found.
      </div>

      <div v-else class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Member ID</th>
              <th>Status</th>
              <th>Registered</th>
              <th>Paid</th>
              <th>Credentials</th>
              <th>Travel</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="reg in filteredRegistrations"
              :key="reg.id"
              :class="getRowClass(reg.status_code)"
              style="cursor: pointer;"
              @click="router.push(`/convention-admin/${reg.id}`)"
            >
              <td>
                <div class="fw-medium text-primary">{{ displayName(reg.person) }}</div>
                <div v-if="reg.person.email" class="text-muted small">{{ reg.person.email }}</div>
              </td>
              <td>{{ reg.person.member_id ?? '—' }}</td>
              <td>
                <span class="badge" :class="getStatusBadgeClass(reg.status_code)">
                  {{ formatStatus(reg.status_code) }}
                </span>
              </td>
              <td class="text-nowrap small">{{ new Date(reg.registration_date).toLocaleDateString() }}</td>
              <td>
                <i v-if="reg.paid" class="bi bi-check-circle-fill text-success"></i>
                <i v-else class="bi bi-dash text-muted"></i>
              </td>
              <td>
                <i v-if="reg.credentials_received" class="bi bi-check-circle-fill text-success"></i>
                <i v-else class="bi bi-dash text-muted"></i>
              </td>
              <td>
                <span v-if="reg.travel_booked" class="badge bg-success">Booked</span>
                <span v-else-if="reg.has_travel" class="badge bg-warning text-dark">Pending</span>
                <span v-else class="text-muted small">—</span>
              </td>
              <td @click.stop>
                <button
                  class="btn btn-sm btn-outline-danger"
                  title="Delete registration"
                  @click="deleteRegistration(reg, $event)"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── Edit / View Modal ─────────────────────────────────────────────── -->
    <div id="editRegistrationModal" class="modal fade" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editModalLabel">
              <span v-if="selectedRegistration">
                {{ displayName(selectedRegistration.person) }}
              </span>
              <span v-else>Registration Detail</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">
            <!-- Loading -->
            <div v-if="loadingDetail" class="text-center py-4">
              <div class="spinner-border text-primary" role="status"></div>
            </div>

            <div v-else-if="selectedRegistration">
              <!-- Person summary -->
              <div class="bg-light rounded p-3 mb-4">
                <div class="row g-2">
                  <div class="col-sm-4">
                    <div class="small text-muted">Name</div>
                    <div class="fw-medium">{{ selectedRegistration.person.first_name }} {{ selectedRegistration.person.last_name }}</div>
                    <div v-if="selectedRegistration.person.preferred_first_name" class="text-muted small">
                      Goes by: {{ selectedRegistration.person.preferred_first_name }}
                    </div>
                  </div>
                  <div class="col-sm-4">
                    <div class="small text-muted">Email</div>
                    <div>{{ selectedRegistration.person.email || '—' }}</div>
                  </div>
                  <div class="col-sm-4">
                    <div class="small text-muted">Member ID</div>
                    <div>{{ selectedRegistration.person.member_id ?? 'Non-member' }}</div>
                  </div>
                </div>
              </div>

              <div class="row g-4">
                <!-- Left: editable fields -->
                <div class="col-lg-6">
                  <h6 class="text-uppercase text-muted small fw-bold mb-3">Registration Fields</h6>

                  <div class="mb-3">
                    <label class="form-label fw-medium">Status</label>
                    <select v-model="editForm.status_code" class="form-select" :class="{ 'is-invalid': editErrors.status_code }">
                      <option v-for="s in STATUS_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
                    </select>
                    <div v-if="editErrors.status_code" class="invalid-feedback">{{ editErrors.status_code }}</div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-medium">Recruiter Visibility</label>
                    <select v-model="editForm.visible_to_recruiters" class="form-select">
                      <option v-for="v in VISIBILITY_CHOICES" :key="v.value" :value="v.value">{{ v.label }}</option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-medium">Guest Attending</label>
                    <select v-model="editForm.guest_attending" class="form-select">
                      <option :value="null">Undecided</option>
                      <option :value="true">Yes</option>
                      <option :value="false">No</option>
                    </select>
                  </div>

                  <div class="d-flex gap-4 mb-3">
                    <div class="form-check">
                      <input id="editPaid" v-model="editForm.paid" type="checkbox" class="form-check-input" />
                      <label for="editPaid" class="form-check-label">Paid</label>
                    </div>
                    <div class="form-check">
                      <input id="editCreds" v-model="editForm.credentials_received" type="checkbox" class="form-check-input" />
                      <label for="editCreds" class="form-check-label">Credentials Received</label>
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-medium">Contact Email</label>
                    <input v-model="editForm.contact_email" type="email" class="form-control" :class="{ 'is-invalid': editErrors.contact_email }" placeholder="For non-member attendees" />
                    <div v-if="editErrors.contact_email" class="invalid-feedback">{{ editErrors.contact_email }}</div>
                  </div>

                  <div class="mb-3">
                    <div class="d-flex align-items-center justify-content-between gap-2 flex-wrap">
                      <div>
                        <span class="form-label fw-medium d-block mb-0">Terms Agreement</span>
                        <span v-if="selectedRegistration.terms_agreed" class="text-success small">
                          <i class="bi bi-check-circle-fill me-1"></i>Agreed {{ selectedRegistration.terms_agreed_at ? new Date(selectedRegistration.terms_agreed_at).toLocaleDateString() : '' }}
                        </span>
                        <span v-else class="text-warning small">
                          <i class="bi bi-clock me-1"></i>Not yet agreed
                        </span>
                      </div>
                      <button
                        v-if="!selectedRegistration.terms_agreed && editForm.contact_email"
                        type="button"
                        class="btn btn-sm btn-outline-primary"
                        :disabled="sendingTermsEmail"
                        @click="sendTermsEmail"
                      >
                        <span v-if="sendingTermsEmail" class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-envelope me-1"></i>
                        Send Terms Email
                      </button>
                      <span v-else-if="!selectedRegistration.terms_agreed && !editForm.contact_email" class="text-muted small">
                        Add a contact email to send terms link.
                      </span>
                    </div>
                  </div>

                  <h6 class="text-uppercase text-muted small fw-bold mt-4 mb-3">Emergency Contact</h6>

                  <div class="mb-2">
                    <label class="form-label">Name</label>
                    <input v-model="editForm.emergency_contact_name" type="text" class="form-control" :class="{ 'is-invalid': editErrors.emergency_contact_name }" />
                    <div v-if="editErrors.emergency_contact_name" class="invalid-feedback">{{ editErrors.emergency_contact_name }}</div>
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Relationship</label>
                    <input v-model="editForm.emergency_contact_relationship" type="text" class="form-control" :class="{ 'is-invalid': editErrors.emergency_contact_relationship }" />
                    <div v-if="editErrors.emergency_contact_relationship" class="invalid-feedback">{{ editErrors.emergency_contact_relationship }}</div>
                  </div>
                  <div class="mb-2">
                    <label class="form-label">Phone</label>
                    <input v-model="editForm.emergency_contact_phone" type="text" class="form-control" :class="{ 'is-invalid': editErrors.emergency_contact_phone }" />
                    <div v-if="editErrors.emergency_contact_phone" class="invalid-feedback">{{ editErrors.emergency_contact_phone }}</div>
                  </div>
                </div>

                <!-- Right: read-only sub-model accordion -->
                <div class="col-lg-6">
                  <h6 class="text-uppercase text-muted small fw-bold mb-3">Registration Details</h6>

                  <div class="accordion accordion-flush" id="editAccordion">

                    <!-- Travel -->
                    <div class="accordion-item border rounded mb-2">
                      <h2 class="accordion-header">
                        <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#accTravel">
                          <i class="bi bi-airplane me-2"></i>Travel
                          <span v-if="selectedRegistration.travel?.outbound_flight_number" class="badge bg-success ms-2 small">Booked</span>
                          <span v-else-if="selectedRegistration.travel" class="badge bg-warning text-dark ms-2 small">Pending</span>
                          <span v-else class="badge bg-secondary ms-2 small">None</span>
                        </button>
                      </h2>
                      <div id="accTravel" class="accordion-collapse collapse">
                        <div class="accordion-body small">
                          <template v-if="selectedRegistration.travel">
                            <div><strong>Method:</strong> {{ travelMethodLabel(selectedRegistration.travel.travel_method) }}</div>
                            <div v-if="selectedRegistration.travel.departure_airport"><strong>Departure:</strong> {{ selectedRegistration.travel.departure_airport }} — {{ selectedRegistration.travel.departure_date }}</div>
                            <div v-if="selectedRegistration.travel.return_airport"><strong>Return:</strong> {{ selectedRegistration.travel.return_airport }} — {{ selectedRegistration.travel.return_date }}</div>
                            <div v-if="selectedRegistration.travel.outbound_flight_number"><strong>Outbound flight:</strong> {{ selectedRegistration.travel.outbound_airline }} {{ selectedRegistration.travel.outbound_flight_number }}</div>
                            <div v-if="selectedRegistration.travel.return_flight_number"><strong>Return flight:</strong> {{ selectedRegistration.travel.return_airline }} {{ selectedRegistration.travel.return_flight_number }}</div>
                            <div v-if="!selectedRegistration.travel.travel_method" class="text-muted">Not yet completed.</div>
                          </template>
                          <div v-else class="text-muted">No travel record.</div>
                        </div>
                      </div>
                    </div>

                    <!-- Accommodation -->
                    <div class="accordion-item border rounded mb-2">
                      <h2 class="accordion-header">
                        <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#accAccom">
                          <i class="bi bi-building me-2"></i>Accommodation
                          <span v-if="selectedRegistration.accommodation?.room_number" class="badge bg-success ms-2 small">Assigned</span>
                          <span v-else-if="selectedRegistration.accommodation?.package_choice" class="badge bg-warning text-dark ms-2 small">Pending</span>
                          <span v-else class="badge bg-secondary ms-2 small">None</span>
                        </button>
                      </h2>
                      <div id="accAccom" class="accordion-collapse collapse">
                        <div class="accordion-body small">
                          <template v-if="selectedRegistration.accommodation">
                            <div v-if="selectedRegistration.accommodation.package_choice"><strong>Package:</strong> {{ selectedRegistration.accommodation.package_choice_display }}</div>
                            <div v-if="selectedRegistration.accommodation.check_in_date"><strong>Check-in:</strong> {{ selectedRegistration.accommodation.check_in_date }}</div>
                            <div v-if="selectedRegistration.accommodation.check_out_date"><strong>Check-out:</strong> {{ selectedRegistration.accommodation.check_out_date }}</div>
                            <div v-if="selectedRegistration.accommodation.room_number"><strong>Room:</strong> {{ selectedRegistration.accommodation.room_number }}</div>
                            <div v-if="!selectedRegistration.accommodation.package_choice" class="text-muted">Not yet completed.</div>
                          </template>
                          <div v-else class="text-muted">No accommodation record.</div>
                        </div>
                      </div>
                    </div>

                    <!-- Committee Preferences -->
                    <div class="accordion-item border rounded mb-2">
                      <h2 class="accordion-header">
                        <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#accCommittee">
                          <i class="bi bi-people me-2"></i>Committee Preferences
                        </button>
                      </h2>
                      <div id="accCommittee" class="accordion-collapse collapse">
                        <div class="accordion-body small">
                          <template v-if="selectedRegistration.committee_preferences">
                            <div v-for="(val, key) in selectedRegistration.committee_preferences" :key="key">
                              <template v-if="key !== 'id' && val > 0">
                                <strong>{{ key.replace(/_/g, ' ') }}:</strong>
                                {{ val === 2 ? 'Prefer' : 'Interested' }}
                              </template>
                            </div>
                            <div v-if="Object.entries(selectedRegistration.committee_preferences).filter(([k,v]) => k !== 'id' && v > 0).length === 0" class="text-muted">No preferences set.</div>
                          </template>
                          <div v-else class="text-muted">No committee preferences record.</div>
                        </div>
                      </div>
                    </div>

                    <!-- Guests -->
                    <div class="accordion-item border rounded mb-2">
                      <h2 class="accordion-header">
                        <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#accGuests">
                          <i class="bi bi-person-plus me-2"></i>Guests
                          <span class="badge bg-secondary ms-2 small">{{ selectedRegistration.guest_details?.length ?? 0 }}</span>
                        </button>
                      </h2>
                      <div id="accGuests" class="accordion-collapse collapse">
                        <div class="accordion-body small">
                          <div v-if="selectedRegistration.guest_details?.length">
                            <div v-for="g in selectedRegistration.guest_details" :key="g.id" class="border-bottom pb-2 mb-2">
                              <div>{{ g.guest_first_name }} {{ g.guest_last_name }}</div>
                              <div v-if="g.guest_email" class="text-muted">{{ g.guest_email }}</div>
                              <div v-if="g.guest_phone" class="text-muted">{{ g.guest_phone }}</div>
                            </div>
                          </div>
                          <div v-else class="text-muted">No guests.</div>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="savingEdit || loadingDetail || !selectedRegistration"
              @click="saveEdit"
            >
              <span v-if="savingEdit" class="spinner-border spinner-border-sm me-1"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Create Modal ──────────────────────────────────────────────────── -->
    <div id="createRegistrationModal" class="modal fade" tabindex="-1" aria-labelledby="createModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="createModalLabel">Register a Person</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>

          <div class="modal-body">
            <!-- Tabs -->
            <ul class="nav nav-tabs mb-4">
              <li class="nav-item">
                <button
                  class="nav-link"
                  :class="{ active: createTab === 'search' }"
                  @click="createTab = 'search'"
                >
                  <i class="bi bi-search me-1"></i>Search Existing Member
                </button>
              </li>
              <li class="nav-item">
                <button
                  class="nav-link"
                  :class="{ active: createTab === 'new-person' }"
                  @click="createTab = 'new-person'"
                >
                  <i class="bi bi-person-plus me-1"></i>New Non-Member
                </button>
              </li>
            </ul>

            <!-- Search tab -->
            <div v-if="createTab === 'search'">
              <div class="mb-3 position-relative">
                <label class="form-label fw-medium">Search by name or member ID</label>
                <input
                  v-model="personSearchQuery"
                  type="text"
                  class="form-control"
                  placeholder="e.g. Smith or 12345"
                  @input="onPersonSearchInput"
                />
                <div v-if="personSearchLoading" class="mt-1 text-muted small">
                  <span class="spinner-border spinner-border-sm me-1"></span>Searching…
                </div>
              </div>

              <!-- Search results -->
              <div v-if="personSearchResults.length" class="list-group mb-3">
                <button
                  v-for="p in personSearchResults"
                  :key="p.id"
                  type="button"
                  class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                  :disabled="p.has_active_registration"
                  @click="selectPerson(p)"
                >
                  <div>
                    <div class="fw-medium">{{ p.first_name }} {{ p.last_name }}
                      <span v-if="p.preferred_first_name" class="text-muted small">({{ p.preferred_first_name }})</span>
                    </div>
                    <div class="text-muted small">{{ p.email || 'No account email' }} · Member ID: {{ p.member_id ?? 'N/A' }}</div>
                  </div>
                  <span v-if="p.has_active_registration" class="badge bg-warning text-dark">Already Registered</span>
                  <span v-else-if="selectedPerson?.id === p.id" class="badge bg-primary">Selected</span>
                </button>
              </div>
              <div v-else-if="personSearchQuery.length >= 2 && !personSearchLoading" class="text-muted small mb-3">
                No matching persons found.
              </div>

              <div v-if="selectedPerson" class="mb-3">
                <label class="form-label fw-medium">Initial Status</label>
                <select v-model="createStatusCode" class="form-select">
                  <option v-for="s in STATUS_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>
            </div>

            <!-- New non-member tab -->
            <div v-if="createTab === 'new-person'">
              <p class="text-muted small mb-3">
                Creates a bare person record with no login account. HQ will manage this registration directly.
              </p>
              <div class="row g-3 mb-3">
                <div class="col-sm-6">
                  <label class="form-label fw-medium">First Name <span class="text-danger">*</span></label>
                  <input v-model="newPersonForm.first_name" type="text" class="form-control" :class="{ 'is-invalid': newPersonErrors.first_name }" />
                  <div v-if="newPersonErrors.first_name" class="invalid-feedback">{{ newPersonErrors.first_name }}</div>
                </div>
                <div class="col-sm-6">
                  <label class="form-label fw-medium">Last Name <span class="text-danger">*</span></label>
                  <input v-model="newPersonForm.last_name" type="text" class="form-control" :class="{ 'is-invalid': newPersonErrors.last_name }" />
                  <div v-if="newPersonErrors.last_name" class="invalid-feedback">{{ newPersonErrors.last_name }}</div>
                </div>
                <div class="col-sm-6">
                  <label class="form-label">Preferred First Name</label>
                  <input v-model="newPersonForm.preferred_first_name" type="text" class="form-control" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label">Contact Email</label>
                  <input v-model="newPersonForm.contact_email" type="email" class="form-control" placeholder="For terms agreement email" />
                </div>
                <div class="col-sm-6">
                  <label class="form-label fw-medium">Initial Status</label>
                  <select v-model="newPersonForm.status_code" class="form-select">
                    <option v-for="s in STATUS_CHOICES" :key="s.value" :value="s.value">{{ s.label }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button
              v-if="createTab === 'search'"
              type="button"
              class="btn btn-primary"
              :disabled="!selectedPerson || creating"
              @click="createFromExistingPerson"
            >
              <span v-if="creating" class="spinner-border spinner-border-sm me-1"></span>
              Create Registration
            </button>
            <button
              v-else
              type="button"
              class="btn btn-primary"
              :disabled="creating"
              @click="createNewPerson"
            >
              <span v-if="creating" class="spinner-border spinner-border-sm me-1"></span>
              Create Registration
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
