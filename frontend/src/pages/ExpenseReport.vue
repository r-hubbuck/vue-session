<template>
  <div>
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Expense Reports</h1>
        <p class="page-subtitle">Submit and track your travel expense reimbursements</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-container">
      <!-- Summary Stats Bar -->
      <div class="stats-bar" v-if="expenseReports.length > 0">
        <div class="stat-item">
          <div class="stat-indicator" style="background: #284080;"></div>
          <div class="stat-content">
            <div class="stat-label">Total Reports</div>
            <div class="stat-value">{{ expenseReports.length }}</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-indicator" style="background: #f59e0b;"></div>
          <div class="stat-content">
            <div class="stat-label">Pending Review</div>
            <div class="stat-value">{{ reportsByStatus('submitted') + reportsByStatus('reviewed') }}</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-indicator" style="background: #10b981;"></div>
          <div class="stat-content">
            <div class="stat-label">Approved</div>
            <div class="stat-value">{{ reportsByStatus('approved') + reportsByStatus('paid') }}</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-indicator" style="background: #8b5cf6;"></div>
          <div class="stat-content">
            <div class="stat-label">Total Reimbursed</div>
            <div class="stat-value">${{ totalReimbursed }}</div>
          </div>
        </div>
        <button class="btn btn-primary" @click="showCreateForm = !showCreateForm" style="margin-left: auto;">
          <i class="bi bi-plus-circle me-2"></i>{{ showCreateForm ? 'Cancel' : 'Create Report' }}
        </button>
      </div>

      <!-- Create Report Form -->
      <div v-if="showCreateForm" class="section-card">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-file-earmark-plus"></i>
            </div>
            New Expense Report
          </h2>
        </div>

        <form @submit.prevent="createReport">
          <!-- Report Type Selection -->
          <div class="info-alert mb-4">
            <i class="bi bi-info-circle-fill"></i>
            <div class="info-alert-content">
              Select your report type to see applicable rates and limits for your expenses.
            </div>
          </div>

          <div class="row g-4">
            <div class="col-12">
              <label class="form-label">Report Type *</label>
              <select v-model="newReport.report_type" class="form-select" required @change="onReportTypeChange">
                <option value="">Select a report type...</option>
                <option v-for="type in reportTypes" :key="type.id" :value="type.id">
                  {{ type.report_code }} - {{ type.report_name }}
                </option>
              </select>
              <div v-if="selectedReportType" class="alert-success-custom mt-3">
                <i class="bi bi-info-circle me-2"></i>
                <strong>Rate Information:</strong>
                Mileage: ${{ selectedReportType.mileage_rate }}/mile
                | Lodging: ${{ selectedReportType.max_lodging_per_night }}/night
                | Breakfast: ${{ selectedReportType.max_breakfast_daily }}
                | Lunch: ${{ selectedReportType.max_lunch_daily }}
                | Dinner: ${{ selectedReportType.max_dinner_daily }}
              </div>
            </div>
          </div>

          <div class="row g-4 mt-3">
            <div class="col-md-6">
              <label class="form-label">Event Date *</label>
              <input v-model="newReport.report_date" type="date" class="form-control" required>
            </div>
          </div>

          <!-- Mailing Address Selection -->
          <div class="form-section mt-4">
            <h6 class="form-section-title">
              <i class="bi bi-mailbox me-2"></i>Mailing Address
            </h6>
            <div class="info-alert mb-3">
              <i class="bi bi-info-circle-fill"></i>
              <div class="info-alert-content">
                Select the address where you would like your reimbursement check to be mailed.
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Select Address *</label>
              <select v-model="newReport.mailing_address" class="form-select" required>
                <option value="">Choose an address...</option>
                <option v-for="address in userAddresses" :key="address.id" :value="address.id">
                  {{ address.add_type }}{{ address.is_primary ? ' (Primary)' : '' }} - {{ address.display_name }}
                </option>
              </select>
            </div>

            <div class="mt-2">
              <router-link to="/account" class="btn btn-sm btn-outline-secondary">
                <i class="bi bi-pencil me-1"></i>Manage Addresses
              </router-link>
            </div>
          </div>

          <h6 class="mt-5 mb-3" style="font-weight: 600; color: #1a202c;">Expense Details</h6>

          <!-- Automobile Expenses -->
          <div class="expense-section">
            <div class="expense-section-header">
              <i class="bi bi-car-front"></i>
              Automobile
            </div>
            <div class="expense-section-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Miles Driven</label>
                  <input v-model.number="newReport.details.automobile_miles" type="number" step="0.01" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Tolls ($)</label>
                  <input v-model.number="newReport.details.automobile_tolls" type="number" step="0.01" class="form-control">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Passengers</label>
                  <input v-model.number="newReport.details.passengers" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Lodging -->
          <div class="expense-section">
            <div class="expense-section-header">
              <i class="bi bi-house-door"></i>
              Lodging
            </div>
            <div class="expense-section-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Number of Nights</label>
                  <input v-model.number="newReport.details.lodging_nights" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Cost Per Night ($)</label>
                  <input v-model.number="newReport.details.lodging_per_night" type="number" step="0.01" class="form-control">
                </div>
              </div>
            </div>
          </div>

          <!-- Meals En Route -->
          <div class="expense-section">
            <div class="expense-section-header">
              <i class="bi bi-cup-hot"></i>
              Meals En Route
            </div>
            <div class="expense-section-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Breakfasts</label>
                  <input v-model.number="newReport.details.breakfast_enroute" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Lunches</label>
                  <input v-model.number="newReport.details.lunch_enroute" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Dinners</label>
                  <input v-model.number="newReport.details.dinner_enroute" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Meals On-Site -->
          <div class="expense-section">
            <div class="expense-section-header">
              <i class="bi bi-egg-fried"></i>
              Meals On-Site
            </div>
            <div class="expense-section-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Breakfasts</label>
                  <input v-model.number="newReport.details.breakfast_onsite" type="number" class="form-control" min="0">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Lunches</label>
                  <input v-model.number="newReport.details.lunch_onsite" type="number" class="form-control" min="0">
                </div>
              </div>
            </div>
          </div>

          <!-- Other Expenses -->
          <div class="expense-section">
            <div class="expense-section-header">
              <i class="bi bi-receipt"></i>
              Other Expenses
            </div>
            <div class="expense-section-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="form-label">Terminal Costs ($)</label>
                  <input v-model.number="newReport.details.terminal_cost" type="number" step="0.01" class="form-control">
                  <small class="form-text">Airport parking, etc.</small>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Public Carrier ($)</label>
                  <input v-model.number="newReport.details.public_carrier_cost" type="number" step="0.01" class="form-control">
                  <small class="form-text">Airline, train, bus</small>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Other On-Site ($)</label>
                  <input v-model.number="newReport.details.other_onsite_cost" type="number" step="0.01" class="form-control">
                </div>
              </div>
              <div class="mt-3">
                <label class="form-label">Additional Notes</label>
                <textarea v-model="newReport.details.expense_notes" class="form-control" rows="3"></textarea>
              </div>
              <div class="form-check mt-3">
                <input v-model="newReport.details.billed_to_hq" type="checkbox" class="form-check-input" id="billedToHq">
                <label class="form-check-label" for="billedToHq">
                  Billed directly to headquarters
                </label>
              </div>
            </div>
          </div>

          <!-- Receipt Upload Section -->
          <div class="form-section mt-4">
            <h4 class="form-section-title">
              <i class="bi bi-receipt me-2"></i>Receipt Upload
            </h4>
            <div class="alert alert-info" style="background: #eff6ff; border-left: 4px solid #284080;">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Important:</strong> You must upload receipts showing each charge you are claiming. 
              Accepted formats: PNG, JPG, PDF. Maximum 10MB per file, 50MB total.
            </div>
            
            <div class="form-group">
              <label class="form-label">Receipt Files *</label>
              <input 
                type="file" 
                ref="receiptInput"
                class="form-control" 
                @change="handleReceiptUpload" 
                multiple
                accept="image/png,image/jpeg,application/pdf"
              >
              <small class="form-text text-muted">
                Select one or more files (PNG, JPG, or PDF). They will be combined into a single PDF.
              </small>
            </div>

            <!-- Preview of selected files -->
            <div v-if="selectedReceipts.length > 0" class="mt-3">
              <strong>Selected Files ({{ selectedReceipts.length }}):</strong>
              <ul class="list-group mt-2">
                <li v-for="(file, index) in selectedReceipts" :key="index" class="list-group-item d-flex justify-content-between align-items-center">
                  <span>
                    <i :class="getFileIcon(file.name)" class="me-2"></i>
                    {{ file.name }}
                  </span>
                  <div>
                    <span class="badge bg-secondary me-2">{{ formatFileSize(file.size) }}</span>
                    <button type="button" class="btn btn-sm btn-outline-danger" @click="removeReceipt(index)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </li>
              </ul>
              <div class="mt-2">
                <strong>Total Size:</strong> {{ formatFileSize(totalReceiptSize) }}
              </div>
            </div>
          </div>

          <div v-if="error" class="alert alert-danger mt-4" style="border-left: 4px solid #ef4444;">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
          </div>

          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="button" class="btn btn-secondary" @click="cancelCreate">
              <i class="bi bi-x-lg me-2"></i>Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading">
                <span class="spinner-border spinner-border-sm me-2"></span>Creating...
              </span>
              <span v-else>
                <i class="bi bi-check2 me-2"></i>Create Report
              </span>
            </button>
          </div>
        </form>
      </div>

      <!-- Loading State -->
      <div v-if="loading && !showCreateForm" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading expense reports...</p>
      </div>

      <!-- Reports List -->
      <div v-else-if="expenseReports.length > 0" class="section-card">
        <div class="section-header">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-file-earmark-text"></i>
            </div>
            Your Expense Reports
          </h2>
        </div>

        <div v-if="success" class="alert-success-custom mb-4">
          <i class="bi bi-check-circle-fill me-2"></i>{{ success }}
        </div>

        <div class="table-responsive">
          <table class="table table-custom">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Chapter</th>
                <th>Date</th>
                <th>Status</th>
                <th>Amount</th>
                <th>Created</th>
                <th style="width: 120px;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in expenseReports" :key="report.id">
                <td style="font-weight: 600; color: #1a202c;">
                  #{{ report.id }}
                </td>
                <td>
                  <span class="badge" style="background: #f1f5f9; color: #1a202c; font-weight: 600;">
                    {{ report.report_type_code }}
                  </span>
                  <br>
                  <small class="text-muted">{{ report.report_type_name }}</small>
                </td>
                <td>{{ report.chapter }}</td>
                <td style="color: #64748b; font-size: 0.875rem;">
                  {{ formatDate(report.report_date) }}
                </td>
                <td>
                  <span :class="getStatusBadgeClass(report.status)">
                    {{ report.status_display }}
                  </span>
                </td>
                <td style="font-weight: 600; color: #1a202c;">
                  ${{ report.total_amount }}
                </td>
                <td style="color: #64748b; font-size: 0.875rem;">
                  {{ formatDate(report.created_at) }}
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-custom" @click="viewReport(report.id)">
                    <i class="bi bi-eye me-1"></i>View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="section-card text-center py-5">
        <i class="bi bi-file-earmark-text" style="font-size: 4rem; color: var(--brand-blue); opacity: 0.3;"></i>
        <h3 class="mt-4">No Expense Reports Yet</h3>
        <p class="text-muted">You haven't created any expense reports yet. Get started by creating your first report.</p>
        <button class="btn btn-primary mt-3" @click="showCreateForm = true">
          <i class="bi bi-plus-circle me-2"></i>Create Your First Report
        </button>
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
            <h5 class="modal-title text-white">
              Expense Report #{{ selectedReport.id }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <!-- Report Information -->
            <div class="row mb-4">
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Report Information</h6>
                <table class="table table-sm">
                  <tbody>
                  <tr>
                    <th style="width: 40%;">Report Type:</th>
                    <td>
                      <span class="badge" style="background: #f1f5f9; color: #1a202c; font-weight: 600;">
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
                    <th>Mailing Address:</th>
                    <td v-if="selectedReport.mailing_address">
                      <div class="small">
                        <strong>{{ selectedReport.mailing_address.add_type }}</strong>
                        <span v-if="selectedReport.mailing_address.is_primary" class="badge bg-primary ms-1">Primary</span>
                      </div>
                      <div class="text-muted small">
                        {{ selectedReport.mailing_address.display_name }}
                      </div>
                    </td>
                    <td v-else class="text-muted">Not specified</td>
                  </tr>
                  <tr>
                    <th>Submitted:</th>
                    <td>{{ formatDateTime(selectedReport.created_at) }}</td>
                  </tr>
                  </tbody>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Status</h6>
                <table class="table table-sm">
                  <tbody>
                  <tr>
                    <th style="width: 40%;">Status:</th>
                    <td>
                      <span :class="getStatusBadgeClass(selectedReport.status)">
                        {{ selectedReport.status_display }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="selectedReport.review_date">
                    <th>Review Date:</th>
                    <td>{{ formatDateTime(selectedReport.review_date) }}</td>
                  </tr>
                  <tr v-if="selectedReport.approval_date">
                    <th>Approval Date:</th>
                    <td>{{ formatDateTime(selectedReport.approval_date) }}</td>
                  </tr>
                  <tr v-if="selectedReport.paid_date">
                    <th>Paid Date:</th>
                    <td>{{ formatDateTime(selectedReport.paid_date) }}</td>
                  </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Expense Details -->
            <h6 class="text-muted mb-3">Expense Details</h6>
            
            <!-- Automobile -->
            <div class="card mb-3" v-if="selectedReport.details.automobile_miles > 0 || selectedReport.details.automobile_tolls > 0">
              <div class="card-header bg-light">
                <i class="bi bi-car-front me-2"></i>Automobile
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4" v-if="selectedReport.details.automobile_miles > 0">
                    <small class="text-muted">Miles Driven</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.automobile_miles }} miles</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.mileage_rate }}/mile = ${{ (selectedReport.details.automobile_miles * selectedReport.report_type_detail.mileage_rate).toFixed(2) }}</small>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.automobile_tolls > 0">
                    <small class="text-muted">Tolls</small>
                    <p class="mb-0 fw-bold">${{ selectedReport.details.automobile_tolls }}</p>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.passengers > 0">
                    <small class="text-muted">Passengers</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.passengers }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Lodging -->
            <div class="card mb-3" v-if="selectedReport.details.lodging_nights > 0">
              <div class="card-header bg-light">
                <i class="bi bi-house-door me-2"></i>Lodging
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <small class="text-muted">Number of Nights</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.lodging_nights }}</p>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted">Cost Per Night</small>
                    <p class="mb-0 fw-bold">${{ selectedReport.details.lodging_per_night }}</p>
                    <small class="text-muted">Total: ${{ (selectedReport.details.lodging_nights * selectedReport.details.lodging_per_night).toFixed(2) }}</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Meals En Route -->
            <div class="card mb-3" v-if="selectedReport.details.breakfast_enroute > 0 || selectedReport.details.lunch_enroute > 0 || selectedReport.details.dinner_enroute > 0">
              <div class="card-header bg-light">
                <i class="bi bi-cup-hot me-2"></i>Meals En Route
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4" v-if="selectedReport.details.breakfast_enroute > 0">
                    <small class="text-muted">Breakfasts</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.breakfast_enroute }}</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.max_breakfast_daily }} = ${{ (selectedReport.details.breakfast_enroute * selectedReport.report_type_detail.max_breakfast_daily).toFixed(2) }}</small>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.lunch_enroute > 0">
                    <small class="text-muted">Lunches</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.lunch_enroute }}</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.max_lunch_daily }} = ${{ (selectedReport.details.lunch_enroute * selectedReport.report_type_detail.max_lunch_daily).toFixed(2) }}</small>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.dinner_enroute > 0">
                    <small class="text-muted">Dinners</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.dinner_enroute }}</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.max_dinner_daily }} = ${{ (selectedReport.details.dinner_enroute * selectedReport.report_type_detail.max_dinner_daily).toFixed(2) }}</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Meals On-Site -->
            <div class="card mb-3" v-if="selectedReport.details.breakfast_onsite > 0 || selectedReport.details.lunch_onsite > 0">
              <div class="card-header bg-light">
                <i class="bi bi-egg-fried me-2"></i>Meals On-Site
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6" v-if="selectedReport.details.breakfast_onsite > 0">
                    <small class="text-muted">Breakfasts</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.breakfast_onsite }}</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.max_breakfast_daily }} = ${{ (selectedReport.details.breakfast_onsite * selectedReport.report_type_detail.max_breakfast_daily).toFixed(2) }}</small>
                  </div>
                  <div class="col-md-6" v-if="selectedReport.details.lunch_onsite > 0">
                    <small class="text-muted">Lunches</small>
                    <p class="mb-0 fw-bold">{{ selectedReport.details.lunch_onsite }}</p>
                    <small class="text-muted">@ ${{ selectedReport.report_type_detail.max_lunch_daily }} = ${{ (selectedReport.details.lunch_onsite * selectedReport.report_type_detail.max_lunch_daily).toFixed(2) }}</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Other Expenses -->
            <div class="card mb-3" v-if="selectedReport.details.terminal_cost > 0 || selectedReport.details.public_carrier_cost > 0 || selectedReport.details.other_onsite_cost > 0">
              <div class="card-header bg-light">
                <i class="bi bi-receipt me-2"></i>Other Expenses
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4" v-if="selectedReport.details.terminal_cost > 0">
                    <small class="text-muted">Terminal Costs</small>
                    <p class="mb-0 fw-bold">${{ selectedReport.details.terminal_cost }}</p>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.public_carrier_cost > 0">
                    <small class="text-muted">Public Carrier</small>
                    <p class="mb-0 fw-bold">${{ selectedReport.details.public_carrier_cost }}</p>
                  </div>
                  <div class="col-md-4" v-if="selectedReport.details.other_onsite_cost > 0">
                    <small class="text-muted">Other On-Site</small>
                    <p class="mb-0 fw-bold">${{ selectedReport.details.other_onsite_cost }}</p>
                  </div>
                </div>
                <div v-if="selectedReport.details.billed_to_hq" class="mt-2">
                  <span class="badge bg-info">Billed directly to headquarters</span>
                </div>
              </div>
            </div>

            <!-- Notes -->
            <div v-if="selectedReport.details.expense_notes" class="card mb-3">
              <div class="card-header bg-light">
                <i class="bi bi-file-text me-2"></i>Additional Notes
              </div>
              <div class="card-body">
                <p class="mb-0">{{ selectedReport.details.expense_notes }}</p>
              </div>
            </div>

            <!-- Total Amount -->
            <div class="alert alert-success">
              <div class="d-flex justify-content-between align-items-center">
                <strong>Total Reimbursement Amount:</strong>
                <h4 class="mb-0">${{ selectedReport.total_amount }}</h4>
              </div>
            </div>

            <!-- Admin Notes (if any) -->
            <div v-if="selectedReport.notes" class="alert alert-info">
              <strong>Administrator Notes:</strong>
              <p class="mb-0 mt-2">{{ selectedReport.notes }}</p>
            </div>

            <!-- Rejection Reason (if rejected) -->
            <div v-if="selectedReport.status === 'rejected' && selectedReport.rejection_reason" class="alert alert-danger">
              <strong>Rejection Reason:</strong>
              <p class="mb-0 mt-2">{{ selectedReport.rejection_reason }}</p>
            </div>

            <!-- Receipt -->
            <div class="card mb-3">
              <div class="card-header bg-light">
                <i class="bi bi-receipt me-2"></i>Receipt
              </div>
              <div class="card-body">
                <div v-if="selectedReport.receipt_url">
                  <a :href="selectedReport.receipt_url" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                    <i class="bi bi-file-earmark-pdf me-2"></i>View Receipt PDF
                  </a>
                  <p class="text-muted mt-2 mb-0">
                    <small>Click to open the combined receipt PDF in a new tab</small>
                  </p>
                </div>
                <div v-else class="text-muted">
                  <i class="bi bi-exclamation-triangle me-2"></i>No receipt uploaded
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-danger" data-bs-dismiss="modal">
              Close
            </button>
          </div>
        </div>
      </div>
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
      userAddresses: [],
      showCreateForm: false,
      loading: false,
      error: null,
      success: null,
      selectedReport: null,
      detailModal: null,
      selectedReceipts: [],
      newReport: {
        report_type: '',
        mailing_address: '',
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
    },
    totalReceiptSize() {
      return this.selectedReceipts.reduce((sum, file) => sum + file.size, 0)
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
        
        // Load user's addresses from accounts app
        const addressesResponse = await api.get('/api/accounts/addresses/')
        this.userAddresses = addressesResponse.data
        
        // Load user's reports
        const reportsResponse = await api.get('/api/expense-reports/my-reports/')
        this.expenseReports = reportsResponse.data.results ?? reportsResponse.data
      } catch (err) {
        console.error('Error loading expense reports:', err)
        this.error = 'Failed to load expense reports. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    onReportTypeChange() {
    },
    
    async createReport() {
      if (this.loading) return
      this.loading = true
      this.error = null
      this.success = null
      
      // Validate mailing address
      if (!this.newReport.mailing_address) {
        this.error = 'Please select a mailing address.'
        this.loading = false
        return
      }
      
      // Validate receipts
      if (this.selectedReceipts.length === 0) {
        this.error = 'Please upload at least one receipt file.'
        this.loading = false
        return
      }
      
      try {
        // First create the report
        const response = await api.post('/api/expense-reports/my-reports/', this.newReport)
        const newReport = response.data
        
        // Then upload receipts
        try {
          await this.uploadReceipts(newReport.id)
          
          // Reload the report to get the updated data with receipt URL
          const updatedResponse = await api.get(`/api/expense-reports/my-reports/${newReport.id}/`)
          this.expenseReports.unshift(updatedResponse.data)
          
          this.success = 'Expense report created successfully with receipts!'
          this.resetForm()
          this.showCreateForm = false
          
          // Clear success message after 3 seconds
          setTimeout(() => {
            this.success = null
          }, 3000)
        } catch (uploadErr) {
          // Report was created but receipt upload failed
          this.expenseReports.unshift(newReport)
          this.error = 'Report created, but receipt upload failed: ' + (uploadErr.response?.data?.error || uploadErr.message)
          this.loading = false
          return
        }
      } catch (err) {
        console.error('Error creating expense report:', err)
        const data = err.response?.data
        if (data && typeof data === 'object') {
          this.error = data.error || Object.values(data).flat().join(' ') || 'Failed to create expense report. Please try again.'
        } else {
          this.error = 'Failed to create expense report. Please try again.'
        }
      } finally {
        this.loading = false
      }
    },
    
    cancelCreate() {
      this.resetForm()
      this.showCreateForm = false
      this.error = null
    },
    
    resetForm() {
      this.newReport = {
        report_type: '',
        mailing_address: '',
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
      this.selectedReceipts = []
      if (this.$refs.receiptInput) {
        this.$refs.receiptInput.value = ''
      }
    },
    
    handleReceiptUpload(event) {
      const files = Array.from(event.target.files)
      
      // Validate file types
      const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
      const invalidFiles = files.filter(f => !allowedTypes.includes(f.type))
      
      if (invalidFiles.length > 0) {
        this.error = `Invalid file type(s). Only PNG, JPG, and PDF files are allowed.`
        return
      }
      
      // Validate file sizes
      const maxFileSize = 10 * 1024 * 1024 // 10MB
      const oversizedFiles = files.filter(f => f.size > maxFileSize)
      
      if (oversizedFiles.length > 0) {
        this.error = `File(s) too large. Maximum size is 10MB per file.`
        return
      }
      
      // Validate total size
      const totalSize = files.reduce((sum, f) => sum + f.size, 0)
      const maxTotalSize = 50 * 1024 * 1024 // 50MB
      
      if (totalSize > maxTotalSize) {
        this.error = `Total file size too large. Maximum total size is 50MB.`
        return
      }
      
      this.selectedReceipts = files
      this.error = null
    },
    
    removeReceipt(index) {
      this.selectedReceipts.splice(index, 1)
      if (this.selectedReceipts.length === 0 && this.$refs.receiptInput) {
        this.$refs.receiptInput.value = ''
      }
    },
    
    async uploadReceipts(reportId) {
      const formData = new FormData()
      
      this.selectedReceipts.forEach(file => {
        formData.append('files', file)
      })
      
      await api.post(`/api/expense-reports/my-reports/${reportId}/upload-receipts/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    },
    
    getFileIcon(filename) {
      const ext = filename.split('.').pop().toLowerCase()
      if (ext === 'pdf') return 'bi bi-file-earmark-pdf text-danger'
      if (['jpg', 'jpeg', 'png'].includes(ext)) return 'bi bi-file-earmark-image text-primary'
      return 'bi bi-file-earmark'
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    
    async viewReport(reportId) {
      this.error = null
      
      try {
        const response = await api.get(`/api/expense-reports/my-reports/${reportId}/`)
        this.selectedReport = response.data
        
        // Show modal
        this.detailModal = new window.bootstrap.Modal(this.$refs.detailModal)
        this.detailModal.show()
      } catch (err) {
        console.error('Error loading report details:', err)
        this.error = 'Failed to load report details. Please try again.'
      }
    },
    
    reportsByStatus(status) {
      return this.expenseReports.filter(r => r.status === status).length
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        submitted: 'badge-status badge-status-submitted',
        reviewed: 'badge-status badge-status-review',
        approved: 'badge-status badge-status-approved',
        paid: 'badge-status badge-status-paid',
        rejected: 'badge-status badge-status-rejected'
      }
      return classes[status] || 'badge-status badge-status-submitted'
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    },
    
    formatDateTime(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString()
    }
  }
}
</script>

<style scoped>
/* Stats Bar */
.stats-bar {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.2;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a202c;
  line-height: 1.2;
}

/* Expense Section Styling */
.expense-section {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.expense-section-header {
  background: #fafbfc;
  padding: 0.875rem 1.25rem;
  font-weight: 600;
  color: #1a202c;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.expense-section-header i {
  color: var(--brand-blue);
  font-size: 1rem;
}

.expense-section-body {
  padding: 1.25rem;
}

/* Status Badges */
.badge-status {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

/* .badge-status-draft removed - no longer used */

.badge-status-submitted {
  background: #dbeafe;
  color: #1e40af;
}

.badge-status-review {
  background: #ede9fe;
  color: #6b21a8;
}

.badge-status-approved {
  background: #dcfce7;
  color: #166534;
}

.badge-status-paid {
  background: #d1fae5;
  color: #065f46;
}

.badge-status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

/* Button Styling */
.gap-2 {
  gap: 0.5rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .stats-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .stats-bar button {
    margin-left: 0 !important;
    width: 100%;
  }
  
  .stat-item {
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f1f5f9;
  }
  
  .stat-item:last-of-type {
    border-bottom: none;
  }
}

/* Table hover effect */
.table-custom tbody tr {
  transition: background-color 0.2s;
}

.table-custom tbody tr:hover {
  background-color: #f8fafc;
}

/* Modal Styles */
.modal-xl {
  max-width: 1200px;
}

.modal-header {
  background: linear-gradient(135deg, #284080 0%, #1a2f5a 100%);
  color: white;
  border-bottom: none;
}

.modal-header .btn-close {
  filter: brightness(0) invert(1);
}

.modal-body h6 {
  font-weight: 600;
  color: #1a202c;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.modal-body .table-sm th {
  color: #64748b;
  font-weight: 500;
  padding: 0.5rem 0;
}

.modal-body .table-sm td {
  color: #1a202c;
  padding: 0.5rem 0;
}

.modal-body .card-header {
  font-weight: 600;
  font-size: 0.875rem;
}
</style>
