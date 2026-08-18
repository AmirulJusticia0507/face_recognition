<script setup>
import { ref, onMounted } from 'vue'
import { historyApi } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const history = ref([])
const loading = ref(true)
const search = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const perPage = 15
const showDeleteModal = ref(false)
const itemToDelete = ref(null)

const fetchHistory = async () => {
  loading.value = true
  try {
    const response = await historyApi.list({
      page: currentPage.value,
      per_page: perPage,
      search: search.value,
    })
    history.value = response.data.results || response.data
    totalCount.value = response.data.count || history.value.length
    totalPages.value = Math.ceil(totalCount.value / perPage)
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchHistory()
}

const viewDetail = (item) => {
  router.push(`/history/${item.id}`)
}

const confirmDelete = (item) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  
  try {
    await historyApi.delete(itemToDelete.value.id)
    Swal.fire('Deleted!', 'History item has been removed.', 'success')
    fetchHistory()
  } catch (error) {
    Swal.fire('Error', 'Failed to delete item', 'error')
  } finally {
    showDeleteModal.value = false
    itemToDelete.value = null
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const getVerifiedBadge = (verified) => {
  return verified 
    ? '<span class="badge badge-success">Match</span>' 
    : '<span class="badge badge-danger">No Match</span>'
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">History</h1>
        <p class="text-gray-500 mt-1">View all face comparison history</p>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="card">
      <div class="card-body">
        <div class="flex flex-col sm:flex-row gap-4">
          <div class="relative flex-1">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              v-model="search"
              @keyup.enter="handleSearch"
              placeholder="Search by model, date, or result..."
              class="input pl-10"
            />
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span>{{ totalCount }} records</span>
          </div>
        </div>
      </div>
    </div>

    <!-- History Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-container">
          <table class="table" v-if="!loading">
            <thead>
              <tr>
                <th class="w-10">#</th>
                <th>Date</th>
                <th>Model</th>
                <th>Similarity</th>
                <th>Result</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in history" :key="item.id">
                <td class="text-gray-500">{{ (currentPage - 1) * perPage + index + 1 }}</td>
                <td>{{ formatDate(item.created_at) }}</td>
                <td>{{ item.model_used }}</td>
                <td>
                  <div class="flex items-center gap-2">
                    <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        class="h-full rounded-full transition-all"
                        :style="{ width: item.similarity_percent + '%', backgroundColor: item.verified ? '#10b981' : '#ef4444' }"
                      ></div>
                    </div>
                    <span class="text-sm font-medium">{{ item.similarity_percent }}%</span>
                  </div>
                </td>
                <td v-html="getVerifiedBadge(item.verified)"></td>
                <td>
                  <div class="flex items-center gap-2">
                    <button
                      @click="viewDetail(item)"
                      class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                      aria-label="View details"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      @click="confirmDelete(item)"
                      class="p-2 rounded-lg text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                      aria-label="Delete"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>

          <div v-if="!loading && history.length === 0" class="p-12 text-center">
            <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-lg font-medium text-gray-900 mt-4">No history found</h3>
            <p class="text-gray-500 mt-1">Start comparing faces to see history</p>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
          <div class="text-sm text-gray-500">
            Page {{ currentPage }} of {{ totalPages }}
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="btn-secondary text-sm"
            >
              Previous
            </button>
            <button
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="btn-secondary text-sm"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Modal -->
  <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-black/50" @click="showDeleteModal = false"></div>
    <div class="relative bg-white rounded-xl shadow-xl max-w-md w-full p-6 animate-fade-in">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete History Item</h3>
      <p class="text-gray-500 mb-6">Are you sure you want to delete this comparison record? This action cannot be undone.</p>
      <div class="flex justify-end gap-3">
        <button @click="showDeleteModal = false" class="btn-secondary">Cancel</button>
        <button @click="deleteItem" class="btn-danger">Delete</button>
      </div>
    </div>
  </div>
</template>