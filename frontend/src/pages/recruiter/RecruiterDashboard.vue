<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Recruiter Dashboard</h1>
        <p class="page-subtitle" v-if="profile">
          {{ profile.first_name }} {{ profile.last_name }} &mdash; {{ profile.organization?.name }}
        </p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <template v-else>
        <!-- Approval Status -->
        <div v-if="profile && !profile.is_approved" class="section-card">
          <div class="alert alert-warning mb-0" style="border-left: 4px solid #f59e0b;">
            <i class="bi bi-hourglass-split me-2"></i>
            <strong>Pending Approval</strong> &mdash; Your recruiter account is awaiting admin approval. You will receive an email once approved.
          </div>
        </div>

        <!-- Dashboard Cards -->
        <div v-if="profile" class="row g-4">
          <!-- Convention Registration -->
          <div class="col-md-6">
            <div class="section-card h-100">
              <h5 class="fw-bold mb-3"><i class="bi bi-calendar-event me-2"></i>Convention Registration</h5>
              <div v-if="registration">
                <p><strong>Status:</strong>
                  <span class="badge" :class="statusBadgeClass(registration.status)">{{ registration.status.charAt(0).toUpperCase() + registration.status.slice(1) }}</span>
                </p>
                <p><strong>Package:</strong> {{ registration.booth_package_detail?.name }}</p>
                <p v-if="registration.booth_id"><strong>Booth ID:</strong> {{ registration.booth_id }}</p>
                <p v-if="registration.meal_option_detail"><strong>Meal:</strong> {{ registration.meal_option_detail.name }}</p>
                <router-link to="/recruiter/convention" class="btn btn-outline-custom btn-sm">
                  <i class="bi bi-pencil me-1"></i>View/Edit
                </router-link>
              </div>
              <div v-else>
                <p class="text-muted">Not yet registered for a convention.</p>
                <router-link
                  v-if="profile.is_approved"
                  to="/recruiter/convention"
                  class="btn btn-primary btn-sm"
                >
                  <i class="bi bi-plus-circle me-1"></i>Register Now
                </router-link>
              </div>
            </div>
          </div>

          <!-- Invoices -->
          <div class="col-md-6">
            <div class="section-card h-100">
              <h5 class="fw-bold mb-3"><i class="bi bi-receipt me-2"></i>Invoices</h5>
              <div v-if="invoices.length > 0">
                <div v-for="inv in invoices.slice(0, 3)" :key="inv.id" class="d-flex justify-content-between align-items-center mb-2 p-2" style="background: #fafbfc; border-radius: 6px;">
                  <div>
                    <strong>{{ inv.invoice_number }}</strong>
                    <span class="text-muted ms-2">${{ inv.amount }}</span>
                  </div>
                  <span class="badge" :class="statusBadgeClass(inv.status)">{{ inv.status.charAt(0).toUpperCase() + inv.status.slice(1) }}</span>
                </div>
                <router-link to="/recruiter/invoices" class="btn btn-outline-custom btn-sm mt-2">
                  View All Invoices
                </router-link>
              </div>
              <div v-else>
                <p class="text-muted">No invoices yet.</p>
                <router-link to="/recruiter/invoices" class="btn btn-outline-custom btn-sm">
                  View Invoices
                </router-link>
              </div>
            </div>
          </div>

          <!-- Attendee List -->
          <div class="col-md-6" v-if="profile.is_approved">
            <div class="section-card h-100">
              <h5 class="fw-bold mb-3"><i class="bi bi-people me-2"></i>Convention Attendees</h5>
              <p class="text-muted">Browse members attending the convention.</p>
              <router-link to="/recruiter/attendees" class="btn btn-outline-custom btn-sm">
                <i class="bi bi-search me-1"></i>View Attendees
              </router-link>
            </div>
          </div>

          <!-- Organization Info -->
          <div class="col-md-6">
            <div class="section-card h-100">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold mb-0"><i class="bi bi-building me-2"></i>Organization</h5>
                <button
                  v-if="!editingOrg && profile.organization"
                  @click="startEditOrg"
                  class="btn btn-outline-custom btn-sm"
                >
                  <i class="bi bi-pencil me-1"></i>Edit
                </button>
              </div>

              <!-- View Mode -->
              <div v-if="profile.organization && !editingOrg">
                <p class="mb-1"><strong>{{ profile.organization.name }}</strong></p>
                <p class="text-muted mb-1">{{ profile.organization.org_type }}</p>
                <p class="text-muted mb-1" v-if="profile.organization.website">
                  <a :href="profile.organization.website" target="_blank" rel="noopener noreferrer">{{ profile.organization.website }}</a>
                </p>
                <p class="text-muted mb-1" v-if="profile.organization.phone">
                  {{ formatPhone(profile.organization.phone) }}
                </p>
                <p class="text-muted mb-0">
                  {{ profile.organization.address_line1 }}<span v-if="profile.organization.address_line2">, {{ profile.organization.address_line2 }}</span><br>
                  {{ profile.organization.city }}<span v-if="profile.organization.state">, {{ profile.organization.state }}</span> {{ profile.organization.zip_code }}
                </p>
                <hr class="my-2">
                <p class="text-muted mb-0 small">
                  <strong>Billing:</strong> {{ profile.organization.billing_contact_first_name }} {{ profile.organization.billing_contact_last_name }} &mdash; {{ profile.organization.billing_email }}
                </p>
              </div>

              <!-- Edit Mode -->
              <form v-if="editingOrg" @submit.prevent="saveOrg">
                <div class="row g-2">
                  <div class="col-12">
                    <label class="form-label small">Organization Name *</label>
                    <input v-model.trim="orgForm.name" type="text" class="form-control form-control-sm" required maxlength="255">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Type *</label>
                    <select v-model="orgForm.org_type" class="form-select form-select-sm" required>
                      <option value="business">Business</option>
                      <option value="graduate_school">Graduate School</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Website</label>
                    <input v-model.trim="orgForm.website" type="url" class="form-control form-control-sm" placeholder="https://..." maxlength="200">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Phone</label>
                    <input v-model="orgForm.phone" @input="formatOrgPhone" type="tel" class="form-control form-control-sm" placeholder="(555) 123-4567" maxlength="14">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small"># Recruiters Attending *</label>
                    <input v-model.number="orgForm.num_recruiters" type="number" class="form-control form-control-sm" min="1" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Address Line 1 *</label>
                    <input v-model.trim="orgForm.address_line1" type="text" class="form-control form-control-sm" required maxlength="255">
                  </div>
                  <div class="col-md-6">
                    <label class="form-label small">Address Line 2</label>
                    <input v-model.trim="orgForm.address_line2" type="text" class="form-control form-control-sm" maxlength="255">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">City *</label>
                    <input v-model.trim="orgForm.city" type="text" class="form-control form-control-sm" required maxlength="100">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">State</label>
                    <input v-model.trim="orgForm.state" type="text" class="form-control form-control-sm" maxlength="100">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Zip Code</label>
                    <input v-model.trim="orgForm.zip_code" type="text" class="form-control form-control-sm" maxlength="20">
                  </div>
                  <div class="col-12">
                    <hr class="my-2">
                    <p class="small fw-bold mb-2">Billing Contact</p>
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">First Name *</label>
                    <input v-model.trim="orgForm.billing_contact_first_name" type="text" class="form-control form-control-sm" required maxlength="100">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Last Name *</label>
                    <input v-model.trim="orgForm.billing_contact_last_name" type="text" class="form-control form-control-sm" required maxlength="100">
                  </div>
                  <div class="col-md-4">
                    <label class="form-label small">Billing Email *</label>
                    <input v-model.trim="orgForm.billing_email" type="email" class="form-control form-control-sm" required maxlength="254">
                  </div>
                </div>
                <div class="d-flex gap-2 mt-3">
                  <button type="submit" class="btn btn-primary btn-sm" :disabled="savingOrg">
                    <span v-if="savingOrg"><span class="spinner-border spinner-border-sm me-1"></span>Saving...</span>
                    <span v-else><i class="bi bi-check2 me-1"></i>Save</span>
                  </button>
                  <button type="button" class="btn btn-outline-secondary btn-sm" @click="editingOrg = false" :disabled="savingOrg">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const loading = ref(true)
const profile = ref(null)
const registration = ref(null)
const invoices = ref([])
const editingOrg = ref(false)
const savingOrg = ref(false)
const orgForm = ref({})

const formatPhone = (value) => {
  if (!value) return ''
  const digits = value.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
  }
  return value
}

const formatPhoneNumber = (value) => {
  if (!value) return value
  const digits = value.replace(/\D/g, '')
  if (digits.length === 10) {
    return `(${digits.substr(0, 3)}) ${digits.substr(3, 3)}-${digits.substr(6, 4)}`
  }
  return digits
}

const formatOrgPhone = () => {
  orgForm.value.phone = formatPhoneNumber(orgForm.value.phone)
}

const startEditOrg = () => {
  const org = profile.value.organization
  orgForm.value = {
    name: org.name || '',
    org_type: org.org_type || '',
    website: org.website || '',
    phone: formatPhoneNumber(org.phone) || '',
    address_line1: org.address_line1 || '',
    address_line2: org.address_line2 || '',
    city: org.city || '',
    state: org.state || '',
    zip_code: org.zip_code || '',
    billing_email: org.billing_email || '',
    billing_contact_first_name: org.billing_contact_first_name || '',
    billing_contact_last_name: org.billing_contact_last_name || '',
    num_recruiters: org.num_recruiters || 1,
  }
  editingOrg.value = true
}

const saveOrg = async () => {
  savingOrg.value = true
  try {
    const res = await api.put('/api/recruiters/organization/', orgForm.value)
    profile.value.organization = res.data
    editingOrg.value = false
    toast.success('Organization updated!')
  } catch (error) {
    const data = error.response?.data
    if (data?.errors) {
      const msgs = Object.values(data.errors).flat().join(' ')
      toast.error(msgs)
    } else {
      toast.error(data?.error || 'Failed to update organization.')
    }
  } finally {
    savingOrg.value = false
  }
}

const statusBadgeClass = (s) => {
  const map = {
    pending: 'bg-warning text-dark',
    approved: 'bg-success',
    confirmed: 'bg-primary',
    cancelled: 'bg-secondary',
    draft: 'bg-secondary',
    sent: 'bg-info',
    paid: 'bg-success',
  }
  return map[s] || 'bg-secondary'
}

onMounted(async () => {
  try {
    const [profileRes, regRes, invoiceRes] = await Promise.allSettled([
      api.get('/api/recruiters/profile/'),
      api.get('/api/recruiters/convention/my-registration/'),
      api.get('/api/recruiters/invoices/'),
    ])

    if (profileRes.status === 'fulfilled') {
      profile.value = profileRes.value.data
    }
    if (regRes.status === 'fulfilled' && regRes.value.data.id) {
      registration.value = regRes.value.data
    }
    if (invoiceRes.status === 'fulfilled') {
      invoices.value = invoiceRes.value.data
    }
  } catch (error) {
    console.error('Error loading dashboard:', error)
    toast.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
})
</script>
