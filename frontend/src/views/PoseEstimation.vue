<script setup>
import { ref } from 'vue'
import { poseEstimationApi } from '../services/api'
import Swal from 'sweetalert2'

const photo = ref(null)
const preview = ref(null)
const loading = ref(false)
const result = ref(null)
const dragActive = ref(false)

const handleFile = (file) => {
  if (file && file.type.startsWith('image/')) {
    photo.value = file
    preview.value = URL.createObjectURL(file)
    result.value = null
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  dragActive.value = false
  handleFile(e.dataTransfer.files[0])
}

const handleDragOver = (e) => { e.preventDefault(); dragActive.value = true }
const handleDragLeave = (e) => { e.preventDefault(); dragActive.value = false }

const removeFile = () => {
  photo.value = null
  preview.value = null
  result.value = null
}

const estimatePose = async () => {
  if (!photo.value) return
  loading.value = true
  result.value = null
  try {
    const formData = new FormData()
    formData.append('photo', photo.value)
    const response = await poseEstimationApi.estimate(formData)
    result.value = response.data
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'Failed to estimate pose', 'error')
  } finally {
    loading.value = false
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreBg = (score) => {
  if (score >= 80) return 'bg-green-100'
  if (score >= 60) return 'bg-yellow-100'
  return 'bg-red-100'
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Pose Estimation</h1>
      <p class="text-gray-500 mt-1">Analyze face pose quality including lighting, occlusion, and sharpness</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Upload -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Upload Face Image</h2>
        </div>
        <div class="card-body">
          <div
            class="relative border-2 border-dashed rounded-xl p-8 text-center transition-colors"
            :class="[dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400', preview ? 'border-transparent' : '']"
            @dragover="handleDragOver" @dragleave="handleDragLeave" @drop="handleDrop"
            @click="$refs.fileInput?.click()"
          >
            <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="(e) => handleFile(e.target.files[0])" />
            <div v-if="!preview" class="space-y-3">
              <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              <p class="text-gray-600">Drag & drop or click to upload</p>
            </div>
            <div v-else class="relative inline-block max-w-full">
              <img :src="preview" alt="Preview" class="max-w-full max-h-80 rounded-lg shadow-lg" />
              <button @click.stop="removeFile" class="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
          </div>
          <div class="flex gap-3 mt-6 pt-4 border-t border-gray-100">
            <button @click="estimatePose" :disabled="loading || !photo" class="btn-primary flex-1">
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg>
                Analyzing...
              </span>
              <span v-else>Analyze Pose</span>
            </button>
            <button @click="removeFile" :disabled="loading" class="btn-secondary">Clear</button>
          </div>
        </div>
      </div>

      <!-- Results -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Analysis Results</h2>
        </div>
        <div class="card-body">
          <div v-if="loading" class="h-64 flex items-center justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
          <div v-else-if="result" class="space-y-6">
            <!-- Overall Score -->
            <div class="text-center p-6 rounded-xl" :class="getScoreBg(result.overall_score)">
              <p class="text-sm text-gray-500 mb-1">Overall Quality Score</p>
              <p class="text-5xl font-bold" :class="getScoreColor(result.overall_score)">{{ result.overall_score }}%</p>
            </div>

            <!-- Individual Scores -->
            <div class="space-y-4">
              <div v-for="(score, key) in { 'Pose Score': result.pose_score, 'Lighting Score': result.lighting_score, 'Occlusion Score': result.occlusion_score, 'Sharpness Score': result.sharpness_score }" :key="key">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">{{ key }}</span>
                  <span class="text-sm font-bold" :class="getScoreColor(score)">{{ score }}%</span>
                </div>
                <div class="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500" :style="{ width: score + '%' }" :class="score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'"></div>
                </div>
              </div>
            </div>

            <!-- Pose Angles -->
            <div v-if="result.angles" class="pt-4 border-t border-gray-100">
              <h3 class="font-medium text-gray-900 mb-3">Detected Angles</h3>
              <div class="grid grid-cols-3 gap-3">
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                  <p class="text-lg font-bold text-gray-900">{{ result.angles.pitch }}°</p>
                  <p class="text-xs text-gray-500">Pitch</p>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                  <p class="text-lg font-bold text-gray-900">{{ result.angles.yaw }}°</p>
                  <p class="text-xs text-gray-500">Yaw</p>
                </div>
                <div class="text-center p-3 bg-gray-50 rounded-lg">
                  <p class="text-lg font-bold text-gray-900">{{ result.angles.roll }}°</p>
                  <p class="text-xs text-gray-500">Roll</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="h-64 flex flex-col items-center justify-center text-gray-400">
            <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            <p>Upload an image to analyze pose quality</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>