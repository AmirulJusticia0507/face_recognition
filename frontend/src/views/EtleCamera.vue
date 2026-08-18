<script setup>
import { ref, onMounted } from 'vue'
import { etleCameraApi } from '../services/api'
import Swal from 'sweetalert2'

const videoRef = ref(null)
const streaming = ref(false)
const loading = ref(false)
const detectedViolations = ref([])
const selectedCamera = ref('camera-1')
const cameras = ref([
  { id: 'camera-1', name: 'Camera 1 - Main Gate', status: 'online' },
  { id: 'camera-2', name: 'Camera 2 - Parking Lot', status: 'offline' },
  { id: 'camera-3', name: 'Camera 3 - Side Entrance', status: 'online' },
])

const startCamera = async () => {
  try {
    loading.value = true
    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      streaming.value = true
    }
  } catch (err) {
    Swal.fire('Error', 'Cannot access camera: ' + err.message, 'error')
  } finally {
    loading.value = false
  }
}

const detectViolation = async () => {
  if (!videoRef.value) return
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
  const imageData = canvas.toDataURL('image/jpeg')
  
  try {
    const response = await etleCameraApi.detectViolation({ image: imageData, camera: selectedCamera.value })
    if (response.data.violations.length > 0) {
      detectedViolations.value.unshift(...response.data.violations)
      Swal.fire({ icon: 'warning', title: 'Violations Detected', text: `${response.data.violations.length} violation(s) found`, timer: 2000, showConfirmButton: false })
    }
  } catch (err) {
    console.error('Detection failed:', err)
  }
}

onMounted(() => {
  etleCameraApi.getCameras().then(res => { cameras.value = res.data || cameras.value }).catch(() => {})
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">ETLE Camera</h1>
      <p class="text-gray-500 mt-1">Electronic Traffic Law Enforcement - Real-time violation detection</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Camera Feed -->
      <div class="lg:col-span-2 card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">Camera Feed</h2>
            <select v-model="selectedCamera" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 mt-1">
              <option v-for="cam in cameras" :key="cam.id" :value="cam.id">{{ cam.name }}</option>
            </select>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="streaming" class="flex items-center gap-2 text-sm text-green-600">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Live
            </span>
          </div>
        </div>
        <div class="card-body">
          <div class="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
            <video ref="videoRef" class="w-full h-full object-cover" :class="{ hidden: !streaming }" autoplay playsinline muted></video>
            <div v-if="!streaming" class="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
              <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              <p>Select a camera and start streaming</p>
            </div>
          </div>
          <div class="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
            <button v-if="!streaming" @click="startCamera" :disabled="loading" class="btn-success">Start Camera</button>
            <button v-else @click="streaming = false; $el.closest('.card').querySelector('video')?.srcObject?.getTracks().forEach(t => t.stop())" class="btn-danger">Stop</button>
            <button v-if="streaming" @click="detectViolation" class="btn-primary">Detect Violations</button>
          </div>
        </div>
      </div>

      <!-- Camera List & Violations -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Detected Violations</h2>
        </div>
        <div class="card-body p-0">
          <div v-if="detectedViolations.length === 0" class="p-6 text-center text-gray-500">
            <p>No violations detected yet</p>
          </div>
          <div v-else class="divide-y divide-gray-100 max-h-[500px] overflow-y-auto">
            <div v-for="(v, i) in detectedViolations" :key="i" class="px-4 py-3 hover:bg-gray-50">
              <div class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ v.type }}</p>
                  <p class="text-xs text-gray-500">{{ v.description }}</p>
                  <p class="text-xs text-gray-400 mt-1">{{ v.time }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>