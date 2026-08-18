<script setup>
import { ref } from 'vue'
import { identifyApi } from '../services/api'
import Swal from 'sweetalert2'

const photo = ref(null)
const preview = ref(null)
const model = ref('ArcFace')
const models = ['ArcFace', 'Facenet', 'VGG-Face', 'OpenFace', 'DeepFace', 'DeepID', 'Dlib']
const loading = ref(false)
const result = ref(null)
const error = ref(null)
const dragActive = ref(false)

const handleFile = (file) => {
  if (file && file.type.startsWith('image/')) {
    photo.value = file
    preview.value = URL.createObjectURL(file)
    error.value = null
    result.value = null
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  dragActive.value = false
  const file = e.dataTransfer.files[0]
  handleFile(file)
}

const handleDragOver = (e) => {
  e.preventDefault()
  dragActive.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragActive.value = false
}

const removeFile = () => {
  photo.value = null
  preview.value = null
  result.value = null
  error.value = null
}

const identifyPerson = async () => {
  if (!photo.value) {
    Swal.fire('Error', 'Please upload an image', 'error')
    return
  }

  loading.value = true
  result.value = null
  error.value = null

  try {
    const formData = new FormData()
    formData.append('photo', photo.value)
    formData.append('model', model.value)

    const response = await identifyApi.identify(formData)
    result.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to identify person'
    Swal.fire('Error', error.value, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-6 max-w-4xl mx-auto">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Identifikasi Wajah</h1>
      <p class="text-gray-500 mt-1">Upload a photo to identify a person from the database</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Upload Area -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Upload Photo</h2>
        </div>
        <div class="card-body">
          <div
            class="relative border-2 border-dashed rounded-xl p-8 text-center transition-colors"
            :class="[
              dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400',
              preview ? 'border-transparent' : ''
            ]"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDrop"
            @click="$refs.fileInput?.click()"
          >
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="(e) => handleFile(e.target.files[0])"
            />
            
            <div v-if="!preview" class="space-y-3">
              <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <p class="text-gray-600 text-lg">Drag & drop or click to upload</p>
                <p class="text-sm text-gray-400">PNG, JPG up to 10MB</p>
              </div>
            </div>

            <div v-else class="relative inline-block max-w-full">
              <img :src="preview" alt="Uploaded photo" class="max-w-full max-h-80 rounded-lg shadow-lg" />
              <button
                @click.stop="removeFile"
                class="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center justify-center"
                aria-label="Remove image"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Model Selection -->
          <div class="mt-6">
            <label class="label">Recognition Model</label>
            <select v-model="model" class="input">
              <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3 mt-6 pt-4 border-t border-gray-100">
            <button
              @click="identifyPerson"
              :disabled="loading || !photo"
              class="btn-primary flex-1"
            >
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Identifying...
              </span>
              <span v-else>Identify Person</span>
            </button>
            <button
              @click="removeFile"
              :disabled="loading"
              class="btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      <!-- Result Area -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Result</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>

          <div v-else-if="error" class="h-64 flex items-center justify-center text-center p-4">
            <div class="w-16 h-16 mx-auto rounded-full bg-red-100 flex items-center justify-center mb-4">
              <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <p class="text-red-600 font-medium">{{ error }}</p>
          </div>

          <div v-else-if="result" class="space-y-4">
            <div class="p-4 rounded-lg" :class="result.matched ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
              <div class="flex items-center gap-3">
                <div :class="result.matched ? 'w-12 h-12 rounded-full bg-green-100 flex items-center justify-center' : 'w-12 h-12 rounded-full bg-red-100 flex items-center justify-center'">
                  <svg v-if="result.matched" class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else class="w-7 h-7 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold" :class="result.matched ? 'text-green-800' : 'text-red-800'">
                    {{ result.matched ? 'Person Found!' : 'No Match Found' }}
                  </h3>
                  <p class="text-sm" :class="result.matched ? 'text-green-700' : 'text-red-700'">
                    {{ result.matched ? `Similarity: ${result.similarity_percent}%` : 'Person not in database' }}
                  </p>
                </div>
              </div>
            </div>

            <div v-if="result.matched && result.person" class="space-y-4">
              <h4 class="font-semibold text-gray-900">Person Details</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-gray-500">Name</p>
                  <p class="font-medium text-gray-900">{{ result.person.name }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Email</p>
                  <p class="font-medium text-gray-900">{{ result.person.email || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Phone</p>
                  <p class="font-medium text-gray-900">{{ result.person.phone || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-500">Registered</p>
                  <p class="font-medium text-gray-900">{{ result.person.created_at ? new Date(result.person.created_at).toLocaleDateString() : '-' }}</p>
                </div>
              </div>

              <div v-if="result.person.avatar">
                <p class="text-xs text-gray-500">Avatar</p>
                <img :src="result.person.avatar" :alt="result.person.name" class="w-24 h-24 rounded-full object-cover" />
              </div>
            </div>

            <div class="pt-4 border-t border-gray-100">
              <p class="text-xs text-gray-500 mb-2">Match Details</p>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p class="text-gray-500">Model</p>
                  <p class="font-medium">{{ result.model_used }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Threshold</p>
                  <p class="font-medium">{{ result.threshold }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Distance</p>
                  <p class="font-medium">{{ result.distance }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Similarity</p>
                  <p class="font-medium">{{ result.similarity_percent }}%</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="h-64 flex flex-col items-center justify-center text-center text-gray-400">
            <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <p>Upload a photo to start identification</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>