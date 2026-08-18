<script setup>
import { ref, onMounted } from 'vue'
import { violationLogsApi } from '../services/api'
import Swal from 'sweetalert2'

const logs = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const perPage = 15
const showDeleteModal = ref(false)
const logToDelete = ref(null)
const stats = ref({ total: 0, today: 0, thisWeek: 0 })

const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await violationLogsApi.list({ page: currentPage.value, per_page: perPage })
    logs.value = response.data.results || response.data
    totalCount.value = response.data.count || logs.value.length
    totalPages.value = Math.ceil(totalCount.value / perPage)
  } catch (error) {
    console.error('Failed to load logs:', error)
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await violationLogsApi.getStats()
    stats.value = response.data
  } catch (error) { /* ignore */ }
}

const confirmDelete = (log) => { logToDelete.value = log; showDeleteModal.value = true }

const deleteLog = async () => {
  if (!logToDelete.value) return
  try {
    await violationLogsApi.delete(logToDelete.value.id)
    Swal.fire('Deleted!', 'Violation log has been removed.', 'success')
    fetchLogs()
  } catch (error) {
    Swal.fire('Error', 'Failed to delete log', 'error')
  } finally {
    showDeleteModal.value = false
    logToDelete.value = null
  }
}

const getTypeBadge = (type) => {
  const types = {
    speeding: 'badge-danger',
    red_light: 'badge-warning',
    no_helmet: 'badge-warning',
    unauthorized: 'badge-info',
    default: 'badge-info',
  }
  return types[type] || types.default
}

const formatDate = (dateString) => new Date(dateString).toLocaleString()

onMounted(() => {
  fetchLogs()
  fetchStats()
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Violation Logs</h1>
      <p class="text-gray-500 mt-1">View and manage detected traffic violations</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card">
        <div class="card-body text-center">
          <p class="text-3xl font-bold text-gray-900">{{ stats.total }}</p>
          <p class="text-sm text-gray-500">Total Violations</p>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <p class="text-3xl font-bold text-orange-600">{{ stats.today }}</p>
          <p class="text-sm text-gray-500">Today</p>
        </div>
      </div>
      <div class="card">
        <div class="card-body text-center">
          <p class="text-3xl font-bold text-blue-600">{{ stats.thisWeek }}</p>
          <p class="text-sm text-gray-500">This Week</p>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-container">
          <table class="table" v-if="!loading">
            <thead>
              <tr>
                <th>#</th>
                <th>Time</th>
                <th>Type</th>
                <th>Camera</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, index) in logs" :key="log.id">
                <td class="text-gray-500">{{ (currentPage - 1) * perPage + index + 1 }}</td>
                <td>{{ formatDate(log.violation_time) }}</td>
                <td><span :class="getTypeBadge(log.violation_type)" class="badge">{{ log.violation_type }}</span></td>
                <td>{{ log.camera_name || '-' }}</td>
                <td class="max-w-xs truncate">{{ log.description || '-' }}</td>
                <td>
                  <div class="flex items-center gap-2">
                    <button v-if="log.foto_a" @click="window.open(log.foto_a, '_blank')" class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    </button>
                    <button @click="confirmDelete(log)" class="p-2 rounded-lg text-gray-500 hover:bg-red-50 hover:text-red-600">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <div v-if="!loading && logs.length === 0" class="p-12 text-center">
            <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            <h3 class="text-lg font-medium text-gray-900 mt-4">No violations found</h3>
            <p class="text-gray-500 mt-1">No violation logs have been recorded yet</p>
          </div>
        </div>

        <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
          <span class="text-sm text-gray-500">Page {{ currentPage }} of {{ totalPages }}</span>
          <div class="flex items-center gap-2">
            <button @click="currentPage--; fetchLogs()" :disabled="currentPage === 1" class="btn-secondary text-sm">Previous</button>
            <button @click="currentPage++; fetchLogs()" :disabled="currentPage === totalPages" class="btn-secondary text-sm">Next</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Modal -->
  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/50" @click="showDeleteModal = false"></div>
    <div class="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6 animate-fade-in">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Violation Log</h3>
      <p class="text-gray-500 mb-6">Are you sure you want to delete this violation log? This action cannot be undone.</p>
      <div class="flex justify-end gap-3">
        <button @click="showDeleteModal = false" class="btn-secondary">Cancel</button>
        <button @click="deleteLog" class="btn-danger">Delete</button>
      </div>
    </div>
  </div>
</template>