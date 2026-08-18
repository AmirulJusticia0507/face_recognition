<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { liveCameraApi } from '../services/api'
import Swal from 'sweetalert2'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const CCTV_API = import.meta.env.VITE_API_URL || ''
const MINIO_URL = import.meta.env.VITE_MINIO_URL || ''

const mapRef = ref(null)
let map = null
let markers = []

const cameras = ref([])
const selectedCamera = ref(null)
const loading = ref(false)
const searchQuery = ref('')
const activeTab = ref('map')
const streaming = ref(false)
const videoRef = ref(null)
const canvasRef = ref(null)
const snapshots = ref([])
const showSnapshots = ref(false)
let stream = null

const jogjaCenter = [-7.7956, 110.3695]

const defaultCameras = [
  { id: 1, name: 'Simpang APMD (PTZ)', lat: -7.791971853164589, lng: 110.39164423942567, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_apmd.stream/playlist.m3u8' },
  { id: 2, name: 'Simpang Gondomanan (PTZ)', lat: -7.801683039634787, lng: 110.36917244417295, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_gondomanan.stream/playlist.m3u8' },
  { id: 3, name: 'Simpang Jokteng Kulon (PTZ)', lat: -7.81294, lng: 110.35594, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_joktengkulon.stream/playlist.m3u8' },
  { id: 4, name: 'Simpang Jokteng Wetan', lat: -7.814380894891082, lng: 110.36806762218477, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_joktengwetan.stream/playlist.m3u8' },
  { id: 5, name: 'Simpang KM Nol (PTZ)', lat: -7.8010758219105565, lng: 110.36475215767108, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_kmnol.stream/playlist.m3u8' },
  { id: 6, name: 'Simpang Permata (PTZ)', lat: -7.8015437731163875, lng: 110.37307262420656, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_permata.stream/playlist.m3u8' },
  { id: 7, name: 'Simpang PKU Muh. (PTZ)', lat: -7.801283, lng: 110.362061, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_pkumuh.stream/playlist.m3u8' },
  { id: 8, name: 'Simpang Sentul (PTZ)', lat: -7.801442745827733, lng: 110.3779435343926, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/atcs/ATCS_sentul.stream/playlist.m3u8' },
  { id: 9, name: 'Sungai Gajah Wong 2', lat: -7.790914106163658, lng: 110.39598405361177, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/bpbd/BPBD_gajahwong2.stream/playlist.m3u8' },
  { id: 10, name: 'Sungai Winongo', lat: -7.789489704931309, lng: 110.35666287355627, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/bpbd/BPBD_kaliwinongo.stream/playlist.m3u8' },
  { id: 11, name: 'Sungai Ngentak', lat: -7.722645179146617, lng: 110.38926337561489, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/bpbd/BPBD_ngentak.stream/playlist.m3u8' },
  { id: 12, name: 'Malioboro_Selatan_Teteg', lat: -7.789968068779914, lng: 110.36602878685423, source: 'jogjakota', stream: 'https://cctvjss.jogjakota.go.id/malioboro/Malioboro_1_Selatan_Teteg.stream/playlist.m3u8' },
]

const filteredCameras = ref(defaultCameras)

const fetchCameras = async () => {
  loading.value = true
  try {
    const response = await fetch(CCTV_API + 'api/devices/', {
      headers: { 'Accept': 'application/json' }
    })
    if (response.ok) {
      const data = await response.json()
      const apiCameras = (data.results || data).map((cam, i) => ({
        id: cam.id || i + 100,
        name: cam.name || cam.location || `Camera ${i + 1}`,
        lat: parseFloat(cam.lat || cam.latitude || jogjaCenter[0]),
        lng: parseFloat(cam.lng || cam.longitude || jogjaCenter[1]),
        source: cam.source || 'ai-cctv',
        stream: cam.stream_url || cam.stream || '',
        status: cam.status || 'unknown',
      }))
      if (apiCameras.length > 0) {
        defaultCameras.push(...apiCameras)
      }
    }
  } catch (err) {
    console.warn('CCTV API not available, using default cameras')
  } finally {
    loading.value = false
    filteredCameras.value = [...defaultCameras]
    loading.value = false
  }
}

const initMap = async () => {
  await nextTick()
  if (!mapRef.value || map) return

  map = L.map(mapRef.value, {
    zoomControl: true,
    attributionControl: true,
  }).setView(jogjaCenter, 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  }).addTo(map)

  addMarkers(filteredCameras.value)
}

const addMarkers = (cams) => {
  if (!map) return
  markers.forEach(m => map.removeLayer(m))
  markers = []

  cams.forEach(cam => {
    const icon = L.divIcon({
      className: 'custom-marker',
      html: `<div class="w-6 h-6 bg-primary-600 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
        <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>
      </div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })

    const marker = L.marker([cam.lat, cam.lng], { icon })
      .addTo(map)
      .bindPopup(`<strong>${cam.name}</strong><br><small>${cam.source}</small>`)
      .on('click', () => selectCamera(cam))

    markers.push(marker)
  })
}

const selectCamera = (cam) => {
  selectedCamera.value = cam
  activeTab.value = 'stream'
  if (map) {
    map.setView([cam.lat, cam.lng], 15)
  }
}

const filterCameras = () => {
  const q = searchQuery.value.toLowerCase()
  filteredCameras.value = defaultCameras.filter(c =>
    c.name.toLowerCase().includes(q) || c.source.toLowerCase().includes(q)
  )
  addMarkers(filteredCameras.value)
}

const startLocalCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.play()
      streaming.value = true
    }
  } catch (err) {
    Swal.fire('Error', 'Cannot access camera: ' + err.message, 'error')
  }
}

const stopLocalCamera = () => {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
  streaming.value = false
}

const captureFrame = () => {
  if (!videoRef.value || !canvasRef.value) return null
  const v = videoRef.value
  const c = canvasRef.value
  c.width = v.videoWidth
  c.height = v.videoHeight
  c.getContext('2d').drawImage(v, 0, 0)
  return c.toDataURL('image/jpeg', 0.8)
}

const saveSnapshot = async () => {
  const imageData = captureFrame()
  if (!imageData) return
  try {
    await liveCameraApi.saveSnapshot({
      image_base64: imageData,
      camera_name: selectedCamera.value?.name || 'Local Camera',
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
    Swal.fire('Error', 'Failed to delete', 'error')
  }
}

onMounted(async () => {
  await fetchCameras()
  await initMap()
  setTimeout(() => { if (map) map.invalidateSize() }, 300)
})

onBeforeUnmount(() => {
  stopLocalCamera()
  if (map) { map.remove(); map = null }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-dark-100">Live Camera CCTV</h1>
        <p class="text-gray-500 dark:text-dark-400 mt-1">Pantau CCTV real-time DIY & face detection</p>
      </div>
      <div class="flex gap-2">
        <button @click="loadSnapshots" class="btn-secondary">Snapshots</button>
        <button v-if="streaming" @click="saveSnapshot" class="btn-primary">Capture</button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left: Map + Stream -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Tab Switcher -->
        <div class="flex gap-1 p-1 bg-gray-100 dark:bg-dark-800 rounded-lg">
          <button
            @click="activeTab = 'map'"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
              activeTab === 'map' ? 'bg-white dark:bg-dark-700 text-primary-600 shadow-sm' : 'text-gray-600 dark:text-dark-400']"
          >
            Peta CCTV
          </button>
          <button
            @click="activeTab = 'stream'"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
              activeTab === 'stream' ? 'bg-white dark:bg-dark-700 text-primary-600 shadow-sm' : 'text-gray-600 dark:text-dark-400']"
          >
            Live Stream
          </button>
          <button
            @click="activeTab = 'local'"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
              activeTab === 'local' ? 'bg-white dark:bg-dark-700 text-primary-600 shadow-sm' : 'text-gray-600 dark:text-dark-400']"
          >
            Lokal Camera
          </button>
        </div>

        <!-- Map View -->
        <div v-show="activeTab === 'map'" class="card overflow-hidden">
          <div ref="mapRef" class="w-full h-[500px] bg-gray-200 dark:bg-dark-700"></div>
        </div>

        <!-- Stream View -->
        <div v-show="activeTab === 'stream'" class="card">
          <div class="card-body">
            <div v-if="selectedCamera" class="space-y-4">
              <div class="flex items-center gap-3 mb-4">
                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <h3 class="font-semibold text-gray-900 dark:text-dark-100">{{ selectedCamera.name }}</h3>
                <span class="badge-info text-xs">{{ selectedCamera.source }}</span>
              </div>
              <div class="relative bg-black rounded-lg overflow-hidden aspect-video">
                <iframe
                  v-if="selectedCamera.stream"
                  :src="selectedCamera.stream"
                  class="w-full h-full"
                  frameborder="0"
                  allowfullscreen
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope"
                ></iframe>
                <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                  <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <p>Stream tidak tersedia</p>
                  <p class="text-sm mt-1">Klik marker di peta atau pilih kamera lain</p>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="p-3 bg-gray-50 dark:bg-dark-800 rounded-lg">
                  <span class="text-gray-500 dark:text-dark-400">Lokasi</span>
                  <p class="font-medium text-gray-900 dark:text-dark-100">{{ selectedCamera.lat.toFixed(4) }}, {{ selectedCamera.lng.toFixed(4) }}</p>
                </div>
                <div class="p-3 bg-gray-50 dark:bg-dark-800 rounded-lg">
                  <span class="text-gray-500 dark:text-dark-400">Sumber</span>
                  <p class="font-medium text-gray-900 dark:text-dark-100">{{ selectedCamera.source }}</p>
                </div>
              </div>
            </div>
            <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
              <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p>Pilih kamera dari daftar atau peta</p>
            </div>
          </div>
        </div>

        <!-- Local Camera View -->
        <div v-show="activeTab === 'local'" class="card">
          <div class="card-body">
            <div class="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
              <video ref="videoRef" class="w-full h-full object-cover" :class="{ hidden: !streaming }" autoplay playsinline muted></video>
              <canvas ref="canvasRef" class="hidden"></canvas>
              <div v-if="!streaming" class="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                </svg>
                <p>Camera lokal</p>
              </div>
            </div>
            <div class="flex gap-3 mt-4">
              <button v-if="!streaming" @click="startLocalCamera" class="btn-success">Start Camera</button>
              <button v-else @click="stopLocalCamera" class="btn-danger">Stop Camera</button>
              <button v-if="streaming" @click="saveSnapshot" class="btn-primary">Snapshot</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Camera List -->
      <div class="card flex flex-col max-h-[700px]">
        <div class="card-header">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-dark-100">Daftar Kamera</h2>
            <span class="badge-info">{{ filteredCameras.length }}</span>
          </div>
          <div class="mt-3">
            <input
              v-model="searchQuery"
              @input="filterCameras"
              type="text"
              placeholder="Cari lokasi..."
              class="input text-sm"
            />
          </div>
        </div>
        <div class="flex-1 overflow-y-auto">
          <div v-if="loading" class="p-6 text-center text-gray-500">
            <svg class="animate-spin h-8 w-8 mx-auto mb-2 text-primary-600" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg>
            <p>Memuat kamera...</p>
          </div>
          <div v-else-if="filteredCameras.length === 0" class="p-6 text-center text-gray-500">
            Tidak ada kamera ditemukan
          </div>
          <div v-else>
            <button
              v-for="cam in filteredCameras"
              :key="cam.id"
              @click="selectCamera(cam)"
              :class="[
                'w-full text-left px-4 py-3 border-b border-gray-100 dark:border-dark-700 hover:bg-gray-50 dark:hover:bg-dark-800 transition-colors',
                selectedCamera?.id === cam.id ? 'bg-primary-50 dark:bg-primary-900/20 border-l-2 border-l-primary-600' : ''
              ]"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center shrink-0">
                  <svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-dark-100 truncate">{{ cam.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-dark-400">{{ cam.source }}</p>
                </div>
                <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Snapshots Modal -->
    <div v-if="showSnapshots" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/50" @click="showSnapshots = false"></div>
      <div class="relative bg-white dark:bg-dark-800 rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-dark-700">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-dark-100">Saved Snapshots</h3>
          <button @click="showSnapshots = false" class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-dark-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="snapshots.length === 0" class="text-center py-12 text-gray-500">
            <p>No snapshots yet</p>
          </div>
          <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <div v-for="snap in snapshots" :key="snap.id" class="relative group">
              <img :src="snap.foto_a" alt="Snapshot" class="w-full aspect-square object-cover rounded-lg border border-gray-200 dark:border-dark-600" />
              <div class="absolute inset-0 bg-black/50 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <button @click="deleteSnapshot(snap.id)" class="p-2 bg-red-500 rounded-full text-white hover:bg-red-600">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              </div>
              <p class="text-xs text-gray-500 dark:text-dark-400 mt-1">{{ snap.created_at ? new Date(snap.created_at).toLocaleString() : '' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.custom-marker {
  background: transparent !important;
  border: none !important;
}
</style>
