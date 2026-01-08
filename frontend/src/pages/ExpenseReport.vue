<template>
  <div class="container-fluid mt-4">
    <h1>Expense Reports</h1>
    
    <!-- Summary Stats -->
    <div class="row mb-4" v-if="expenseReports.length > 0">
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Total Reports</h6>
            <h3 class="card-title">{{ expenseReports.length }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Pending</h6>
            <h3 class="card-title">{{ reportsByStatus('submitted') + reportsByStatus('under_review') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Approved</h6>
            <h3 class="card-title">{{ reportsByStatus('approved') }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="card-subtitle mb-2 text-muted">Total Reimbursed</h6>
            <h3 class="card-title">${{ totalReimbursed }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Create New Report Button -->
    <div class="mb-4">
      <button class="btn btn-primary" @click="showCreateForm = !showCreateForm">
        <i class="bi bi-plus-circle"></i> {{ showCreateForm ? 'Cancel' : 'Create New Report' }}
      </button>
    </div>

    <!-- Create Report Form -->
    <div v-if="showCreateForm" class="card mb-4">
      <div class="card-header">
        <h5>New Expense Report</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="createReport">
          <!-- Report Type Selection -->
          <div class="mb-3">
            <label class="form-label">Report Type *</label>
            <select v-model="newReport.report_type" class="form-select" required @change="onReportTypeChange">
              <option value="">Select a report type...</option>
              <option v-for="type in reportTypes" :key="type.id" :value="type.id">
                {{ type.report_code }} - {{ type.report_name }}
              </option>
            </select>
            <div v-if="selectedReportType" class="form-text mt-2">
              <strong>Rate Information:</strong><br>
              Mileage: ${{ selectedReportType.mileage_rate }}/mile
              | Lodging: ${{ selectedReportType.max_lodging_per_night }}/night
              | Breakfast: ${{ selectedReportType.max_breakfast_daily }}
              | Lunch: ${{ selectedReportType.max_lunch_daily }}
              | Dinner: ${{ selectedReportType.max_dinner_daily }}
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Chapter *</label>
              <input v-model="newReport.chapter" type="text" class="form-control" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Event Date *</label>
              <input v-model="newReport.report_date" type="date" class="form-control" required>
            </div>
          </div>

          <h6 class="mt-4 mb-3">Expense Details</h6>

          <!-- Automobile Expenses -->
          <div class="card mb-3">
            <div class="card-header">Automobile</div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Miles Driven</label>
                  <input v-model.number="newReport.details.automobile_miles" type="number" step="0.01" class="form-control">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Tolls ($)</label>
                  <input v-model.number="newReport.details.automobile_tolls" type="number" step="0.01" class="form-control">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Passengers</label>
                  <input v-model.number="newReport.details.passengers" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Lodging -->
          <div class="card mb-3">
            <div class="card-header">Lodging</div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Number of Nights</label>
                  <input v-model.number="newReport.details.lodging_nights" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Cost Per Night ($)</label>
                  <input v-model.number="newReport.details.lodging_per_night" type="number" step="0.01" class="form-control">
                </div>
              </div>
            </div>
          </div>

          <!-- Meals En Route -->
          <div class="card mb-3">
            <div class="card-header">Meals En Route</div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Breakfasts</label>
                  <input v-model.number="newReport.details.breakfast_enroute" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Lunches</label>
                  <input v-model.number="newReport.details.lunch_enroute" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Dinners</label>
                  <input v-model.number="newReport.details.dinner_enroute" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Meals On-Site -->
          <div class="card mb-3">
            <div class="card-header">Meals On-Site</div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Breakfasts</label>
                  <input v-model.number="newReport.details.breakfast_onsite" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Lunches</label>
                  <input v-model.number="newReport.details.lunch_onsite" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Other Expenses -->
          <div class="card mb-3">
            <div class="card-header">Other Expenses</div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Terminal Costs ($)</label>
                  <input v-model.number="newReport.details.terminal_cost" type="number" step="0.01" class="form-control">
                  <small class="form-text text-muted">Airport parking, etc.</small>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Public Carrier ($)</label>
                  <input v-model.number="newReport.details.public_carrier_cost" type="number" step="0.01" class="form-control">
                  <small class="form-text text-muted">Airline, train, bus</small>
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Other On-Site ($)</label>
                  <input v-model.number="newReport.details.other_onsite_cost" type="number" step="0.01" class="form-control">
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Additional Notes</label>
                <textarea v-model="newReport.details.expense_notes" class="form-control" rows="3"></textarea>
              </div>
              <div class="form-check">
                <input v-model="newReport.details.billed_to_hq" type="checkbox" class="form-check-input" id="billedToHq">
                <label class="form-check-label" for="billedToHq">
                  Billed directly to headquarters
                </label>
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" @click="cancelCreate">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Create Report
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !showCreateForm" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Reports List -->
    <div v-else-if="expenseReports.length > 0" class="card">
      <div class="card-header">
        <h5>Your Expense Reports</h5>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
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
              <tr v-for="report in expenseReports" :key="report.id">
                <td>{{ report.id }}</td>
                <td>
                  <span class="badge bg-secondary">{{ report.report_type_code }}</span>
                  <br>
                  <small class="text-muted">{{ report.report_type_name }}</small>
                </td>
                <td>{{ report.chapter }}</td>
                <td>{{ formatDate(report.report_date) }}</td>
                <td>
                  <span :class="getStatusBadgeClass(report.status)">
                    {{ report.status_display }}
                  </span>
                </td>
                <td>${{ report.total_amount }}</td>
                <td>{{ formatDate(report.created_at) }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="viewReport(report.id)">
                    View
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
        <i class="bi bi-file-earmark-text" style="font-size: 4rem; color: #ccc;"></i>
        <h5 class="mt-3">No Expense Reports</h5>
        <p class="text-muted">You haven't created any expense reports yet.</p>
        <button class="btn btn-primary" @click="showCreateForm = true">
          Create Your First Report
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
      {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Success Alert -->
    <div v-if="success" class="alert alert-success alert-dismissible fade show mt-3" role="alert">
      {{ success }}
      <button type="button" class="btn-close" @click="success = null"></button>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'ExpenseReport',
  data() {
    return {
      expenseReports: [],
      reportTypes: [],
      showCreateForm: false,
      loading: false,
      error: null,
      success: null,
      newReport: {
        report_type: '',
        chapter: '',
        report_date: '',
        details: {
          automobile_miles: 0,
          automobile_tolls: 0,
          passengers: 0,
          lodging_nights: 0,
          lodging_per_night: 0,
          breakfast_enroute: 0,
          lunch_enroute: 0,
          dinner_enroute: 0,
          breakfast_onsite: 0,
          lunch_onsite: 0,
          terminal_cost: 0,
          public_carrier_cost: 0,
          other_onsite_cost: 0,
          billed_to_hq: false,
          expense_notes: ''
        }
      }
    }
  },
  computed: {
    selectedReportType() {
      if (!this.newReport.report_type) return null
      return this.reportTypes.find(t => t.id === this.newReport.report_type)
    },
    totalReimbursed() {
      return this.expenseReports
        .filter(r => r.status === 'paid')
        .reduce((sum, r) => sum + parseFloat(r.total_amount), 0)
        .toFixed(2)
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        // Load report types
        const typesResponse = await api.get('/api/expense-reports/types/')
        this.reportTypes = typesResponse.data
        
        // Load user's reports
        const reportsResponse = await api.get('/api/expense-reports/my-reports/')
        this.expenseReports = reportsResponse.data
      } catch (err) {
        console.error('Error loading expense reports:', err)
        this.error = 'Failed to load expense reports. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    onReportTypeChange() {
      // Could pre-fill chapter from user's member info if available
    },
    
    async createReport() {
      this.loading = true
      this.error = null
      this.success = null
      
      try {
        const response = await api.post('/api/expense-reports/my-reports/', this.newReport)
        this.expenseReports.unshift(response.data)
        this.success = 'Expense report created successfully!'
        this.resetForm()
        this.showCreateForm = false
      } catch (err) {
        console.error('Error creating expense report:', err)
        this.error = err.response?.data?.error || 'Failed to create expense report. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    cancelCreate() {
      this.resetForm()
      this.showCreateForm = false
    },
    
    resetForm() {
      this.newReport = {
        report_type: '',
        chapter: '',
        report_date: '',
        details: {
          automobile_miles: 0,
          automobile_tolls: 0,
          passengers: 0,
          lodging_nights: 0,
          lodging_per_night: 0,
          breakfast_enroute: 0,
          lunch_enroute: 0,
          dinner_enroute: 0,
          breakfast_onsite: 0,
          lunch_onsite: 0,
          terminal_cost: 0,
          public_carrier_cost: 0,
          other_onsite_cost: 0,
          billed_to_hq: false,
          expense_notes: ''
        }
      }
    },
    
    viewReport(reportId) {
      // Navigate to report detail view (implement later)
      this.$router.push(`/expense-report/${reportId}`)
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
</style>
