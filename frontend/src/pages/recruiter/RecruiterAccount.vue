<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Account Settings</h1>
        <p class="page-subtitle">Manage your login credentials</p>
      </div>
    </div>

    <div class="content-container">
      <div class="section-card">
        <h5 class="fw-bold mb-4"><i class="bi bi-person me-2"></i>Account Information</h5>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Email Address</label>
            <input type="email" class="form-control" :value="authStore.user?.email" disabled>
            <small class="form-text">Your login email cannot be changed. Please contact <a href="mailto:tbp.it@tbp.org">tbp.it@tbp.org</a> with any concerns.</small>
          </div>
        </div>
      </div>

      <ChangePasswordSection />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../store/auth'
import ChangePasswordSection from '../../components/ChangePasswordSection.vue'

const authStore = useAuthStore()
</script>
