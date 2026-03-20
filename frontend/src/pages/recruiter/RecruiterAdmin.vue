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
                  <th>Recruiter</th>
                  <th>Organization</th>
                  <th>Package</th>
                  <th>Booth ID</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reg in registrations" :key="reg.id">
                  <td class="fw-medium">{{ reg.recruiter.first_name }} {{ reg.recruiter.last_name }}</td>
                  <td>{{ reg.recruiter.organization_name }}</td>
                  <td>{{ reg.booth_package_detail?.name }}</td>
                  <td>
                    <input
                      v-model.trim="reg._boothId"
                      type="text"
                      class="form-control form-control-sm"
                      style="width: 100px;"
                      placeholder="Assign..."
                      maxlength="50"
                    >
                  </td>
                  <td>
                    <select v-model="reg._status" class="form-select form-select-sm" style="width: 130px;">
                      <option value="pending">Pending</option>
                      <option value="approved">Approved</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </td>
                  <td>
                    <button
                      v-if="reg._status !== reg.status || reg._boothId !== (reg.booth_id || '')"
                      @click="updateRegistration(reg)"
                      class="btn btn-primary btn-sm"
                      :disabled="saving"
                    >
                      <i class="bi bi-check2 me-1"></i>Save
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

const updateRegistration = async (reg) => {
  if (saving.value) return
  if (reg._boothId && !/^[A-Za-z0-9-]+$/.test(reg._boothId)) {
    toast.error('Booth ID may only contain letters, numbers, and hyphens.')
    return
  }
  saving.value = true
  try {
    const res = await api.put(`/api/recruiters/admin/registrations/${reg.id}/`, {
      booth_id: reg._boothId,
      status: reg._status,
    })
    Object.assign(reg, res.data)
    reg._boothId = res.data.booth_id
    reg._status = res.data.status
    toast.success('Registration updated!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Update failed.')
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
      registrations.value = results.map(r => ({
        ...r,
        _boothId: r.booth_id || '',
        _status: r.status,
      }))
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

/* Modal */
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
