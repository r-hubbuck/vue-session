<template>
  <div>
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
          <h5 class="fw-bold mb-0 collapse-toggle" @click="showCreateForm = !showCreateForm">
            <i class="bi bi-plus-circle me-2"></i>Create Invoice
            <i class="bi ms-2 toggle-chevron" :class="showCreateForm ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
          </h5>
          <form v-if="showCreateForm" @submit.prevent="createInvoice" class="mt-3">
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
                <label class="form-label">Payment Link</label>
                <input v-model.trim="newInvoice.payment_link" type="url" class="form-control" placeholder="https://" maxlength="2000">
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
                  <th class="sortable-col" @click="setSort('invoice_number')">Invoice # <i :class="sortIcon('invoice_number')"></i></th>
                  <th class="sortable-col" @click="setSort('organization_name')">Organization <i :class="sortIcon('organization_name')"></i></th>
                  <th class="sortable-col" @click="setSort('amount')">Amount <i :class="sortIcon('amount')"></i></th>
                  <th class="sortable-col" @click="setSort('status')">Status <i :class="sortIcon('status')"></i></th>
                  <th>Payment Link</th>
                  <th class="sortable-col" @click="setSort('issued_date')">Issued <i :class="sortIcon('issued_date')"></i></th>
                  <th class="sortable-col" @click="setSort('due_date')">Due <i :class="sortIcon('due_date')"></i></th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in sortedInvoices" :key="inv.id" :class="invoiceRowClass(inv)">
                  <td class="fw-medium">{{ inv.invoice_number }}</td>
                  <td>{{ inv.organization_name }}</td>
                  <td>${{ inv.amount }}</td>
                  <td>
                    <span :class="statusBadgeClass(inv.status)">
                      {{ inv.status.charAt(0).toUpperCase() + inv.status.slice(1) }}
                    </span>
                  </td>
                  <td>
                    <a
                      v-if="inv.payment_link"
                      :href="inv.payment_link"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="payment-link"
                      @click.stop
                    >
                      <i class="bi bi-box-arrow-up-right me-1"></i>Link
                    </a>
                    <span v-else class="text-muted fst-italic">None</span>
                  </td>
                  <td>{{ inv.issued_date }}</td>
                  <td>{{ inv.due_date }}</td>
                  <td>
                    <button
                      class="btn btn-outline-secondary btn-sm"
                      @click="openInvoiceEdit(inv)"
                      title="Edit invoice"
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

  <!-- Invoice Edit Modal -->
  <div v-if="selectedInvoice" class="modal-backdrop-custom" @click.self="closeInvoiceEdit">
    <div class="modal-dialog-custom" style="max-width: 540px;">
      <div class="modal-header-custom">
        <h5 class="modal-title-custom">
          <i class="bi bi-pencil-square me-2"></i>Edit Invoice
          <span class="text-muted fw-normal ms-2" style="font-size: 0.9rem;">{{ selectedInvoice.invoice_number }}</span>
        </h5>
        <button class="btn-close" @click="closeInvoiceEdit"></button>
      </div>
      <div class="modal-body-custom">

        <h6 class="section-label">Details</h6>
        <div class="detail-grid mb-3">
          <div class="detail-item">
            <span class="detail-label">Organization</span>
            <span class="detail-value">{{ selectedInvoice.organization_name }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Amount</span>
            <span class="detail-value">${{ selectedInvoice.amount }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Issued</span>
            <span class="detail-value">{{ selectedInvoice.issued_date }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Due</span>
            <span class="detail-value">{{ selectedInvoice.due_date }}</span>
          </div>
        </div>

        <h6 class="section-label">Editable Fields</h6>
        <div class="detail-grid">
          <div class="detail-item">
            <label class="detail-label" for="inv-status">Status</label>
            <select id="inv-status" v-model="invoiceEditForm.status" class="form-select form-select-sm mt-1" :disabled="availableStatuses.length === 1">
              <option v-for="opt in availableStatuses" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <p v-if="availableStatuses.length === 1" class="small text-muted mt-1 mb-0">No further status changes allowed.</p>
          </div>
        </div>

        <div class="detail-item mt-3">
          <label class="detail-label" for="inv-link">Payment Link</label>
          <input
            id="inv-link"
            v-model.trim="invoiceEditForm.payment_link"
            type="url"
            class="form-control form-control-sm mt-1"
            placeholder="https://"
            maxlength="2000"
          >
        </div>

        <div v-if="invoiceEditForm.status === 'sent' && selectedInvoice.status !== 'sent'" class="alert alert-warning mt-3 mb-0 py-2 px-3" style="font-size: 0.85rem;">
          <i class="bi bi-envelope me-1"></i>
          Changing status to <strong>Sent</strong> will email the invoice to the organization.
        </div>

      </div>
      <div class="modal-footer-custom">
        <button @click="closeInvoiceEdit" class="btn btn-outline-secondary">Cancel</button>
        <button @click="saveInvoiceEdit" class="btn btn-primary ms-auto" :disabled="saving">
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
const hasAccess = computed(() => authStore.hasRole('hq_staff') || authStore.hasRole('hq_finance') || authStore.hasRole('hq_admin'))
const loading = ref(true)
const saving = ref(false)
const createError = ref('')
const filterStatus = ref('')
const showCreateForm = ref(false)

const invoices = ref([])
const organizations = ref([])
const activeConvention = ref(null)
const selectedInvoice = ref(null)
const invoiceEditForm = ref({ status: '', payment_link: '' })

const today = new Date().toISOString().split('T')[0]
const newInvoice = ref({
  organization: '',
  convention: '',
  status: 'sent',
  amount: '',
  description: '',
  payment_link: '',
  notes: '',
  issued_date: today,
  due_date: '',
})

const sortKey = ref('')
const sortDir = ref(1)

const setSort = (key) => {
  if (sortKey.value === key) sortDir.value *= -1
  else { sortKey.value = key; sortDir.value = 1 }
}

const sortIcon = (key) => {
  if (sortKey.value !== key) return 'bi bi-chevron-expand text-muted small'
  return sortDir.value === 1 ? 'bi bi-chevron-up small' : 'bi bi-chevron-down small'
}

const sortedInvoices = computed(() => {
  if (!sortKey.value) return invoices.value
  return [...invoices.value].sort((a, b) => {
    let av = a[sortKey.value] ?? ''
    let bv = b[sortKey.value] ?? ''
    if (sortKey.value === 'amount') { av = parseFloat(av); bv = parseFloat(bv) }
    if (av < bv) return -sortDir.value
    if (av > bv) return sortDir.value
    return 0
  })
})

const invoiceRowClass = (inv) => {
  if (inv.status === 'paid') return 'row-success'
  if (inv.status === 'cancelled') return 'row-danger'
  return ''
}

const statusBadgeClass = (status) => {
  const map = {
    paid: 'badge bg-success',
    sent: 'badge bg-primary',
    draft: 'badge bg-secondary',
    cancelled: 'badge bg-danger',
  }
  return map[status] || 'badge bg-secondary'
}

const statusTransitions = {
  draft:     [{ value: 'draft', label: 'Draft' }, { value: 'sent', label: 'Sent' }, { value: 'cancelled', label: 'Cancelled' }],
  sent:      [{ value: 'sent', label: 'Sent' }, { value: 'paid', label: 'Paid' }, { value: 'cancelled', label: 'Cancelled' }],
  paid:      [{ value: 'paid', label: 'Paid' }],
  cancelled: [{ value: 'cancelled', label: 'Cancelled' }],
}

const availableStatuses = computed(() =>
  statusTransitions[selectedInvoice.value?.status] ?? []
)

const openInvoiceEdit = (inv) => {
  selectedInvoice.value = inv
  invoiceEditForm.value = {
    status: inv.status,
    payment_link: inv.payment_link || '',
  }
}

const closeInvoiceEdit = () => {
  selectedInvoice.value = null
}

const saveInvoiceEdit = async () => {
  if (saving.value) return
  const inv = selectedInvoice.value
  saving.value = true
  try {
    const res = await api.put(`/api/recruiters/admin/invoices/${inv.id}/`, {
      status: invoiceEditForm.value.status,
      payment_link: invoiceEditForm.value.payment_link,
    })
    Object.assign(inv, res.data)
    closeInvoiceEdit()
    toast.success('Invoice updated!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Update failed.')
  } finally {
    saving.value = false
  }
}

const fetchInvoices = async () => {
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res = await api.get('/api/recruiters/admin/invoices/', { params })
    const results = res.data.results ?? res.data
    invoices.value = results
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
      payment_link: '',
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

onMounted(async () => {
  try {
    const [invRes, orgRes, convRes] = await Promise.allSettled([
      api.get('/api/recruiters/admin/invoices/'),
      api.get('/api/recruiters/admin/organizations/'),
      api.get('/api/convention/current/'),
    ])

    if (invRes.status === 'fulfilled') {
      const invResults = invRes.value.data.results ?? invRes.value.data
      invoices.value = invResults
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

<style scoped>
.collapse-toggle {
  cursor: pointer;
  user-select: none;
}
.toggle-chevron {
  font-size: 0.85rem;
  color: #64748b;
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
.row-danger td {
  background-color: #fee2e2 !important;
}
.payment-link {
  font-size: 0.85rem;
  color: #0d6efd;
  text-decoration: none;
}
.payment-link:hover {
  text-decoration: underline;
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
