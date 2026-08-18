<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { liveCameraApi } from '../services/api'
import Swal from 'sweetalert2'

const videoRef = ref(null)
const canvasRef = ref(null)
const streaming = ref(false)
const loading = ref(false)
const detectedExpression = ref('')
const snapshots = ref([])
const showSnapshots = ref(false)
let stream = null
let detectionInterval = null

const startCamera = async () => {
  try {
    loading.value = true
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.play()
      streaming.value = true
    }
  } catch (err) {
    Swal.fire('Error', 'Cannot access camera: ' + err.message, 'error')
  } finally {
    loading.value = false
  }
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (detectionInterval) {
    clearInterval(detectionInterval)
    detectionInterval = null
  }
  streaming.value = false
  detectedExpression.value = ''
}

const captureFrame = () => {
  if (!videoRef.value || !canvasRef.value) return null
  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  return canvas.toDataURL('image/jpeg', 0.8)
}

const saveSnapshot = async () => {
  const imageData = captureFrame()
  if (!imageData) return
  
  try {
    await liveCameraApi.saveSnapshot({
      image_base64: imageData,
      detected_expression: detectedExpression.value,
    })
    Swal.fire({ icon: 'success', title: 'Snapshot saved', timer: 1500, showConfirmButton: false })
  } catch (error) {
    Swal.fire('Error', 'Failed to save snapshot', 'error')
  }
}

const loadSnapshots = async () => {
  showSnapshots.value = true
  try {
    const response = await liveCameraApi.getSnapshots({ limit: 20 })
    snapshots.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to load snapshots')
  }
}

const deleteSnapshot = async (id) => {
  try {
    await liveCameraApi.deleteSnapshot(id)
    snapshots.value = snapshots.value.filter(s => s.id !== id)
    Swal.fire({ icon: 'success', title: 'Deleted', timer: 1500, showConfirmButton: false })
  } catch (error) {
    Swal.fire('Error', 'Failed to delete snapshot', 'error')
  }
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Live Camera</h1>
        <p class="text-gray-500 mt-1">Real-time face detection and snapshot capture</p>
      </div>
      <button @click="loadSnapshots" class="btn-secondary">View Snapshots</button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Camera Feed -->
      <div class="lg:col-span-2 card">
        <div class="card-header flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">Camera Feed</h2>
          <div class="flex items-center gap-2">
            <span v-if="streaming" class="flex items-center gap-2 text-sm text-green-600">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Live
            </span>
            <span v-else class="text-sm text-gray-500">Offline</span>
          </div>
        </div>
        <div class="card-body">
          <div class="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
            <video
              ref="videoRef"
              class="w-full h-full object-cover"
              :class="{ 'hidden': !streaming }"
              autoplay
              playsinline
              muted
            ></video>
            <canvas ref="canvasRef" class="hidden"></canvas>
            <div v-if="!streaming" class="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
              <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              </svg>
              <p>Camera feed will appear here</p>
            </div>
          </div>

          <!-- Controls -->
          <div class="flex flex-wrap items-center justify-between gap-4 mt-4 pt-4 border-t border-gray-100">
            <div class="flex items-center gap-3">
              <button
                v-if="!streaming"
                @click="startCamera"
                :disabled="loading"
                class="btn-success"
              >
                <span v-if="loading" class="flex items-center gap-2">
                  <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg>
                  Starting...
                </span>
                <span v-else>Start Camera</span>
              </button>
              <button v-else @click="stopCamera" class="btn-danger">Stop Camera</button>
              <button v-if="streaming" @click="saveSnapshot" class="btn-primary">
                <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /></svg>
                Snapshot
              </button>
            </div>
            <div v-if="detectedExpression" class="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              Expression: <strong>{{ detectedExpression }}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Panel -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Information</h2>
        </div>
        <div class="card-body space-y-4">
          <div class="p-4 bg-blue-50 rounded-lg">
            <h3 class="font-medium text-blue-900">How it works</h3>
            <ul class="text-sm text-blue-700 mt-2 space-y-1">
              <li>1. Click "Start Camera" to begin</li>
              <li>2. Position your face in the frame</li>
              <li>3. Click "Snapshot" to capture</li>
              <li>4. View saved snapshots above</li>
            </ul>
          </div>

          <div class="space-y-3">
            <h3 class="font-medium text-gray-900">Settings</h3>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span class="text-sm text-gray-600">Resolution</span>
              <span class="text-sm font-medium text-gray-900">640x480</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span class="text-sm text-gray-600">Quality</span>
              <span class="text-sm font-medium text-gray-900">80%</span>
            </div>
          </div>

          <div class="p-4 bg-yellow-50 rounded-lg">
            <h3 class="font-medium text-yellow-900">Tips</h3>
            <ul class="text-sm text-yellow-700 mt-2 space-y-1">
              <li>- Ensure good lighting</li>
              <li>- Face the camera directly</li>
              <li>- Avoid wearing sunglasses</li>
              <li>- Keep a neutral expression</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Snapshots Modal -->
    <div v-if="showSnapshots" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/50" @click="showSnapshots = false"></div>
      <div class="relative bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col animate-fade-in">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-semibold text-gray-900">Saved Snapshots</h3>
          <button @click="showSnapshots = false" class="p-2 rounded-lg text-gray-500 hover:bg-gray-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="snapshots.length === 0" class="text-center py-12 text-gray-500">
            <p>No snapshots yet</p>
          </div>
          <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <div v-for="snap in snapshots" :key="snap.id" class="relative group">
              <img :src="snap.foto_a" alt="Snapshot" class="w-full aspect-square object-cover rounded-lg border border-gray-200" />
              <div class="absolute inset-0 bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <button @click="deleteSnapshot(snap.id)" class="p-2 bg-red-500 rounded-full text-white hover:bg-red-600">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ snap.created_at ? new Date(snap.created_at).toLocaleString() : '' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>