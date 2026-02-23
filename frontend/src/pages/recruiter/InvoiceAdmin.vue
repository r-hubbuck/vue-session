<template>
  <div v-if="hasAccess">
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Invoice Management</h1>
        <p class="page-subtitle">Create and manage recruiter invoices</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <template v-else>
        <!-- Create Invoice -->
        <div class="section-card">
          <h5 class="fw-bold mb-3"><i class="bi bi-plus-circle me-2"></i>Create Invoice</h5>
          <form @submit.prevent="createInvoice">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Organization *</label>
                <select v-model="newInvoice.organization" class="form-select" required>
                  <option value="">Select organization...</option>
                  <option v-for="org in organizations" :key="org.id" :value="org.id">
                    {{ org.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Convention *</label>
                <select v-model="newInvoice.convention" class="form-select" required>
                  <option value="">Select convention...</option>
                  <option v-if="activeConvention" :value="activeConvention.id">
                    {{ activeConvention.name }} ({{ activeConvention.year }})
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">Status</label>
                <select v-model="newInvoice.status" class="form-select">
                  <option value="sent">Sent</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Amount *</label>
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input v-model="newInvoice.amount" type="number" step="0.01" min="0" max="999999.99" class="form-control" required>
                </div>
              </div>
              <div class="col-md-4">
                <label class="form-label">Issued Date *</label>
                <input v-model="newInvoice.issued_date" type="date" class="form-control" required>
              </div>
              <div class="col-md-4">
                <label class="form-label">Due Date *</label>
                <input v-model="newInvoice.due_date" type="date" class="form-control" required>
              </div>
              <div class="col-12">
                <label class="form-label">Description *</label>
                <textarea v-model.trim="newInvoice.description" class="form-control" rows="2" required maxlength="1000"></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Notes</label>
                <textarea v-model.trim="newInvoice.notes" class="form-control" rows="2" maxlength="1000"></textarea>
              </div>
            </div>

            <div v-if="createError" class="alert alert-danger mt-3">{{ createError }}</div>

            <button type="submit" class="btn btn-primary mt-3" :disabled="saving">
              <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Creating...</span>
              <span v-else><i class="bi bi-plus-circle me-2"></i>Create Invoice</span>
            </button>
          </form>
        </div>

        <!-- Invoice List -->
        <div class="section-card">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0"><i class="bi bi-receipt me-2"></i>All Invoices</h5>
            <div class="d-flex gap-2">
              <select v-model="filterStatus" class="form-select form-select-sm" style="width: auto;" @change="fetchInvoices">
                <option value="">All Statuses</option>
                <option value="draft">Draft</option>
                <option value="sent">Sent</option>
                <option value="paid">Paid</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          <div v-if="invoices.length === 0" class="text-muted text-center py-3">
            No invoices found.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th>Invoice #</th>
                  <th>Organization</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Issued</th>
                  <th>Due</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in invoices" :key="inv.id">
                  <td class="fw-medium">{{ inv.invoice_number }}</td>
                  <td>{{ inv.organization_name }}</td>
                  <td>${{ inv.amount }}</td>
                  <td>
                    <select
                      v-model="inv._status"
                      class="form-select form-select-sm"
                      style="width: 120px;"
                    >
                      <option value="draft">Draft</option>
                      <option value="sent">Sent</option>
                      <option value="paid">Paid</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </td>
                  <td>{{ inv.issued_date }}</td>
                  <td>{{ inv.due_date }}</td>
                  <td>
                    <button
                      v-if="inv._status !== inv.status"
                      @click="updateInvoice(inv)"
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
const hasAccess = computed(() => authStore.hasRole('hq_staff') || authStore.hasRole('hq_finance') || authStore.hasRole('hq_admin'))
const loading = ref(true)
const saving = ref(false)
const createError = ref('')
const filterStatus = ref('')

const invoices = ref([])
const organizations = ref([])
const activeConvention = ref(null)

const today = new Date().toISOString().split('T')[0]
const newInvoice = ref({
  organization: '',
  convention: '',
  status: 'sent',
  amount: '',
  description: '',
  notes: '',
  issued_date: today,
  due_date: '',
})

const fetchInvoices = async () => {
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res = await api.get('/api/recruiters/admin/invoices/', { params })
    const results = res.data.results ?? res.data
    invoices.value = results.map(inv => ({ ...inv, _status: inv.status }))
  } catch (error) {
    console.error('Error fetching invoices:', error)
  }
}

const createInvoice = async () => {
  if (saving.value) return
  createError.value = ''
  saving.value = true
  try {
    await api.post('/api/recruiters/admin/invoices/', newInvoice.value)
    toast.success('Invoice created!')
    newInvoice.value = {
      organization: '',
      convention: activeConvention.value?.id || '',
      status: 'sent',
      amount: '',
      description: '',
      notes: '',
      issued_date: today,
      due_date: '',
    }
    await fetchInvoices()
  } catch (error) {
    console.error('Invoice creation error:', error)
    createError.value = 'Failed to create invoice. Please check your inputs and try again.'
  } finally {
    saving.value = false
  }
}

const updateInvoice = async (inv) => {
  if (saving.value) return
  if (inv._status === 'sent') {
    if (!confirm('This will send an invoice email to the organization. Continue?')) return
  }
  saving.value = true
  try {
    const res = await api.put(`/api/recruiters/admin/invoices/${inv.id}/`, {
      status: inv._status,
    })
    Object.assign(inv, res.data)
    inv._status = res.data.status
    toast.success('Invoice updated!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Update failed.')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [invRes, orgRes, convRes] = await Promise.allSettled([
      api.get('/api/recruiters/admin/invoices/'),
      api.get('/api/recruiters/admin/organizations/'),
      api.get('/api/convention/current/'),
    ])

    if (invRes.status === 'fulfilled') {
      const invResults = invRes.value.data.results ?? invRes.value.data
      invoices.value = invResults.map(inv => ({ ...inv, _status: inv.status }))
    }
    if (orgRes.status === 'fulfilled') {
      organizations.value = orgRes.value.data.results ?? orgRes.value.data
    }
    if (convRes.status === 'fulfilled') {
      activeConvention.value = convRes.value.data
      newInvoice.value.convention = convRes.value.data.id
    }
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
})
</script>
