<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Invoices</h1>
        <p class="page-subtitle">View your organization's invoices</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else class="section-card">
        <div v-if="invoices.length === 0" class="text-center py-4 text-muted">
          <i class="bi bi-receipt" style="font-size: 3rem; opacity: 0.3;"></i>
          <p class="mt-3">No invoices found.</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-custom">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Amount</th>
                <th>Description</th>
                <th>Status</th>
                <th>Issued</th>
                <th>Due</th>
                <th>Paid</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in invoices" :key="inv.id">
                <td class="fw-medium">{{ inv.invoice_number }}</td>
                <td>${{ inv.amount }}</td>
                <td>{{ inv.description }}</td>
                <td>
                  <span class="badge" :class="statusClass(inv.status)">{{ inv.status.charAt(0).toUpperCase() + inv.status.slice(1) }}</span>
                </td>
                <td>{{ inv.issued_date }}</td>
                <td>{{ inv.due_date }}</td>
                <td>{{ inv.paid_date || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api'

const loading = ref(true)
const invoices = ref([])

const statusClass = (s) => {
  const map = {
    draft: 'bg-secondary',
    sent: 'bg-info',
    paid: 'bg-success',
    cancelled: 'bg-danger',
  }
  return map[s] || 'bg-secondary'
}

onMounted(async () => {
  try {
    const res = await api.get('/api/recruiters/invoices/')
    invoices.value = res.data
  } catch (error) {
    console.error('Error loading invoices:', error)
  } finally {
    loading.value = false
  }
})
</script>
