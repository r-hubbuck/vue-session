<template>
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
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in pendingRecruiters" :key="r.id">
                  <td class="fw-medium">{{ r.first_name }} {{ r.last_name }}</td>
                  <td>{{ r.email }}</td>
                  <td>{{ r.organization_name }}</td>
                  <td>{{ formatPhone(r.phone) }}</td>
                  <td>
                    <button
                      @click="approveRecruiter(r.id)"
                      class="btn btn-success btn-sm"
                      :disabled="saving"
                    >
                      <i class="bi bi-check-lg me-1"></i>Approve
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
                  <th>Meal</th>
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
                  <td>{{ reg.meal_option_detail?.name || '—' }}</td>
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

const formatPhone = (value) => {
  if (!value) return '—'
  const digits = value.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
  }
  return value
}

const approveRecruiter = async (id) => {
  if (saving.value) return
  saving.value = true
  try {
    await api.put(`/api/recruiters/admin/approve/${id}/`)
    pendingRecruiters.value = pendingRecruiters.value.filter(r => r.id !== id)
    toast.success('Recruiter approved!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Approval failed.')
  } finally {
    saving.value = false
  }
}

const updateRegistration = async (reg) => {
  if (saving.value) return
  if (reg._boothId && !/^[A-Za-z0-9\-]+$/.test(reg._boothId)) {
    toast.error('Booth ID may only contain letters, numbers, and hyphens.')
    return
  }
  saving.value = true
  try {
    const res = await api.put(`/api/recruiters/admin/registrations/${reg.id}/`, {
      booth_id: reg._boothId,
      status: reg._status,
    })
    // Update local data
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
