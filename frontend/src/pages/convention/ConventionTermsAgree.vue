<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api'
import ConventionTermsContent from '../../components/ConventionTermsContent.vue'

const route = useRoute()
const token = route.params.token

const state = ref('loading') // loading | valid | invalid | agreed | error
const invalidReason = ref('')
const personInfo = ref(null)
const convention = ref(null)
const agreeing = ref(false)

onMounted(async () => {
  try {
    const res = await api.get(`/api/convention/terms/${token}/`)
    if (res.data.valid) {
      personInfo.value = { first_name: res.data.first_name, last_name: res.data.last_name }
      convention.value = { name: res.data.convention_name, location: res.data.convention_location }
      state.value = 'valid'
    } else {
      invalidReason.value = res.data.reason || 'This link is invalid.'
      state.value = 'invalid'
    }
  } catch {
    state.value = 'error'
  }
})

async function agree() {
  agreeing.value = true
  try {
    await api.post(`/api/convention/terms/${token}/`)
    state.value = 'agreed'
  } catch {
    state.value = 'error'
  } finally {
    agreeing.value = false
  }
}
</script>

<template>
  <div class="terms-page">
    <!-- Sticky header -->
    <div class="terms-header">
      <img src="/logo_circle_blue.png" alt="Tau Beta Pi" width="48" height="48" />
      <div>
        <h5 class="mb-0">Tau Beta Pi</h5>
        <p class="mb-0 text-muted small">Convention Terms Agreement</p>
      </div>
    </div>

    <div class="terms-body">

      <!-- Loading -->
      <div v-if="state === 'loading'" class="section-card text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-3 text-muted">Validating your link…</p>
      </div>

      <!-- Invalid / expired -->
      <div v-else-if="state === 'invalid'" class="section-card text-center py-5">
        <i class="bi bi-x-circle-fill text-danger" style="font-size: 3rem;"></i>
        <h4 class="mt-3">Link Unavailable</h4>
        <p class="text-muted">{{ invalidReason }}</p>
        <p class="text-muted small">
          If you need assistance, please contact
          <a href="mailto:tbp.convention@tbp.org">tbp.convention@tbp.org</a>.
        </p>
      </div>

      <!-- Error -->
      <div v-else-if="state === 'error'" class="section-card text-center py-5">
        <i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 3rem;"></i>
        <h4 class="mt-3">Something went wrong</h4>
        <p class="text-muted">
          Please try again or contact
          <a href="mailto:tbp.convention@tbp.org">tbp.convention@tbp.org</a>.
        </p>
      </div>

      <!-- Already agreed -->
      <div v-else-if="state === 'agreed'" class="section-card text-center py-5">
        <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
        <h4 class="mt-3">Agreement Recorded</h4>
        <p class="text-muted">
          Thank you, {{ personInfo?.first_name }}. Your agreement to the
          <strong>{{ convention?.name }}</strong> terms and conditions has been recorded.
          You may close this window.
        </p>
      </div>

      <!-- Valid — show terms -->
      <div v-else-if="state === 'valid'" class="section-card">
        <div class="section-header mb-0">
          <h2 class="section-title">
            <div class="section-icon">
              <i class="bi bi-file-earmark-text"></i>
            </div>
            {{ convention.name }} Terms and Conditions
          </h2>
        </div>

        <div class="info-alert mt-4">
          <i class="bi bi-info-circle-fill"></i>
          <div class="info-alert-content">
            Hi <strong>{{ personInfo.first_name }}</strong>, Tau Beta Pi Headquarters has registered you as an
            attendee for the <strong>{{ convention.name }}</strong>. Please read the terms and conditions
            below and click <strong>I Agree</strong> to finalize your registration.
          </div>
        </div>

        <p class="text-muted mt-3 mb-4">
          If you have any questions or concerns regarding these policies, please contact us at
          <a href="mailto:tbp.convention@tbp.org">tbp.convention@tbp.org</a>.
        </p>

        <ConventionTermsContent :convention="convention" />

        <div class="policy-agreement mt-4">
          <button
            class="btn btn-primary btn-lg w-100"
            :disabled="agreeing"
            @click="agree"
          >
            <span v-if="agreeing" class="spinner-border spinner-border-sm me-2"></span>
            I Agree to the Terms and Conditions
          </button>
          <p class="text-muted small text-center mt-2">
            By clicking above you confirm that you have read and agree to all policies listed.
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.terms-page {
  min-height: 100vh;
  background: #f8f9fc;
}

.terms-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.terms-body {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 80px;
}

.policy-agreement {
  background: var(--brand-blue-light);
  border: 1.5px solid #c3d0e8;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}
</style>
