<script setup>
import { ref, onMounted } from 'vue'
import { personApi } from '../services/api'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

const router = useRouter()

const people = ref([])
const loading = ref(true)
const search = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const perPage = 10
const showDeleteModal = ref(false)
const personToDelete = ref(null)

const fetchPeople = async () => {
  loading.value = true
  try {
    const response = await personApi.list({
      page: currentPage.value,
      per_page: perPage,
      search: search.value,
    })
    people.value = response.data.results || response.data
    totalCount.value = response.data.count || people.value.length
    totalPages.value = Math.ceil(totalCount.value / perPage)
  } catch (error) {
    Swal.fire('Error', 'Failed to load people', 'error')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPeople()
}

const confirmDelete = (person) => {
  personToDelete.value = person
  showDeleteModal.value = true
}

const deletePerson = async () => {
  if (!personToDelete.value) return
  
  try {
    await personApi.delete(personToDelete.value.id)
    Swal.fire('Deleted!', `${personToDelete.value.name} has been removed.`, 'success')
    fetchPeople()
  } catch (error) {
    Swal.fire('Error', 'Failed to delete person', 'error')
  } finally {
    showDeleteModal.value = false
    personToDelete.value = null
  }
}

const viewPerson = (id) => {
  router.push(`/people/${id}`)
}

onMounted(() => {
  fetchPeople()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Data Orang</h1>
        <p class="text-gray-500 mt-1">Manage registered people in the system</p>
      </div>
      <router-link to="/people/register" class="btn-primary">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Person
      </router-link>
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
              placeholder="Search by name, email, or ID..."
              class="input pl-10"
            />
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span>{{ totalCount }} people</span>
          </div>
        </div>
      </div>
    </div>

    <!-- People Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-container">
          <table class="table" v-if="!loading">
            <thead>
              <tr>
                <th class="w-16">Avatar</th>
                <th>Name</th>
                <th>Email</th>
                <th>Photos</th>
                <th>Registered</th>
                <th class="w-24">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="person in people" :key="person.id">
                <td>
                  <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden">
                    <img 
                      v-if="person.avatar" 
                      :src="person.avatar" 
                      :alt="person.name" 
                      class="w-full h-full object-cover"
                    >
                    <svg v-else class="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                </td>
                <td>
                  <div>
                    <p class="font-medium text-gray-900">{{ person.name }}</p>
                    <p class="text-xs text-gray-500">ID: {{ person.id }}</p>
                  </div>
                </td>
                <td>{{ person.email || '-' }}</td>
                <td>
                  <span class="badge badge-info">{{ person.photo_count || 0 }} photos</span>
                </td>
                <td class="text-gray-500">{{ person.created_at ? new Date(person.created_at).toLocaleDateString() : '-' }}</td>
                <td>
                  <div class="flex items-center gap-2">
                    <button
                      @click="viewPerson(person.id)"
                      class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                      aria-label="View person"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      @click="confirmDelete(person)"
                      class="p-2 rounded-lg text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                      aria-label="Delete person"
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

          <div v-if="!loading && people.length === 0" class="p-12 text-center">
            <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 class="text-lg font-medium text-gray-900 mt-4">No people found</h3>
            <p class="text-gray-500 mt-1">Get started by adding a new person</p>
            <router-link to="/people/register" class="btn-primary mt-4 inline-flex">Add Person</router-link>
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
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Delete Person</h3>
      <p class="text-gray-500 mb-6">Are you sure you want to delete <strong>{{ personToDelete?.name }}</strong>? This action cannot be undone.</p>
      <div class="flex justify-end gap-3">
        <button @click="showDeleteModal = false" class="btn-secondary">Cancel</button>
        <button @click="deletePerson" class="btn-danger">Delete</button>
      </div>
    </div>
  </div>
</template>