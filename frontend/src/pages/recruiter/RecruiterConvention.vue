<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Convention Registration</h1>
        <p class="page-subtitle">Select your booth package and meal preference</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <template v-else>
        <!-- Already registered -->
        <div v-if="registration" class="section-card">
          <h5 class="fw-bold mb-3"><i class="bi bi-check-circle me-2"></i>Current Registration</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <p><strong>Status:</strong>
                <span class="badge" :class="statusClass">{{ registration.status.charAt(0).toUpperCase() + registration.status.slice(1) }}</span>
              </p>
              <p><strong>Package:</strong> {{ registration.booth_package_detail?.name }}</p>
              <p><strong>Price:</strong> ${{ registration.booth_package_detail?.price }}</p>
            </div>
            <div class="col-md-6">
              <p v-if="registration.booth_id"><strong>Booth ID:</strong> {{ registration.booth_id }}</p>
              <p v-if="registration.special_requests"><strong>Special Requests:</strong> {{ registration.special_requests }}</p>
            </div>
          </div>

          <!-- Attendees display -->
          <div v-if="registration.attendees?.length" class="mt-3">
            <p class="fw-bold mb-2">Recruiter Attendees</p>
            <div class="table-responsive">
              <table class="table table-sm table-custom mb-0">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(a, i) in registration.attendees" :key="i">
                    <td>{{ a.first_name }} {{ a.last_name }}</td>
                    <td>{{ a.email }}</td>
                    <td>{{ formatPhone(a.phone) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Edit form (only if pending) -->
          <div v-if="registration.status === 'pending'" class="mt-4">
            <hr>
            <h6 class="fw-bold">Update Registration</h6>
            <form @submit.prevent="updateRegistration">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Booth Package *</label>
                  <select v-model="editForm.booth_package" class="form-select" required>
                    <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
                      {{ pkg.name }} - ${{ pkg.price }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Majors recruiting (edit) -->
              <div class="row g-3 mt-1">
                <div class="col-md-6">
                  <label class="form-label">Majors Recruiting</label>
                  <div class="border rounded p-2" style="max-height: 160px; overflow-y: auto;">
                    <div v-for="c in curricula" :key="c.id" class="form-check">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        :id="`edit-major-${c.id}`"
                        :value="c.id"
                        v-model="editForm.recruiting_majors"
                      >
                      <label class="form-check-label small" :for="`edit-major-${c.id}`">{{ c.full_name }}</label>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Positions Recruiting</label>
                  <div class="border rounded p-2">
                    <div v-for="pos in positionOptions" :key="pos" class="form-check">
                      <input
                        class="form-check-input"
                        type="checkbox"
                        :id="`edit-pos-${pos}`"
                        :value="pos"
                        v-model="editForm.recruiting_positions"
                      >
                      <label class="form-check-label small" :for="`edit-pos-${pos}`">{{ pos }}</label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Number of recruiters (edit) -->
              <div class="row g-3 mt-1">
                <div class="col-md-4">
                  <label class="form-label">Number of Recruiters Attending *</label>
                  <select v-model.number="editNumRecruiters" class="form-select" @change="resizeEditAttendees">
                    <option v-for="n in 4" :key="n" :value="n">{{ n }}</option>
                  </select>
                </div>
              </div>

              <!-- Attendee fields (edit) -->
              <div v-for="(attendee, i) in editForm.attendees" :key="i" class="mt-3 p-3 border rounded">
                <p class="small fw-bold mb-2">Recruiter {{ i + 1 }}{{ i === 0 ? ' (Primary)' : '' }}</p>
                <div class="row g-2">
                  <div class="col-md-3">
                    <label class="form-label small">First Name *</label>
                    <input v-model.trim="attendee.first_name" type="text" class="form-control form-control-sm" required maxlength="100">
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small">Last Name *</label>
                    <input v-model.trim="attendee.last_name" type="text" class="form-control form-control-sm" required maxlength="100">
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small">Email *</label>
                    <input
                      v-model.trim="attendee.email"
                      type="email"
                      class="form-control form-control-sm"
                      required
                      maxlength="254"
                      :readonly="i === 0"
                      :class="{ 'bg-light': i === 0 }"
                    >
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small">Phone</label>
                    <input :value="attendee.phone" @input="formatAttendeePhone(attendee, $event)" type="tel" class="form-control form-control-sm" placeholder="(555) 123-4567" maxlength="14">
                  </div>
                </div>
              </div>

              <div class="mt-3">
                <label class="form-label">Special Requests</label>
                <textarea v-model.trim="editForm.special_requests" class="form-control" rows="3" maxlength="500"></textarea>
              </div>

              <button type="submit" class="btn btn-primary mt-3" :disabled="saving">
                <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Updating...</span>
                <span v-else><i class="bi bi-check2 me-2"></i>Update Registration</span>
              </button>
            </form>
          </div>
        </div>

        <!-- New registration -->
        <div v-else class="section-card">
          <h5 class="fw-bold mb-4">Choose Your Booth Package</h5>

          <!-- Package Rows -->
          <div class="mb-4">
            <div
              v-for="pkg in packages"
              :key="pkg.id"
              class="d-flex align-items-center gap-2 px-3 py-2 border rounded mb-2"
              :class="newForm.booth_package === pkg.id ? 'border-primary bg-light' : 'border'"
              style="cursor: pointer;"
              @click="selectPackage(pkg)"
            >
              <span
                class="flex-shrink-0"
                style="width: 14px; height: 14px; border-radius: 50%; border: 1.5px solid #aaa; display: inline-block; box-sizing: border-box;"
                :style="newForm.booth_package === pkg.id
                  ? 'border-color: #0d6efd; background: #0d6efd; box-shadow: inset 0 0 0 3px #fff;'
                  : ''"
              ></span>
              <span class="fw-semibold small flex-grow-1">{{ pkg.name }}</span>
              <div class="d-flex gap-1 flex-shrink-0">
                <span v-if="pkg.is_in_person" class="badge bg-info">In-Person</span>
                <span v-if="pkg.is_virtual" class="badge bg-secondary">Virtual</span>
                <span v-if="pkg.includes_resume_access" class="badge bg-success">Resume Access</span>
              </div>
              <span class="fw-semibold small flex-shrink-0 ms-2">${{ pkg.price }}</span>
            </div>
          </div>

          <form @submit.prevent="createRegistration">
            <!-- Majors and positions -->
            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Majors Recruiting</label>
                <div class="border rounded p-2" style="max-height: 160px; overflow-y: auto;">
                  <div v-for="c in curricula" :key="c.id" class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="`new-major-${c.id}`"
                      :value="c.id"
                      v-model="newForm.recruiting_majors"
                    >
                    <label class="form-check-label small" :for="`new-major-${c.id}`">{{ c.full_name }}</label>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label">Positions Recruiting</label>
                <div class="border rounded p-2">
                  <div v-for="pos in positionOptions" :key="pos" class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="`new-pos-${pos}`"
                      :value="pos"
                      v-model="newForm.recruiting_positions"
                    >
                    <label class="form-check-label small" :for="`new-pos-${pos}`">{{ pos }}</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Number of recruiters -->
            <div class="row g-3 mb-3">
              <div class="col-md-4">
                <label class="form-label">Number of Recruiters Attending *</label>
                <select v-model.number="numRecruiters" class="form-select" @change="resizeAttendees">
                  <option v-for="n in 4" :key="n" :value="n">{{ n }}</option>
                </select>
              </div>
            </div>

            <!-- Attendee fields -->
            <div v-for="(attendee, i) in newForm.attendees" :key="i" class="mb-3 p-3 border rounded">
              <p class="small fw-bold mb-2">Recruiter {{ i + 1 }}{{ i === 0 ? ' (Primary)' : '' }}</p>
              <div class="row g-2">
                <div class="col-md-3">
                  <label class="form-label small">First Name *</label>
                  <input v-model.trim="attendee.first_name" type="text" class="form-control form-control-sm" required maxlength="100">
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Last Name *</label>
                  <input v-model.trim="attendee.last_name" type="text" class="form-control form-control-sm" required maxlength="100">
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Email *</label>
                  <input
                    v-model.trim="attendee.email"
                    type="email"
                    class="form-control form-control-sm"
                    required
                    maxlength="254"
                    :readonly="i === 0"
                    :class="{ 'bg-light': i === 0 }"
                  >
                </div>
                <div class="col-md-3">
                  <label class="form-label small">Phone</label>
                  <input :value="attendee.phone" @input="formatAttendeePhone(attendee, $event)" type="tel" class="form-control form-control-sm" placeholder="(555) 123-4567" maxlength="14">
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Special Requests</label>
              <textarea v-model.trim="newForm.special_requests" class="form-control" rows="3" maxlength="500"></textarea>
            </div>

            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <button type="submit" class="btn btn-primary" :disabled="saving || !newForm.booth_package">
              <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Registering...</span>
              <span v-else><i class="bi bi-check2 me-2"></i>Register for Convention</span>
            </button>
          </form>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

const flattenErrors = (val) => {
  if (typeof val === 'string') return [val]
  if (Array.isArray(val)) return val.flatMap(flattenErrors)
  if (val && typeof val === 'object') return Object.values(val).flatMap(flattenErrors)
  return []
}

const packages = ref([])
const curricula = ref([])
const positionOptions = ['Full-time', 'Part-time', 'Paid Internship']
const registration = ref(null)
const primaryRecruiter = ref(null)

const numRecruiters = ref(1)
const editNumRecruiters = ref(1)

const formatPhone = (value) => {
  if (!value) return '—'
  const digits = value.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
  }
  return value || '—'
}

const formatAttendeePhone = (attendee, event) => {
  const raw = event.target.value
  const digits = raw.replace(/\D/g, '')
  if (digits.length === 10) {
    const formatted = `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
    attendee.phone = formatted
    event.target.value = formatted
  } else {
    attendee.phone = raw
  }
}

const blankAttendee = () => ({ first_name: '', last_name: '', email: '', phone: '' })

const newForm = ref({
  booth_package: null,
  special_requests: '',
  recruiting_majors: [],
  recruiting_positions: [],
  attendees: [blankAttendee()],
})

const editForm = ref({
  booth_package: null,
  special_requests: '',
  recruiting_majors: [],
  recruiting_positions: [],
  attendees: [],
})

const statusClass = computed(() => {
  const map = {
    pending: 'bg-warning text-dark',
    approved: 'bg-success',
    confirmed: 'bg-primary',
    cancelled: 'bg-secondary',
  }
  return map[registration.value?.status] || 'bg-secondary'
})

const primaryAttendee = () => {
  const raw = primaryRecruiter.value?.phone || ''
  const digits = raw.replace(/\D/g, '')
  const phone = digits.length === 10
    ? `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
    : raw
  return {
    first_name: primaryRecruiter.value?.first_name || '',
    last_name: primaryRecruiter.value?.last_name || '',
    email: primaryRecruiter.value?.email || '',
    phone,
  }
}

const resizeAttendees = () => {
  const current = newForm.value.attendees
  const n = numRecruiters.value
  if (n > current.length) {
    for (let i = current.length; i < n; i++) {
      current.push(blankAttendee())
    }
  } else {
    newForm.value.attendees = current.slice(0, n)
  }
}

const resizeEditAttendees = () => {
  const current = editForm.value.attendees
  const n = editNumRecruiters.value
  if (n > current.length) {
    for (let i = current.length; i < n; i++) {
      current.push(blankAttendee())
    }
  } else {
    editForm.value.attendees = current.slice(0, n)
  }
}

const selectPackage = (pkg) => {
  newForm.value.booth_package = pkg.id
}

const createRegistration = async () => {
  if (saving.value) return
  errorMessage.value = ''
  saving.value = true
  try {
    const res = await api.post('/api/recruiters/convention/register/', newForm.value)
    registration.value = res.data
    toast.success('Registration submitted!')
  } catch (error) {
    const data = error.response?.data
    if (data?.errors) {
      errorMessage.value = flattenErrors(data.errors).join(' ')
    } else {
      errorMessage.value = data?.error || 'Registration failed. Please check your selections and try again.'
    }
  } finally {
    saving.value = false
  }
}

const updateRegistration = async () => {
  if (saving.value) return
  saving.value = true
  try {
    const res = await api.put('/api/recruiters/convention/my-registration/', editForm.value)
    registration.value = res.data
    toast.success('Registration updated!')
  } catch (error) {
    const data = error.response?.data
    if (data?.errors) {
      toast.error(flattenErrors(data.errors).join(' '))
    } else {
      toast.error(data?.error || 'Update failed.')
    }
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [pkgRes, regRes, profileRes, curriculaRes] = await Promise.allSettled([
      api.get('/api/recruiters/convention/booth-packages/'),
      api.get('/api/recruiters/convention/my-registration/'),
      api.get('/api/recruiters/profile/'),
      api.get('/api/accounts/curricula'),
    ])

    if (pkgRes.status === 'fulfilled') packages.value = pkgRes.value.data
    if (profileRes.status === 'fulfilled') primaryRecruiter.value = profileRes.value.data
    if (curriculaRes.status === 'fulfilled') curricula.value = curriculaRes.value.data

    if (regRes.status === 'fulfilled' && regRes.value.data.id) {
      registration.value = regRes.value.data
      const existingAttendees = regRes.value.data.attendees || []
      editNumRecruiters.value = existingAttendees.length || 1
      editForm.value = {
        booth_package: regRes.value.data.booth_package,
        special_requests: regRes.value.data.special_requests || '',
        recruiting_majors: (regRes.value.data.recruiting_majors || []),
        recruiting_positions: (regRes.value.data.recruiting_positions || []),
        attendees: existingAttendees.length
          ? existingAttendees.map(a => ({
              first_name: a.first_name,
              last_name: a.last_name,
              email: a.email,
              phone: a.phone || '',
            }))
          : [primaryAttendee()],
      }
    } else {
      // Pre-populate primary recruiter as first attendee for new registration
      newForm.value.attendees = [primaryAttendee()]
    }
  } catch (error) {
    console.error('Error loading convention data:', error)
  } finally {
    loading.value = false
  }
})
</script>