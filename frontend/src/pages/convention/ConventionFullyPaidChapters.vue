<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useToast } from 'vue-toastification'
import api from '../../api'

const toast = useToast()

// ── State ──────────────────────────────────────────────────────────────────
const chapters = ref([])
const loading = ref(false)

const allChapterOptions = ref([]) // [{id: chp_code, title: "Name - School"}, ...]
const addChapterCode = ref('')
const adding = ref(false)

const editingId = ref(null)
const editForm = ref({ spots_available: 0, spots_used: 0 })
const saving = ref(false)

const deletingId = ref(null)
const deleting = ref(false)

// ── Computed ───────────────────────────────────────────────────────────────
const chapterMap = computed(() =>
  Object.fromEntries(allChapterOptions.value.map(c => [c.id, c.title]))
)

const availableChapterOptions = computed(() => {
  const added = new Set(chapters.value.map(c => c.chapter_code))
  return allChapterOptions.value.filter(c => !added.has(c.id))
})

function chapterDisplayName(code) {
  return chapterMap.value[code] || code
}

const sorted = computed(() =>
  [...chapters.value].sort((a, b) =>
    chapterDisplayName(a.chapter_code).localeCompare(chapterDisplayName(b.chapter_code))
  )
)

// ── Load ───────────────────────────────────────────────────────────────────
async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/convention/admin/fully-paid-chapters/')
    chapters.value = res.data
  } catch {
    toast.error('Failed to load fully paid chapters.')
  } finally {
    loading.value = false
  }
  try {
    const res = await api.get('/api/accounts/chapter-list')
    allChapterOptions.value = Object.values(res.data.chapters)
  } catch {
    toast.error('Failed to load chapter list. The add dropdown may be unavailable.')
  }
}

onMounted(load)

// ── Add chapter ────────────────────────────────────────────────────────────
async function addChapter() {
  if (!addChapterCode.value) return
  adding.value = true
  try {
    const res = await api.post('/api/convention/admin/fully-paid-chapters/', { chapter_code: addChapterCode.value })
    chapters.value.push(res.data)
    addChapterCode.value = ''
    toast.success('Chapter added.')
  } catch (err) {
    const msg = err.response?.data?.error || 'Failed to add chapter.'
    toast.error(msg)
  } finally {
    adding.value = false
  }
}

// ── Edit ───────────────────────────────────────────────────────────────────
function openEdit(chapter) {
  editingId.value = chapter.id
  editForm.value = { spots_available: chapter.spots_available, spots_used: chapter.spots_used }
  nextTick(() => {
    showModal('editModal')
  })
}

async function saveEdit() {
  saving.value = true
  try {
    const res = await api.patch(
      `/api/convention/admin/fully-paid-chapters/${editingId.value}/`,
      editForm.value
    )
    const idx = chapters.value.findIndex(c => c.id === editingId.value)
    if (idx !== -1) chapters.value[idx] = res.data
    hideModal('editModal')
    toast.success('Chapter updated.')
  } catch (err) {
    const data = err.response?.data
    const msg = data?.error || data?.spots_available?.[0] || data?.spots_used?.[0] || 'Failed to save changes.'
    toast.error(msg)
  } finally {
    saving.value = false
  }
}

// ── Delete ─────────────────────────────────────────────────────────────────
function openDelete(chapter) {
  deletingId.value = chapter.id
  nextTick(() => showModal('deleteModal'))
}

async function confirmDelete() {
  deleting.value = true
  try {
    await api.delete(`/api/convention/admin/fully-paid-chapters/${deletingId.value}/`)
    chapters.value = chapters.value.filter(c => c.id !== deletingId.value)
    hideModal('deleteModal')
    toast.success('Chapter removed.')
  } catch {
    toast.error('Failed to remove chapter.')
  } finally {
    deleting.value = false
  }
}

// ── Modal helpers ──────────────────────────────────────────────────────────
function showModal(id) {
  nextTick(() => {
    const el = document.getElementById(id)
    if (!el) return
    const m = window.bootstrap?.Modal?.getInstance(el) || new window.bootstrap.Modal(el)
    m.show()
  })
}

function hideModal(id) {
  const el = document.getElementById(id)
  if (!el) return
  window.bootstrap?.Modal?.getInstance(el)?.hide()
}

// ── Helpers ────────────────────────────────────────────────────────────────
function spotsRemaining(chapter) {
  return Math.max(0, chapter.spots_available - chapter.spots_used)
}

function deletingChapter() {
  return chapters.value.find(c => c.id === deletingId.value)
}
</script>

<template>
  <div>
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Fully Paid Chapters</h1>
        <p class="page-subtitle">
          Manage per-chapter fully-paid registration quotas for the active convention.
        </p>
      </div>
    </div>

    <div class="content-container">

      <!-- Add Chapter -->
      <div class="card mb-4">
        <div class="card-body">
          <h6 class="card-title mb-3">Add Chapter</h6>
          <form class="d-flex gap-2 align-items-end" @submit.prevent="addChapter">
            <div>
              <label class="form-label mb-1 small fw-semibold">Chapter</label>
              <select
                v-model="addChapterCode"
                class="form-select"
                style="min-width: 320px;"
                :disabled="adding || !availableChapterOptions.length"
              >
                <option value="" disabled>Select a chapter…</option>
                <option v-for="ch in availableChapterOptions" :key="ch.id" :value="ch.id">
                  {{ ch.title }}
                </option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary" :disabled="adding || !addChapterCode">
              <span v-if="adding" class="spinner-border spinner-border-sm me-1"></span>
              Add Chapter
            </button>
          </form>
        </div>
      </div>

      <!-- Chapters Table -->
      <div class="card">
        <div class="card-body p-0">
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary"></div>
          </div>

          <div v-else-if="!sorted.length" class="text-center py-5 text-muted">
            No chapters added yet. Use the form above to add one.
          </div>

          <table v-else class="table table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>Chapter</th>
                <th class="text-center">Spots Available</th>
                <th class="text-center">Spots Used</th>
                <th class="text-center">Spots Remaining</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in sorted" :key="chapter.id">
                <td class="fw-semibold">{{ chapterDisplayName(chapter.chapter_code) }}</td>
                <td class="text-center">{{ chapter.spots_available }}</td>
                <td class="text-center">{{ chapter.spots_used }}</td>
                <td class="text-center">
                  <span
                    class="badge"
                    :class="spotsRemaining(chapter) > 0 ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ spotsRemaining(chapter) }}
                  </span>
                </td>
                <td class="text-end">
                  <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(chapter)">
                    <i class="bi bi-pencil"></i> Edit
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="openDelete(chapter)">
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editModalLabel">Edit Spots</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label fw-semibold">Spots Available</label>
              <input
                v-model.number="editForm.spots_available"
                type="number"
                min="0"
                class="form-control"
              />
            </div>
            <div class="mb-1">
              <label class="form-label fw-semibold">Spots Used</label>
              <input
                v-model.number="editForm.spots_used"
                type="number"
                min="0"
                class="form-control"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal" :disabled="saving">Cancel</button>
            <button class="btn btn-primary" @click="saveEdit" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-sm">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteModalLabel">Remove Chapter</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Remove <strong>{{ chapterDisplayName(deletingChapter()?.chapter_code) }}</strong> from the fully paid program?
            This cannot be undone.
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal" :disabled="deleting">Cancel</button>
            <button class="btn btn-danger" @click="confirmDelete" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
