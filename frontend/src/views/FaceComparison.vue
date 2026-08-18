<script setup>
import { ref } from 'vue'
import { faceComparisonApi } from '../services/api'
import Swal from 'sweetalert2'

const model = ref('ArcFace')
const models = ['ArcFace', 'Facenet', 'VGG-Face', 'OpenFace', 'DeepFace', 'DeepID', 'Dlib']
const fotoA = ref(null)
const fotoB = ref(null)
const previewA = ref(null)
const previewB = ref(null)
const loading = ref(false)
const result = ref(null)
const dragActiveA = ref(false)
const dragActiveB = ref(false)

const handleFileA = (file) => {
  if (file && file.type.startsWith('image/')) {
    fotoA.value = file
    previewA.value = URL.createObjectURL(file)
  }
}

const handleFileB = (file) => {
  if (file && file.type.startsWith('image/')) {
    fotoB.value = file
    previewB.value = URL.createObjectURL(file)
  }
}

const handleDropA = (e) => {
  e.preventDefault()
  dragActiveA.value = false
  const file = e.dataTransfer.files[0]
  handleFileA(file)
}

const handleDropB = (e) => {
  e.preventDefault()
  dragActiveB.value = false
  const file = e.dataTransfer.files[0]
  handleFileB(file)
}

const handleDragOver = (e, side) => {
  e.preventDefault()
  if (side === 'a') dragActiveA.value = true
  else dragActiveB.value = true
}

const handleDragLeave = (e, side) => {
  e.preventDefault()
  if (side === 'a') dragActiveA.value = false
  else dragActiveB.value = false
}

const removeFile = (side) => {
  if (side === 'a') {
    fotoA.value = null
    previewA.value = null
  } else {
    fotoB.value = null
    previewB.value = null
  }
  result.value = null
}

const compareFaces = async () => {
  if (!fotoA.value || !fotoB.value) {
    Swal.fire('Error', 'Please upload both images', 'error')
    return
  }

  loading.value = true
  result.value = null

  try {
    const formData = new FormData()
    formData.append('foto_a', fotoA.value)
    formData.append('foto_b', fotoB.value)
    formData.append('model', model.value)

    const response = await faceComparisonApi.compare(formData)
    result.value = response.data
    
    Swal.fire({
      title: result.value.match ? 'Match Found!' : 'No Match',
      html: `
        <div class="text-left">
          <p><strong>Similarity:</strong> ${result.value.similarity_percent}%</p>
          <p><strong>Model:</strong> ${result.value.model_used}</p>
          <div class="mt-4">
            <p class="text-sm text-gray-500">Quality Scores:</p>
            <div class="grid grid-cols-2 gap-2 mt-2 text-sm">
              <div>Pose: ${result.value.pose_score}%</div>
              <div>Lighting: ${result.value.lighting_score}%</div>
              <div>Occlusion: ${result.value.occlusion_score}%</div>
              <div>Sharpness: ${result.value.sharpness_score}%</div>
            </div>
          </div>
        </div>
      `,
      icon: result.value.match ? 'success' : 'error',
      confirmButtonColor: result.value.match ? '#059669' : '#dc2626',
    })
  } catch (error) {
    Swal.fire('Error', error.response?.data?.error || 'Failed to compare faces', 'error')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  fotoA.value = null
  fotoB.value = null
  previewA.value = null
  previewB.value = null
  result.value = null
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Face Comparison</h1>
      <p class="text-gray-500 mt-1">Compare two faces to verify if they belong to the same person</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Image A -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Image A</h2>
        </div>
        <div class="card-body">
          <div
            class="relative border-2 border-dashed rounded-xl p-8 text-center transition-colors"
            :class="[
              dragActiveA ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400',
              previewA ? 'border-transparent' : ''
            ]"
            @dragover="(e) => handleDragOver(e, 'a')"
            @dragleave="(e) => handleDragLeave(e, 'a')"
            @drop="(e) => handleDropA(e)"
            @click="$refs.inputA?.click()"
          >
            <input
              ref="inputA"
              type="file"
              accept="image/*"
              class="hidden"
              @change="(e) => handleFileA(e.target.files[0])"
            />
            
            <div v-if="!previewA" class="space-y-3">
              <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <p class="text-gray-600">Drag & drop or click to upload</p>
                <p class="text-sm text-gray-400">PNG, JPG up to 10MB</p>
              </div>
            </div>

            <div v-else class="relative inline-block">
              <img :src="previewA" alt="Image A" class="max-w-full max-h-64 rounded-lg shadow-lg" />
              <button
                @click.stop="removeFile('a')"
                class="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center justify-center"
                aria-label="Remove image"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Image B -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Image B</h2>
        </div>
        <div class="card-body">
          <div
            class="relative border-2 border-dashed rounded-xl p-8 text-center transition-colors"
            :class="[
              dragActiveB ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400',
              previewB ? 'border-transparent' : ''
            ]"
            @dragover="(e) => handleDragOver(e, 'b')"
            @dragleave="(e) => handleDragLeave(e, 'b')"
            @drop="(e) => handleDropB(e)"
            @click="$refs.inputB?.click()"
          >
            <input
              ref="inputB"
              type="file"
              accept="image/*"
              class="hidden"
              @change="(e) => handleFileB(e.target.files[0])"
            />
            
            <div v-if="!previewB" class="space-y-3">
              <svg class="w-12 h-12 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <p class="text-gray-600">Drag & drop or click to upload</p>
                <p class="text-sm text-gray-400">PNG, JPG up to 10MB</p>
              </div>
            </div>

            <div v-else class="relative inline-block">
              <img :src="previewB" alt="Image B" class="max-w-full max-h-64 rounded-lg shadow-lg" />
              <button
                @click.stop="removeFile('b')"
                class="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors flex items-center justify-center"
                aria-label="Remove image"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings & Result -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Settings & Result</h2>
        </div>
        <div class="card-body space-y-6">
          <!-- Model Selection -->
          <div>
            <label class="label">Recognition Model</label>
            <select v-model="model" class="input">
              <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">ArcFace recommended for best accuracy</p>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3 pt-4">
            <button
              @click="compareFaces"
              :disabled="loading || !fotoA || !fotoB"
              class="btn-primary flex-1"
            >
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Comparing...
              </span>
              <span v-else>Compare Faces</span>
            </button>
            <button
              @click="resetForm"
              :disabled="loading"
              class="btn-secondary"
            >
              Clear
            </button>
          </div>

          <!-- Result -->
          <div v-if="result" class="space-y-4 p-4 rounded-lg" :class="result.match ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
            <div class="flex items-center gap-3">
              <div :class="result.match ? 'w-10 h-10 rounded-full bg-green-100 flex items-center justify-center' : 'w-10 h-10 rounded-full bg-red-100 flex items-center justify-center'">
                <svg v-if="result.match" class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold" :class="result.match ? 'text-green-800' : 'text-red-800'">
                  {{ result.match ? 'Match Found!' : 'No Match' }}
                </h3>
                <p class="text-sm" :class="result.match ? 'text-green-700' : 'text-red-700'">
                  Similarity: {{ result.similarity_percent }}%
                </p>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4 pt-4 border-t" :class="result.match ? 'border-green-200' : 'border-red-200'">
              <div>
                <p class="text-xs text-gray-500">Model Used</p>
                <p class="font-medium text-gray-900">{{ result.model_used }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Distance</p>
                <p class="font-medium text-gray-900">{{ (result.data?.distance || 0).toFixed(4) }}</p>
              </div>
            </div>

            <!-- Quality Scores -->
            <div class="pt-4 border-t" :class="result.match ? 'border-green-200' : 'border-red-200'">
              <p class="text-xs text-gray-500 mb-3">Image Quality Scores</p>
              <div class="grid grid-cols-4 gap-4">
                <div class="text-center p-3 rounded-lg bg-white">
                  <p class="text-2xl font-bold text-gray-900">{{ result.pose_score }}%</p>
                  <p class="text-xs text-gray-500">Pose</p>
                </div>
                <div class="text-center p-3 rounded-lg bg-white">
                  <p class="text-2xl font-bold text-gray-900">{{ result.lighting_score }}%</p>
                  <p class="text-xs text-gray-500">Lighting</p>
                </div>
                <div class="text-center p-3 rounded-lg bg-white">
                  <p class="text-2xl font-bold text-gray-900">{{ result.occlusion_score }}%</p>
                  <p class="text-xs text-gray-500">Occlusion</p>
                </div>
                <div class="text-center p-3 rounded-lg bg-white">
                  <p class="text-2xl font-bold text-gray-900">{{ result.sharpness_score }}%</p>
                  <p class="text-xs text-gray-500">Sharpness</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>