<template>
  <div class="container-fluid mt-4">
    <h1>Expense Reports Administration</h1>
    
    <!-- Summary Stats -->
    <div class="row mb-4" v-if="expenseReports.length > 0">
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Total</h6>
            <h3 class="card-title">{{ expenseReports.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Submitted</h6>
            <h3 class="card-title">{{ reportsByStatus('submitted') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Under Review</h6>
            <h3 class="card-title">{{ reportsByStatus('under_review') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Approved</h6>
            <h3 class="card-title">{{ reportsByStatus('approved') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Paid</h6>
            <h3 class="card-title">{{ reportsByStatus('paid') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Total Amount</h6>
            <h3 class="card-title">${{ totalAmount }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-3">
            <label class="form-label">Filter by Status</label>
            <select v-model="statusFilter" class="form-select" @change="loadReports">
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="submitted">Submitted</option>
              <option value="under_review">Under Review</option>
              <option value="approved">Approved</option>
              <option value="paid">Paid</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Search Member</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="form-control" 
              placeholder="Search by name..."
              @input="filterReports"
            >
          </div>
          <div class="col-md-2">
            <label class="form-label">&nbsp;</label>
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              Clear Filters
            </button>
          </div>
          <div class="col-md-4 text-end">
            <label class="form-label">&nbsp;</label>
            <div>
              <button class="btn btn-primary" @click="loadReports">
                <i class="bi bi-arrow-clockwise"></i> Refresh
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Reports Table -->
    <div v-else-if="filteredReports.length > 0" class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Member</th>
                <th>Type</th>
                <th>Chapter</th>
                <th>Event Date</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Submitted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in filteredReports" :key="report.id">
                <td>{{ report.id }}</td>
                <td>{{ report.member_name }}</td>
                <td>
                  <span class="badge bg-secondary">{{ report.report_type_code }}</span>
                </td>
                <td>{{ report.chapter }}</td>
                <td>{{ formatDate(report.report_date) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(report.status)">
                    {{ report.status_display }}
                  </span>
                </td>
                <td class="fw-bold">${{ report.total_amount }}</td>
                <td>{{ formatDate(report.created_at) }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-primary me-1" 
                    @click="viewReport(report.id)"
                  >
                    <i class="bi bi-eye"></i> View
                  </button>
                  <button 
                    v-if="report.status === 'approved'"
                    class="btn btn-sm btn-success" 
                    @click="quickMarkAsPaid(report)"
                  >
                    <i class="bi bi-check-circle"></i> Mark Paid
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="card">
      <div class="card-body text-center py-5">
        <i class="bi bi-inbox" style="font-size: 4rem; color: #ccc;"></i>
        <h5 class="mt-3">No Reports Found</h5>
        <p class="text-muted">Try adjusting your filters</p>
      </div>
    </div>

    <!-- Detail Modal -->
    <div 
      class="modal fade" 
      id="detailModal" 
      tabindex="-1" 
      ref="detailModal"
    >
      <div class="modal-dialog modal-xl">
        <div class="modal-content" v-if="selectedReport">
          <div class="modal-header">
            <h5 class="modal-title">
              Expense Report #{{ selectedReport.id }} - {{ selectedReport.member_name }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <!-- Report Information -->
            <div class="row mb-4">
              <div class="col-md-6">
                <h6 class="text-muted">Report Information</h6>
                <table class="table table-sm">
                  <tr>
                    <th style="width: 40%;">Member:</th>
                    <td>{{ selectedReport.member_name }}</td>
                  </tr>
                  <tr>
                    <th>Email:</th>
                    <td>{{ selectedReport.member_email }}</td>
                  </tr>
                  <tr>
                    <th>Report Type:</th>
                    <td>
                      <span class="badge bg-secondary me-2">
                        {{ selectedReport.report_type_detail.report_code }}
                      </span>
                      {{ selectedReport.report_type_detail.report_name }}
                    </td>
                  </tr>
                  <tr>
                    <th>Chapter:</th>
                    <td>{{ selectedReport.chapter }}</td>
                  </tr>
                  <tr>
                    <th>Event Date:</th>
                    <td>{{ formatDate(selectedReport.report_date) }}</td>
                  </tr>
                  <tr>
                    <th>Submitted:</th>
                    <td>{{ formatDateTime(selectedReport.created_at) }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted">Status & Processing</h6>
                <table class="table table-sm">
                  <tr>
                    <th style="width: 40%;">Status:</th>
                    <td>
                      <span :class="getStatusBadgeClass(selectedReport.status)">
                        {{ selectedReport.status_display }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="selectedReport.reviewer_name">
                    <th>Reviewer:</th>
                    <td>{{ selectedReport.reviewer_name }}</td>
                  </tr>
                  <tr v-if="selectedReport.review_date">
                    <th>Review Date:</th>
                    <td>{{ formatDateTime(selectedReport.review_date) }}</td>
                  </tr>
                  <tr v-if="selectedReport.approver_name">
                    <th>Approver:</th>
                    <td>{{ selectedReport.approver_name }}</td>
                  </tr>
                  <tr v-if="selectedReport.approval_date">
                    <th>Approval Date:</th>
                    <td>{{ formatDateTime(selectedReport.approval_date) }}</td>
                  </tr>
                  <tr>
                    <th>Total Amount:</th>
                    <td class="fs-4 fw-bold text-success">${{ selectedReport.total_amount }}</td>
                  </tr>
                </table>
              </div>
            </div>

            <!-- Expense Details -->
            <div v-if="selectedReport.details" class="mb-4">
              <h6 class="text-muted">Expense Details</h6>
              
              <!-- Automobile -->
              <div class="card mb-3">
                <div class="card-header bg-light">
                  <strong>Automobile Expenses</strong>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-4">
                      <strong>Miles Driven:</strong> {{ selectedReport.details.automobile_miles }}
                    </div>
                    <div class="col-md-4">
                      <strong>Tolls:</strong> ${{ selectedReport.details.automobile_tolls }}
                    </div>
                    <div class="col-md-4">
                      <strong>Passengers:</strong> {{ selectedReport.details.passengers }}
                    </div>
                  </div>
                  <div class="mt-2 text-muted">
                    <small>
                      Rate: ${{ selectedReport.report_type_detail.mileage_rate }}/mile + 
                      ${{ selectedReport.report_type_detail.passenger_mileage_rate }}/passenger/mile
                    </small>
                  </div>
                </div>
              </div>

              <!-- Lodging -->
              <div class="card mb-3">
                <div class="card-header bg-light">
                  <strong>Lodging</strong>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <strong>Nights:</strong> {{ selectedReport.details.lodging_nights }}
                    </div>
                    <div class="col-md-6">
                      <strong>Cost per Night:</strong> ${{ selectedReport.details.lodging_per_night }}
                    </div>
                  </div>
                  <div class="mt-2 text-muted">
                    <small>Max: ${{ selectedReport.report_type_detail.max_lodging_per_night }}/night</small>
                  </div>
                </div>
              </div>

              <!-- Meals -->
              <div class="card mb-3">
                <div class="card-header bg-light">
                  <strong>Meals</strong>
                </div>
                <div class="card-body">
                  <div class="row mb-2">
                    <div class="col-12"><strong>En Route:</strong></div>
                    <div class="col-md-4">
                      Breakfasts: {{ selectedReport.details.breakfast_enroute }}
                      (Max: ${{ selectedReport.report_type_detail.max_breakfast_daily }})
                    </div>
                    <div class="col-md-4">
                      Lunches: {{ selectedReport.details.lunch_enroute }}
                      (Max: ${{ selectedReport.report_type_detail.max_lunch_daily }})
                    </div>
                    <div class="col-md-4">
                      Dinners: {{ selectedReport.details.dinner_enroute }}
                      (Max: ${{ selectedReport.report_type_detail.max_dinner_daily }})
                    </div>
                  </div>
                  <div class="row">
                    <div class="col-12"><strong>On-Site:</strong></div>
                    <div class="col-md-6">
                      Breakfasts: {{ selectedReport.details.breakfast_onsite }}
                      (Max: ${{ selectedReport.report_type_detail.max_breakfast_onsite }})
                    </div>
                    <div class="col-md-6">
                      Lunches: {{ selectedReport.details.lunch_onsite }}
                      (Max: ${{ selectedReport.report_type_detail.max_lunch_onsite }})
                    </div>
                  </div>
                </div>
              </div>

              <!-- Other Expenses -->
              <div class="card mb-3">
                <div class="card-header bg-light">
                  <strong>Other Expenses</strong>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-4">
                      <strong>Terminal Cost:</strong> ${{ selectedReport.details.terminal_cost }}
                    </div>
                    <div class="col-md-4">
                      <strong>Public Carrier:</strong> ${{ selectedReport.details.public_carrier_cost }}
                    </div>
                    <div class="col-md-4">
                      <strong>Other On-Site:</strong> ${{ selectedReport.details.other_onsite_cost }}
                    </div>
                  </div>
                  <div class="mt-3" v-if="selectedReport.details.expense_notes">
                    <strong>Notes:</strong>
                    <p class="mb-0">{{ selectedReport.details.expense_notes }}</p>
                  </div>
                  <div class="mt-2" v-if="selectedReport.details.billed_to_hq">
                    <span class="badge bg-info">Billed to HQ</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Update Status Form -->
            <div class="card">
              <div class="card-header bg-primary text-white">
                <strong>Update Report Status</strong>
              </div>
              <div class="card-body">
                <form @submit.prevent="updateReportStatus">
                  <div class="row">
                    <div class="col-md-4 mb-3">
                      <label class="form-label">Status *</label>
                      <select v-model="updateForm.status" class="form-select" required>
                        <option value="draft">Draft</option>
                        <option value="submitted">Submitted</option>
                        <option value="under_review">Under Review</option>
                        <option value="approved">Approved</option>
                        <option value="paid">Paid</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </div>
                    
                    <div class="col-md-4 mb-3" v-if="updateForm.status === 'paid'">
                      <label class="form-label">Payment Method</label>
                      <select v-model="updateForm.payment_method" class="form-select">
                        <option value="">Select...</option>
                        <option value="check">Check</option>
                        <option value="direct_deposit">Direct Deposit</option>
                        <option value="credit">Credit to Account</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    
                    <div class="col-md-4 mb-3" v-if="updateForm.status === 'paid' && updateForm.payment_method === 'check'">
                      <label class="form-label">Check Number</label>
                      <input v-model="updateForm.payment_check_number" type="text" class="form-control">
                    </div>
                  </div>

                  <div class="row" v-if="updateForm.status === 'paid'">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Payment Payer</label>
                      <input v-model="updateForm.payment_payer" type="text" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Paid Date</label>
                      <input v-model="updateForm.paid_date" type="datetime-local" class="form-control">
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Notes</label>
                    <textarea v-model="updateForm.notes" class="form-control" rows="3"></textarea>
                  </div>

                  <div class="mb-3" v-if="updateForm.status === 'rejected'">
                    <label class="form-label">Rejection Reason *</label>
                    <textarea v-model="updateForm.rejection_reason" class="form-control" rows="3" required></textarea>
                  </div>

                  <div class="d-flex justify-content-end gap-2">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                      Cancel
                    </button>
                    <button type="submit" class="btn btn-primary" :disabled="updateLoading">
                      <span v-if="updateLoading" class="spinner-border spinner-border-sm me-2"></span>
                      Update Report
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <!-- Payment Information (if paid) -->
            <div v-if="selectedReport.status === 'paid'" class="card mt-3">
              <div class="card-header bg-success text-white">
                <strong>Payment Information</strong>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4">
                    <strong>Method:</strong> {{ selectedReport.payment_method_display }}
                  </div>
                  <div class="col-md-4" v-if="selectedReport.payment_check_number">
                    <strong>Check #:</strong> {{ selectedReport.payment_check_number }}
                  </div>
                  <div class="col-md-4" v-if="selectedReport.payment_payer">
                    <strong>Payer:</strong> {{ selectedReport.payment_payer }}
                  </div>
                  <div class="col-md-4" v-if="selectedReport.paid_date">
                    <strong>Paid Date:</strong> {{ formatDateTime(selectedReport.paid_date) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Internal Notes -->
            <div v-if="selectedReport.notes" class="alert alert-info mt-3">
              <strong>Internal Notes:</strong>
              <p class="mb-0 mt-2">{{ selectedReport.notes }}</p>
            </div>

            <!-- Rejection Reason -->
            <div v-if="selectedReport.rejection_reason" class="alert alert-danger mt-3">
              <strong>Rejection Reason:</strong>
              <p class="mb-0 mt-2">{{ selectedReport.rejection_reason }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <div v-if="success" class="alert alert-success alert-dismissible fade show mt-3" role="alert">
      {{ success }}
      <button type="button" class="btn-close" @click="success = null"></button>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'ExpenseReportAdmin',
  data() {
    return {
      expenseReports: [],
      filteredReports: [],
      selectedReport: null,
      statusFilter: '',
      searchQuery: '',
      loading: false,
      updateLoading: false,
      error: null,
      success: null,
      detailModal: null,
      updateForm: {
        status: '',
        payment_method: '',
        payment_check_number: '',
        payment_payer: '',
        paid_date: '',
        notes: '',
        rejection_reason: ''
      }
    }
  },
  computed: {
    totalAmount() {
      return this.expenseReports
        .reduce((sum, r) => sum + parseFloat(r.total_amount), 0)
        .toFixed(2)
    }
  },
  mounted() {
    this.loadReports()
  },
  methods: {
    async loadReports() {
      this.loading = true
      this.error = null
      
      try {
        let url = '/api/expense-reports/staff/reports/'
        if (this.statusFilter) {
          url += `?status=${this.statusFilter}`
        }
        
        const response = await api.get(url)
        this.expenseReports = response.data
        this.filterReports()
      } catch (err) {
        console.error('Error loading expense reports:', err)
        this.error = 'Failed to load expense reports. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    filterReports() {
      if (!this.searchQuery) {
        this.filteredReports = this.expenseReports
        return
      }
      
      const query = this.searchQuery.toLowerCase()
      this.filteredReports = this.expenseReports.filter(report => 
        report.member_name.toLowerCase().includes(query) ||
        report.chapter.toLowerCase().includes(query)
      )
    },
    
    resetFilters() {
      this.statusFilter = ''
      this.searchQuery = ''
      this.loadReports()
    },
    
    async viewReport(reportId) {
      this.error = null
      
      try {
        const response = await api.get(`/api/expense-reports/staff/reports/${reportId}/`)
        this.selectedReport = response.data
        
        // Initialize update form with current values
        this.updateForm = {
          status: this.selectedReport.status,
          payment_method: this.selectedReport.payment_method || '',
          payment_check_number: this.selectedReport.payment_check_number || '',
          payment_payer: this.selectedReport.payment_payer || '',
          paid_date: this.selectedReport.paid_date ? this.formatDateTimeForInput(this.selectedReport.paid_date) : '',
          notes: this.selectedReport.notes || '',
          rejection_reason: this.selectedReport.rejection_reason || ''
        }
        
        // Show modal
        this.detailModal = new window.bootstrap.Modal(this.$refs.detailModal)
        this.detailModal.show()
      } catch (err) {
        console.error('Error loading report details:', err)
        this.error = 'Failed to load report details. Please try again.'
      }
    },
    
    async updateReportStatus() {
      this.updateLoading = true
      this.error = null
      this.success = null
      
      try {
        // Prepare data - only send fields that are set
        const updateData = {
          status: this.updateForm.status
        }
        
        if (this.updateForm.notes) {
          updateData.notes = this.updateForm.notes
        }
        
        if (this.updateForm.status === 'rejected' && this.updateForm.rejection_reason) {
          updateData.rejection_reason = this.updateForm.rejection_reason
        }
        
        if (this.updateForm.status === 'paid') {
          if (this.updateForm.payment_method) {
            updateData.payment_method = this.updateForm.payment_method
          }
          if (this.updateForm.payment_check_number) {
            updateData.payment_check_number = this.updateForm.payment_check_number
          }
          if (this.updateForm.payment_payer) {
            updateData.payment_payer = this.updateForm.payment_payer
          }
          if (this.updateForm.paid_date) {
            updateData.paid_date = this.updateForm.paid_date
          } else {
            // Set to now if not specified
            updateData.paid_date = new Date().toISOString()
          }
        }
        
        if (this.updateForm.status === 'under_review') {
          updateData.review_date = new Date().toISOString()
        }
        
        if (this.updateForm.status === 'approved') {
          updateData.approval_date = new Date().toISOString()
        }
        
        const response = await api.put(
          `/api/expense-reports/staff/reports/${this.selectedReport.id}/`,
          updateData
        )
        
        // Update local data
        this.selectedReport = response.data
        const index = this.expenseReports.findIndex(r => r.id === this.selectedReport.id)
        if (index !== -1) {
          // Update the list item with new data
          this.expenseReports[index] = {
            ...this.expenseReports[index],
            status: response.data.status,
            status_display: response.data.status_display,
            total_amount: response.data.total_amount
          }
        }
        this.filterReports()
        
        this.success = 'Report updated successfully!'
        
        // Close modal after a delay
        setTimeout(() => {
          this.detailModal.hide()
          this.success = null
        }, 1500)
      } catch (err) {
        console.error('Error updating report:', err)
        this.error = err.response?.data?.error || 'Failed to update report. Please try again.'
      } finally {
        this.updateLoading = false
      }
    },
    
    async quickMarkAsPaid(report) {
      if (!confirm(`Mark expense report #${report.id} as paid?`)) {
        return
      }
      
      this.loading = true
      this.error = null
      this.success = null
      
      try {
        const updateData = {
          status: 'paid',
          paid_date: new Date().toISOString()
        }
        
        await api.put(`/api/expense-reports/staff/reports/${report.id}/`, updateData)
        
        // Reload reports to get updated data
        await this.loadReports()
        
        this.success = `Report #${report.id} marked as paid!`
        
        setTimeout(() => {
          this.success = null
        }, 3000)
      } catch (err) {
        console.error('Error marking report as paid:', err)
        this.error = 'Failed to mark report as paid. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    reportsByStatus(status) {
      return this.expenseReports.filter(r => r.status === status).length
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        draft: 'badge bg-secondary',
        submitted: 'badge bg-primary',
        under_review: 'badge bg-info',
        approved: 'badge bg-success',
        paid: 'badge bg-success',
        rejected: 'badge bg-danger'
      }
      return classes[status] || 'badge bg-secondary'
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    },
    
    formatDateTime(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString()
    },
    
    formatDateTimeForInput(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day}T${hours}:${minutes}`
    }
  }
}
</script>

<style scoped>
.card {
  margin-bottom: 1.5rem;
}

.gap-2 {
  gap: 0.5rem;
}

.bi {
  vertical-align: middle;
}

.table th {
  background-color: #f8f9fa;
}

.modal-xl {
  max-width: 1200px;
}

.badge {
  font-size: 0.9em;
}
</style>
