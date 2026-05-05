<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import api from '../api'

const emit = defineEmits(['close'])
const toast = useToast()

const subject = ref('')
const message = ref('')
const loading = ref(false)
const submitted = ref(false)

async function submit() {
  if (!subject.value.trim() || !message.value.trim()) return
  loading.value = true
  try {
    await api.post('/api/accounts/contact-support', {
      subject: subject.value.trim(),
      message: message.value.trim(),
    })
    submitted.value = true
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to send message. Please try again.'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

function close() {
  emit('close')
}
</script>

<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="support-modal-title">
      <div class="modal-card-header">
        <h5 id="support-modal-title" class="modal-card-title">
          <i class="bi bi-headset me-2"></i>Contact Support
        </h5>
        <button class="modal-card-close" @click="close" aria-label="Close">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <div class="modal-card-body">
        <template v-if="submitted">
          <div class="text-center py-4">
            <i class="bi bi-check-circle-fill" style="font-size: 2.5rem; color: #22c55e;"></i>
            <h6 class="mt-3 mb-2">Message Sent</h6>
            <p class="text-muted mb-4">We received your request and will get back to you shortly.</p>
            <button class="btn btn-primary btn-sm" @click="close">Close</button>
          </div>
        </template>

        <template v-else>
          <p class="text-muted mb-4" style="font-size: 0.9rem;">
            Have a question or need help? Send us a message and we'll get back to you.
          </p>
          <form @submit.prevent="submit">
            <div class="mb-3">
              <label class="form-label">Subject <span class="text-danger">*</span></label>
              <input
                v-model="subject"
                type="text"
                class="form-control"
                placeholder="Brief description of your issue"
                maxlength="150"
                required
                :disabled="loading"
              >
            </div>
            <div class="mb-4">
              <label class="form-label">Message <span class="text-danger">*</span></label>
              <textarea
                v-model="message"
                class="form-control"
                rows="5"
                placeholder="Describe your issue or question in detail..."
                maxlength="2000"
                required
                :disabled="loading"
              ></textarea>
              <div class="text-end mt-1">
                <small class="text-muted">{{ message.length }}/2000</small>
              </div>
            </div>
            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="close" :disabled="loading">
                Cancel
              </button>
              <button
                type="submit"
                class="btn btn-primary btn-sm"
                :disabled="loading || !subject.trim() || !message.trim()"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-1" role="status"></span>
                {{ loading ? 'Sending...' : 'Send Message' }}
              </button>
            </div>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1b2342;
}

.modal-card-close {
  background: none;
  border: none;
  font-size: 1rem;
  color: #718096;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.modal-card-close:hover {
  color: #374151;
}

.modal-card-body {
  padding: 1.25rem 1.5rem 1.5rem;
}
</style>
