<script setup>
import { ref, reactive, onMounted } from 'vue'
import { personApi } from '../services/api'
import Swal from 'sweetalert2'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isEditing = ref(route.params.id)

const form = reactive({
  name: '',
  email: '',
  phone: '',
  address: '',
  notes: '',
})

const photos = ref([])
const previews = ref([])
const loading = ref(false)
const uploadLoading = ref(false)
const dragActive = ref(false)

const fetchPerson = async () => {
  if (!isEditing.value) return
  try {
    const response = await personApi.get(route.params.id)
    form.name = response.data.name
    form.email = response.data.email
    form.phone = response.data.phone
    form.address = response.data.address
    form.notes = response.data.notes
  } catch (error) {
    Swal.fire('Error', 'Failed to load person', 'error')
  }
}

const handleFiles = (files) => {
  const validFiles = Array.from(files).filter(f => f.type.startsWith('image/'))
  if (validFiles.length + photos.value.length > 10) {
    Swal.fire('Error', 'Maximum 10 photos allowed', 'error')
    return
  }
  validFiles.forEach(file => {
    photos.value.push(file)
    previews.value.push(URL.createObjectURL(file))
  })
}

const handleDrop = (e) => {
  e.preventDefault()
  dragActive.value = false
  handleFiles(e.dataTransfer.files)
}

const handleDragOver = (e) => {
  e.preventDefault()
  dragActive.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragActive.value = false
}

const removePhoto = (index) => {
  photos.value.splice(index, 1)
  previews.value.splice(index, 1)
}

const submitForm = async () => {
  if (!form.name || !form.email) {
    Swal.fire('Error', 'Name and email are required', 'error')
    return
  }
  if (!isEditing.value && photos.value.length === 0) {
    Swal.fire('Error', 'At least one photo is required', 'error')
    return
  }

  loading.value = true
  try {
    let personId = isEditing.value
    
    if (!personId) {
      const response = await personApi.create({
        name: form.name,
        email: form.email,
        phone: form.phone,
        address: form.address,
        notes: form.notes,
      })
      personId = response.data.id
    } else {
      await personApi.update(personId, {
        name: form.name,
        email: form.email,
        phone: form.phone,
        address: form.address,
        notes: form.notes,
      })
    }

    if (photos.value.length > 0) {
      uploadLoading.value = true
      const formData = new FormData()
      photos.value.forEach(photo => formData.append('photos', photo))
      await personApi.uploadPhotos(personId, formData)
    }

    Swal.fire('Success', isEditing.value ? 'Person updated' : 'Person registered', 'success')
    router.push('/people')
  } catch (error) {
    Swal.fire('Error', error.response?.data?.error || 'Failed to save person', 'error')
  } finally {
    loading.value = false
    uploadLoading.value = false
  }
}

onMounted(() => {
  if (isEditing.value) {
    fetchPerson()
  }
})
</script>

<template>
  <div class="space-y-6 max-w-3xl mx-auto">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ isEditing ? 'Edit Person' : 'Register Person' }}</h1>
        <p class="text-gray-500 mt-1">{{ isEditing ? 'Update person information' : 'Add a new person to the database' }}</p>
      </div>
      <router-link to="/people" class="btn-secondary">Back to List</router-link>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Personal Info -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Personal Information</h2>
        </div>
        <div class="card-body space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="label">Full Name <span class="text-red-500">*</span></label>
              <input
                type="text"
                v-model="form.name"
                placeholder="Enter full name"
                class="input"
                required
              />
            </div>
            <div>
              <label class="label">Email <span class="text-red-500">*</span></label>
              <input
                type="email"
                v-model="form.email"
                placeholder="Enter email"
                class="input"
                required
              />
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="label">Phone</label>
              <input
                type="tel"
                v-model="form.phone"
                placeholder="Enter phone number"
                class="input"
              />
            </div>
            <div class="sm:col-span-2">
              <label class="label">Address</label>
              <textarea
                v-model="form.address"
                placeholder="Enter address"
                class="input"
                rows="3"
              ></textarea>
            </div>
          </div>
          <div>
            <label class="label">Notes</label>
            <textarea
              v-model="form.notes"
              placeholder="Additional notes"
              class="input"
              rows="3"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- Photos -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Face Photos</h2>
        </div>
        <div class="card-body">
          <p class="text-sm text-gray-500 mb-4">
            {{ isEditing ? 'Add additional photos (optional)' : 'Upload at least one clear face photo' }}
            <span class="text-primary-600"> (max 10 photos)</span>
          </p>
          
          <div
            class="relative border-2 border-dashed rounded-xl p-6 text-center transition-colors mb-4"
            :class="[
              dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400',
              photos.length > 0 ? 'border-transparent p-0' : ''
            ]"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDrop"
            @click="$refs.photoInput?.click()"
          >
            <input
              ref="photoInput"
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              @change="(e) => handleFiles(e.target.files)"
            />
            
            <div v-if="photos.length === 0" class="space-y-3">
              <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <p class="text-gray-600">Drag & drop or click to upload</p>
                <p class="text-sm text-gray-400">PNG, JPG up to 10MB each</p>
              </div>
            </div>
          </div>

          <!-- Photo Previews -->
          <div v-if="photos.length > 0" class="space-y-4">
            <div class="flex flex-wrap gap-3">
              <div v-for="(preview, index) in previews" :key="index" class="relative group w-24 h-24 flex-shrink-0">
                <img :src="preview" alt="Preview" class="w-full h-full object-cover rounded-lg border border-gray-200" />
                <button
                  type="button"
                  @click="removePhoto(index)"
                  class="absolute top-1 right-1 w-6 h-6 rounded-full bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                  aria-label="Remove photo"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 text-xs bg-black/50 text-white px-1.5 py-0.5 rounded">{{ index + 1 }}</span>
              </div>
            </div>
            <p class="text-sm text-gray-500">{{ photos.length }}/10 photos</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3 pt-4">
        <router-link to="/people" class="btn-secondary">Cancel</router-link>
        <button
          type="submit"
          :disabled="loading || uploadLoading"
          class="btn-primary"
        >
          <span v-if="loading || uploadLoading" class="flex items-center gap-2">
            <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            {{ isEditing ? 'Updating...' : 'Registering...' }}
          </span>
          <span v-else>{{ isEditing ? 'Update Person' : 'Register Person' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>