<template>
  <div>
  <div v-if="hasAccess">
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Recruiter Administration</h1>
        <p class="page-subtitle">Approve recruiter accounts and manage booth assignments</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <template v-else>
        <!-- Pending Approvals -->
        <div class="section-card">
          <h5 class="fw-bold mb-3">
            <i class="bi bi-hourglass-split me-2"></i>Pending Approvals
            <span v-if="pendingRecruiters.length" class="badge bg-warning text-dark ms-2">{{ pendingRecruiters.length }}</span>
          </h5>

          <div v-if="pendingRecruiters.length === 0" class="text-muted">
            No pending recruiter approvals.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Organization</th>
                  <th>Phone</th>
                  <th>Registered</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="r in pendingRecruiters"
                  :key="r.id"
                  class="clickable-row"
                  @click="openDetail(r)"
                >
                  <td class="fw-medium">{{ r.first_name }} {{ r.last_name }}</td>
                  <td>{{ r.email }}</td>
                  <td>{{ r.organization_name }}</td>
                  <td>{{ formatPhone(r.phone) }}</td>
                  <td>{{ formatDate(r.created_at) }}</td>
                  <td @click.stop>
                    <button
                      @click="approveRecruiter(r.id)"
                      class="btn btn-success btn-sm me-1"
                      :disabled="saving"
                    >
                      <i class="bi bi-check-lg me-1"></i>Approve
                    </button>
                    <button
                      @click="openDetail(r)"
                      class="btn btn-outline-secondary btn-sm"
                    >
                      <i class="bi bi-eye me-1"></i>View
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Convention Registrations -->
        <div class="section-card">
          <h5 class="fw-bold mb-3">
            <i class="bi bi-calendar-event me-2"></i>Convention Registrations
          </h5>

          <div v-if="registrations.length === 0" class="text-muted">
            No recruiter registrations for the current convention.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th class="sortable-col" @click="setRegSort('name')">Recruiter <i :class="regSortIcon('name')"></i></th>
                  <th class="sortable-col" @click="setRegSort('org')">Organization <i :class="regSortIcon('org')"></i></th>
                  <th class="sortable-col" @click="setRegSort('package')">Package <i :class="regSortIcon('package')"></i></th>
                  <th class="sortable-col" @click="setRegSort('booth_id')">Booth ID <i :class="regSortIcon('booth_id')"></i></th>
                  <th class="sortable-col" @click="setRegSort('status')">Status <i :class="regSortIcon('status')"></i></th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reg in sortedRegistrations" :key="reg.id" :class="regRowClass(reg)">
                  <td class="fw-medium">{{ reg.recruiter.first_name }} {{ reg.recruiter.last_name }}</td>
                  <td>{{ reg.recruiter.organization_name }}</td>
                  <td>{{ reg.booth_package_detail?.name }}</td>
                  <td>
                    <span v-if="reg.booth_id" class="text-monospace">{{ reg.booth_id }}</span>
                    <span v-else class="text-muted fst-italic">Unassigned</span>
                  </td>
                  <td>
                    <span :class="statusBadgeClass(reg.status)">
                      {{ reg.status.charAt(0).toUpperCase() + reg.status.slice(1) }}
                    </span>
                  </td>
                  <td>
                    <button
                      class="btn btn-outline-secondary btn-sm"
                      @click="openRegEdit(reg)"
                      title="Edit registration"
                    >
                      <i class="bi bi-pencil"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </div>
  <div v-else class="content-container">
    <div class="alert alert-danger mt-4">You do not have permission to view this page.</div>
  </div>

  <!-- Recruiter Detail Modal -->
  <div v-if="selectedRecruiter" class="modal-backdrop-custom" @click.self="closeDetail">
    <div class="modal-dialog-custom">
      <div class="modal-header-custom">
        <h5 class="modal-title-custom">
          <i class="bi bi-person-badge me-2"></i>Recruiter Details
        </h5>
        <button class="btn-close" @click="closeDetail"></button>
      </div>
      <div class="modal-body-custom">

        <!-- Personal Info -->
        <h6 class="section-label">Personal Information</h6>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Name</span>
            <span class="detail-value">{{ selectedRecruiter.first_name }} {{ selectedRecruiter.last_name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ selectedRecruiter.email }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Phone</span>
            <span class="detail-value">{{ formatPhone(selectedRecruiter.phone) || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Cell Phone</span>
            <span class="detail-value">{{ formatPhone(selectedRecruiter.cell_phone) || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Registered</span>
            <span class="detail-value">{{ formatDate(selectedRecruiter.created_at) }}</span>
          </div>
        </div>

        <!-- Organization Info -->
        <h6 class="section-label mt-4">Organization</h6>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Name</span>
            <span class="detail-value">{{ selectedRecruiter.organization?.name || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Type</span>
            <span class="detail-value">{{ { business: 'Business', graduate_school: 'Graduate School', other: 'Other' }[selectedRecruiter.organization?.org_type] || selectedRecruiter.organization?.org_type || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Website</span>
            <span class="detail-value">{{ selectedRecruiter.organization?.website || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Phone</span>
            <span class="detail-value">{{ formatPhone(selectedRecruiter.organization?.phone) || '—' }}</span>
          </div>
          <div class="detail-item detail-item--full">
            <span class="detail-label">Address</span>
            <span class="detail-value">{{ formatOrgAddress(selectedRecruiter.organization) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Billing Email</span>
            <span class="detail-value">{{ selectedRecruiter.organization?.billing_email || '—' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Invoice Contact</span>
            <span class="detail-value">
              {{ selectedRecruiter.organization?.billing_contact_first_name }}
              {{ selectedRecruiter.organization?.billing_contact_last_name }}
            </span>
          </div>
        </div>
      </div>

      <div class="modal-footer-custom">
        <button
          @click="approveRecruiter(selectedRecruiter.id)"
          class="btn btn-success"
          :disabled="saving"
        >
          <i class="bi bi-check-lg me-1"></i>Approve
        </button>
        <button
          @click="denyRecruiter(selectedRecruiter.id)"
          class="btn btn-warning"
          :disabled="saving"
        >
          <i class="bi bi-x-lg me-1"></i>Deny
        </button>
        <button
          @click="deleteRecruiter(selectedRecruiter.id)"
          class="btn btn-danger"
          :disabled="saving"
        >
          <i class="bi bi-trash me-1"></i>Delete
        </button>
        <button @click="closeDetail" class="btn btn-outline-dark ms-auto" style="border: 1px solid #212529;">
          Close
        </button>
      </div>
    </div>
  </div>

  <!-- Registration Edit Modal -->
  <div v-if="selectedReg" class="modal-backdrop-custom" @click.self="closeRegEdit">
    <div class="modal-dialog-custom" style="max-width: 520px;">
      <div class="modal-header-custom">
        <h5 class="modal-title-custom">
          <i class="bi bi-pencil-square me-2"></i>Edit Registration
        </h5>
        <button class="btn-close" @click="closeRegEdit"></button>
      </div>
      <div class="modal-body-custom">

        <h6 class="section-label">Recruiter</h6>
        <div class="detail-grid mb-3">
          <div class="detail-item">
            <span class="detail-label">Name</span>
            <span class="detail-value">{{ selectedReg.recruiter.first_name }} {{ selectedReg.recruiter.last_name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Organization</span>
            <span class="detail-value">{{ selectedReg.recruiter.organization_name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Package</span>
            <span class="detail-value">{{ selectedReg.booth_package_detail?.name || '—' }}</span>
          </div>
        </div>

        <h6 class="section-label">Assignment</h6>
        <div class="detail-grid">
          <div class="detail-item">
            <label class="detail-label" for="reg-booth">Booth ID</label>
            <input
              id="reg-booth"
              v-model.trim="regEditForm.boothId"
              type="text"
              class="form-control form-control-sm mt-1"
              placeholder="e.g. B-12"
              maxlength="50"
            >
          </div>
          <div class="detail-item">
            <label class="detail-label" for="reg-status">Status</label>
            <select id="reg-status" v-model="regEditForm.status" class="form-select form-select-sm mt-1">
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="confirmed">Confirmed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

      </div>
      <div class="modal-footer-custom">
        <button @click="closeRegEdit" class="btn btn-outline-secondary">Cancel</button>
        <button @click="saveRegEdit" class="btn btn-primary ms-auto" :disabled="saving">
          <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Saving...</span>
          <span v-else><i class="bi bi-check2 me-1"></i>Save Changes</span>
        </button>
      </div>
    </div>
  </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '../../store/auth'

const toast = useToast()
const authStore = useAuthStore()
const hasAccess = computed(() => authStore.hasRole('hq_staff') || authStore.hasRole('hq_admin'))
const loading = ref(true)
const saving = ref(false)
const pendingRecruiters = ref([])
const registrations = ref([])
const selectedRecruiter = ref(null)
const selectedReg = ref(null)
const regEditForm = ref({ boothId: '', status: '' })

const regSortKey = ref('')
const regSortDir = ref(1)

const setRegSort = (key) => {
  if (regSortKey.value === key) regSortDir.value *= -1
  else { regSortKey.value = key; regSortDir.value = 1 }
}

const regSortIcon = (key) => {
  if (regSortKey.value !== key) return 'bi bi-chevron-expand text-muted small'
  return regSortDir.value === 1 ? 'bi bi-chevron-up small' : 'bi bi-chevron-down small'
}

const regSortVal = (reg, key) => {
  if (key === 'name') return `${reg.recruiter.first_name} ${reg.recruiter.last_name}`.toLowerCase()
  if (key === 'org') return (reg.recruiter.organization_name || '').toLowerCase()
  if (key === 'package') return (reg.booth_package_detail?.name || '').toLowerCase()
  if (key === 'booth_id') return (reg.booth_id || '').toLowerCase()
  if (key === 'status') return reg.status
  return ''
}

const sortedRegistrations = computed(() => {
  if (!regSortKey.value) return registrations.value
  return [...registrations.value].sort((a, b) => {
    const av = regSortVal(a, regSortKey.value)
    const bv = regSortVal(b, regSortKey.value)
    if (av < bv) return -regSortDir.value
    if (av > bv) return regSortDir.value
    return 0
  })
})

const regRowClass = (reg) => {
  if (reg.status === 'confirmed') return 'row-success'
  if (reg.status === 'approved') return 'row-info'
  if (reg.status === 'cancelled') return 'row-danger'
  return ''
}

const statusBadgeClass = (status) => {
  const map = {
    confirmed: 'badge bg-success',
    approved: 'badge bg-primary',
    pending: 'badge bg-warning text-dark',
    cancelled: 'badge bg-danger',
  }
  return map[status] || 'badge bg-secondary'
}

const formatPhone = (value) => {
  if (!value) return '—'
  const digits = value.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
  }
  return value
}

const formatDate = (value) => {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatOrgAddress = (org) => {
  if (!org) return '—'
  const parts = [
    org.address_line1,
    org.address_line2,
    org.city,
    org.state,
    org.zip_code,
    org.country,
  ].filter(Boolean)
  return parts.join(', ') || '—'
}

const openDetail = (recruiter) => {
  selectedRecruiter.value = recruiter
}

const closeDetail = () => {
  selectedRecruiter.value = null
}

const openRegEdit = (reg) => {
  selectedReg.value = reg
  regEditForm.value = {
    boothId: reg.booth_id || '',
    status: reg.status,
  }
}

const closeRegEdit = () => {
  selectedReg.value = null
}

const saveRegEdit = async () => {
  if (saving.value) return
  const reg = selectedReg.value
  if (regEditForm.value.boothId && !/^[A-Za-z0-9-]+$/.test(regEditForm.value.boothId)) {
    toast.error('Booth ID may only contain letters, numbers, and hyphens.')
    return
  }
  saving.value = true
  try {
    const res = await api.put(`/api/recruiters/admin/registrations/${reg.id}/`, {
      booth_id: regEditForm.value.boothId,
      status: regEditForm.value.status,
    })
    Object.assign(reg, res.data)
    closeRegEdit()
    toast.success('Registration updated!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Update failed.')
  } finally {
    saving.value = false
  }
}

const removeFromPending = (id) => {
  pendingRecruiters.value = pendingRecruiters.value.filter(r => r.id !== id)
  closeDetail()
}

const approveRecruiter = async (id) => {
  if (saving.value) return
  saving.value = true
  try {
    await api.put(`/api/recruiters/admin/approve/${id}/`)
    removeFromPending(id)
    toast.success('Recruiter approved!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Approval failed.')
  } finally {
    saving.value = false
  }
}

const denyRecruiter = async (id) => {
  if (saving.value) return
  if (!confirm('Deny this recruiter? Their account will be deactivated.')) return
  saving.value = true
  try {
    await api.put(`/api/recruiters/admin/deny/${id}/`)
    removeFromPending(id)
    toast.success('Recruiter denied.')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Deny failed.')
  } finally {
    saving.value = false
  }
}

const deleteRecruiter = async (id) => {
  if (saving.value) return
  if (!confirm('Permanently delete this recruiter and their account? This cannot be undone.')) return
  saving.value = true
  try {
    await api.delete(`/api/recruiters/admin/delete/${id}/`)
    removeFromPending(id)
    toast.success('Recruiter deleted.')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Delete failed.')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [pendingRes, regRes] = await Promise.allSettled([
      api.get('/api/recruiters/admin/pending/'),
      api.get('/api/recruiters/admin/registrations/'),
    ])

    if (pendingRes.status === 'fulfilled') {
      pendingRecruiters.value = pendingRes.value.data.results ?? pendingRes.value.data
    }
    if (regRes.status === 'fulfilled') {
      const results = regRes.value.data.results ?? regRes.value.data
      registrations.value = results
    }
  } catch (error) {
    console.error('Error loading admin data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.clickable-row {
  cursor: pointer;
}
.clickable-row:hover {
  background-color: #f8fafc;
}
.sortable-col {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.sortable-col:hover {
  background-color: #f1f5f9;
}
.row-success td {
  background-color: #d1fae5 !important;
}
.row-info td {
  background-color: #dbeafe !important;
}
.row-danger td {
  background-color: #fee2e2 !important;
}
.text-monospace {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.85em;
}

/* Recruiter detail modal */
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}

.modal-dialog-custom {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header-custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title-custom {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.modal-body-custom {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-footer-custom {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.75rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-item--full {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 0.9rem;
  color: #1a202c;
}
</style>
