<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Convention Registration</h1>
        <p class="page-subtitle">Select your booth package and meal preference</p>
      </div>
    </div>

    <div class="content-container">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <template v-else>
        <!-- Already registered -->
        <div v-if="registration" class="section-card">
          <h5 class="fw-bold mb-3"><i class="bi bi-check-circle me-2"></i>Current Registration</h5>
          <div class="row g-3">
            <div class="col-md-6">
              <p><strong>Status:</strong>
                <span class="badge" :class="statusClass">{{ registration.status.charAt(0).toUpperCase() + registration.status.slice(1) }}</span>
              </p>
              <p><strong>Package:</strong> {{ registration.booth_package_detail?.name }}</p>
              <p><strong>Price:</strong> ${{ registration.booth_package_detail?.price }}</p>
            </div>
            <div class="col-md-6">
              <p v-if="registration.booth_id"><strong>Booth ID:</strong> {{ registration.booth_id }}</p>
              <p v-if="registration.meal_option_detail"><strong>Meal:</strong> {{ registration.meal_option_detail.name }}</p>
              <p v-if="registration.special_requests"><strong>Special Requests:</strong> {{ registration.special_requests }}</p>
            </div>
          </div>

          <!-- Edit form (only if pending) -->
          <div v-if="registration.status === 'pending'" class="mt-4">
            <hr>
            <h6 class="fw-bold">Update Registration</h6>
            <form @submit.prevent="updateRegistration">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Booth Package *</label>
                  <select v-model="editForm.booth_package" class="form-select" required @change="onPackageChange">
                    <option v-for="pkg in packages" :key="pkg.id" :value="pkg.id">
                      {{ pkg.name }} - ${{ pkg.price }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6" v-if="selectedPackageIsInPerson">
                  <label class="form-label">Meal Option *</label>
                  <select v-model="editForm.meal_option" class="form-select" :required="selectedPackageIsInPerson">
                    <option :value="null">Select meal...</option>
                    <option v-for="meal in mealOptions" :key="meal.id" :value="meal.id">
                      {{ meal.name }}
                    </option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Special Requests</label>
                  <textarea v-model.trim="editForm.special_requests" class="form-control" rows="3" maxlength="500"></textarea>
                </div>
              </div>
              <button type="submit" class="btn btn-primary mt-3" :disabled="saving">
                <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Updating...</span>
                <span v-else><i class="bi bi-check2 me-2"></i>Update Registration</span>
              </button>
            </form>
          </div>
        </div>

        <!-- New registration -->
        <div v-else class="section-card">
          <h5 class="fw-bold mb-4">Choose Your Booth Package</h5>

          <!-- Package Cards -->
          <div class="row g-3 mb-4">
            <div v-for="pkg in packages" :key="pkg.id" class="col-md-6">
              <div
                class="p-3 border rounded"
                :class="{ 'border-primary': newForm.booth_package === pkg.id }"
                style="cursor: pointer;"
                @click="selectPackage(pkg)"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="fw-bold mb-1">{{ pkg.name }}</h6>
                    <p class="text-muted mb-1" v-if="pkg.description">{{ pkg.description }}</p>
                    <div>
                      <span v-if="pkg.is_in_person" class="badge bg-info me-1">In-Person</span>
                      <span v-else class="badge bg-secondary me-1">Virtual</span>
                      <span v-if="pkg.includes_resume_access" class="badge bg-success">Resume Access</span>
                    </div>
                  </div>
                  <div class="text-end">
                    <strong style="font-size: 1.25rem;">${{ pkg.price }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <form @submit.prevent="createRegistration">
            <div v-if="selectedNewPackageIsInPerson" class="row g-3 mb-3">
              <div class="col-md-6">
                <label class="form-label">Meal Option *</label>
                <select v-model="newForm.meal_option" class="form-select" required>
                  <option :value="null">Select meal...</option>
                  <option v-for="meal in mealOptions" :key="meal.id" :value="meal.id">
                    {{ meal.name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Special Requests</label>
              <textarea v-model.trim="newForm.special_requests" class="form-control" rows="3" maxlength="500"></textarea>
            </div>

            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <button type="submit" class="btn btn-primary" :disabled="saving || !newForm.booth_package">
              <span v-if="saving"><span class="spinner-border spinner-border-sm me-2"></span>Registering...</span>
              <span v-else><i class="bi bi-check2 me-2"></i>Register for Convention</span>
            </button>
          </form>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

const packages = ref([])
const mealOptions = ref([])
const registration = ref(null)

const newForm = ref({
  booth_package: null,
  meal_option: null,
  special_requests: '',
})

const editForm = ref({
  booth_package: null,
  meal_option: null,
  special_requests: '',
})

const selectedNewPackageIsInPerson = computed(() => {
  const pkg = packages.value.find(p => p.id === newForm.value.booth_package)
  return pkg?.is_in_person || false
})

const selectedPackageIsInPerson = computed(() => {
  const pkg = packages.value.find(p => p.id === editForm.value.booth_package)
  return pkg?.is_in_person || false
})

const statusClass = computed(() => {
  const map = {
    pending: 'bg-warning text-dark',
    approved: 'bg-success',
    confirmed: 'bg-primary',
    cancelled: 'bg-secondary',
  }
  return map[registration.value?.status] || 'bg-secondary'
})

const selectPackage = (pkg) => {
  newForm.value.booth_package = pkg.id
  if (!pkg.is_in_person) {
    newForm.value.meal_option = null
  }
}

const onPackageChange = () => {
  if (!selectedPackageIsInPerson.value) {
    editForm.value.meal_option = null
  }
}

const createRegistration = async () => {
  if (saving.value) return
  errorMessage.value = ''
  saving.value = true
  try {
    const payload = { ...newForm.value }
    if (!selectedNewPackageIsInPerson.value) {
      payload.meal_option = null
    }
    const res = await api.post('/api/recruiters/convention/register/', payload)
    registration.value = res.data
    toast.success('Registration submitted!')
  } catch (error) {
    console.error('Registration error:', error)
    errorMessage.value = 'Registration failed. Please check your selections and try again.'
  } finally {
    saving.value = false
  }
}

const updateRegistration = async () => {
  if (saving.value) return
  saving.value = true
  try {
    const payload = { ...editForm.value }
    if (!selectedPackageIsInPerson.value) {
      payload.meal_option = null
    }
    const res = await api.put('/api/recruiters/convention/my-registration/', payload)
    registration.value = res.data
    toast.success('Registration updated!')
  } catch (error) {
    toast.error(error.response?.data?.error || 'Update failed.')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [pkgRes, mealRes, regRes] = await Promise.allSettled([
      api.get('/api/recruiters/convention/booth-packages/'),
      api.get('/api/recruiters/convention/meal-options/'),
      api.get('/api/recruiters/convention/my-registration/'),
    ])

    if (pkgRes.status === 'fulfilled') packages.value = pkgRes.value.data
    if (mealRes.status === 'fulfilled') mealOptions.value = mealRes.value.data
    if (regRes.status === 'fulfilled' && regRes.value.data.id) {
      registration.value = regRes.value.data
      editForm.value = {
        booth_package: regRes.value.data.booth_package,
        meal_option: regRes.value.data.meal_option,
        special_requests: regRes.value.data.special_requests || '',
      }
    }
  } catch (error) {
    console.error('Error loading convention data:', error)
  } finally {
    loading.value = false
  }
})
</script>
