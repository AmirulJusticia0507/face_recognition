<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { etleCameraApi } from '../services/api'
import Swal from 'sweetalert2'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapRef = ref(null)
let map = null
let markers = []

const cameras = ref([])
const selectedCamera = ref(null)
const loading = ref(false)
const detecting = ref(false)
const searchQuery = ref('')
const detectedViolations = ref([])
const activeTab = ref('map')

const jogjaCenter = [-7.7956, 110.3695]

const initMap = async () => {
  await nextTick()
  if (!mapRef.value || map) return

  map = L.map(mapRef.value, { zoomControl: true }).setView(jogjaCenter, 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18,
  }).addTo(map)

  addMarkers(cameras.value)
}

const addMarkers = (cams) => {
  if (!map) return
  markers.forEach(m => map.removeLayer(m))
  markers = []

  cams.forEach(cam => {
    if (!cam.lat || !cam.lng) return
    const isOnline = cam.status === 'online'
    const icon = L.divIcon({
      className: 'custom-marker',
      html: `<div class="w-7 h-7 ${isOnline ? 'bg-red-600' : 'bg-gray-400'} rounded-full border-2 border-white shadow-lg flex items-center justify-center">
        <svg class="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/></svg>
      </div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    })

    const marker = L.marker([cam.lat, cam.lng], { icon })
      .addTo(map)
      .bindPopup(`<strong>${cam.name}</strong><br><small>${cam.source} &middot; ${cam.status}</small>`)
      .on('click', () => selectCamera(cam))

    markers.push(marker)
  })
}

const selectCamera = (cam) => {
  selectedCamera.value = cam
  activeTab.value = 'stream'
  if (map) map.setView([cam.lat, cam.lng], 15)
}

const filteredCameras = ref([])

const filterCameras = () => {
  const q = searchQuery.value.toLowerCase()
  filteredCameras.value = cameras.value.filter(c =>
    c.name.toLowerCase().includes(q) || c.source?.toLowerCase().includes(q)
  )
  addMarkers(filteredCameras.value)
}

const detectViolation = async () => {
  if (!selectedCamera.value) return
  detecting.value = true
  try {
    const response = await etleCameraApi.detectViolation({
      stream_url: selectedCamera.value.stream,
      camera: selectedCamera.value.name,
      mode: 'proxy',
    })
    if (response.data.violations?.length > 0) {
      detectedViolations.value.unshift(...response.data.violations)
      const hasReal = response.data.violations.some(v => v.type !== 'normal' && v.type !== 'error')
      Swal.fire({
        icon: hasReal ? 'warning' : 'info',
        title: hasReal ? 'Pelanggaran Terdeteksi' : 'Tidak Ada Pelanggaran',
        text: `${response.data.violations.length} hasil deteksi`,
        timer: 2000,
        showConfirmButton: false,
      })
    }
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'Detection failed', 'error')
  } finally {
    detecting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await etleCameraApi.getJogjaCameras()
    cameras.value = res.data || []
  } catch {
    cameras.value = []
  }
  filteredCameras.value = [...cameras.value]
  await initMap()
  setTimeout(() => { if (map) map.invalidateSize() }, 300)
})

onBeforeUnmount(() => {
  if (map) { map.remove(); map = null }
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-dark-100">ETLE Camera</h1>
      <p class="text-gray-500 dark:text-dark-400 mt-1">Electronic Traffic Law Enforcement - Real-time violation detection dari CCTV DIY</p>
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
            Peta ETLE
          </button>
          <button
            @click="activeTab = 'stream'"
            :class="['flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
              activeTab === 'stream' ? 'bg-white dark:bg-dark-700 text-primary-600 shadow-sm' : 'text-gray-600 dark:text-dark-400']"
          >
            Live Stream & Detect
          </button>
        </div>

        <!-- Map View -->
        <div v-show="activeTab === 'map'" class="card overflow-hidden">
          <div ref="mapRef" class="w-full h-[500px] bg-gray-200 dark:bg-dark-700"></div>
        </div>

        <!-- Stream + Detect View -->
        <div v-show="activeTab === 'stream'" class="card">
          <div class="card-body">
            <div v-if="selectedCamera" class="space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <span :class="['w-2 h-2 rounded-full', selectedCamera.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-gray-400']"></span>
                  <h3 class="font-semibold text-gray-900 dark:text-dark-100">{{ selectedCamera.name }}</h3>
                  <span class="badge-info text-xs">{{ selectedCamera.source }}</span>
                </div>
                <button
                  @click="detectViolation"
                  :disabled="detecting || selectedCamera.status !== 'online'"
                  :class="['btn-primary', detecting ? 'opacity-50 cursor-not-allowed' : '']"
                >
                  <span v-if="detecting" class="flex items-center gap-2">
                    <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" /></svg>
                    Mendeteksi...
                  </span>
                  <span v-else class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    Deteksi Pelanggaran
                  </span>
                </button>
              </div>
              <div class="relative bg-black rounded-lg overflow-hidden aspect-video">
                <iframe
                  v-if="selectedCamera.stream"
                  :src="selectedCamera.stream"
                  class="w-full h-full"
                  frameborder="0"
                  allowfullscreen
                ></iframe>
                <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
                  <p>Stream tidak tersedia</p>
                </div>
              </div>
            </div>
            <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
              <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p>Pilih kamera dari peta atau daftar</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Camera List + Violations -->
      <div class="space-y-4">
        <!-- Camera List -->
        <div class="card flex flex-col max-h-[350px]">
          <div class="card-header">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-dark-100">Kamera ETLE</h2>
              <span class="badge-info">{{ filteredCameras.length }}</span>
            </div>
            <div class="mt-3">
              <input v-model="searchQuery" @input="filterCameras" type="text" placeholder="Cari lokasi..." class="input text-sm" />
            </div>
          </div>
          <div class="flex-1 overflow-y-auto">
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
                <span :class="['w-2 h-2 rounded-full shrink-0', cam.status === 'online' ? 'bg-green-500' : 'bg-gray-400']"></span>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-dark-100 truncate">{{ cam.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-dark-400">{{ cam.source }}</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Violations Log -->
        <div class="card flex flex-col max-h-[350px]">
          <div class="card-header">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-dark-100">Hasil Deteksi</h2>
          </div>
          <div class="flex-1 overflow-y-auto">
            <div v-if="detectedViolations.length === 0" class="p-6 text-center text-gray-500 dark:text-dark-400">
              <p>Belum ada hasil deteksi</p>
            </div>
            <div v-else>
              <div v-for="(v, i) in detectedViolations" :key="i" class="px-4 py-3 border-b border-gray-100 dark:border-dark-700 hover:bg-gray-50 dark:hover:bg-dark-800">
                <div class="flex items-start gap-3">
                  <div :class="['w-8 h-8 rounded-lg flex items-center justify-center shrink-0',
                    v.type === 'normal' ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30']">
                    <svg v-if="v.type === 'normal'" class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    <svg v-else class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                  </div>
                  <div class="min-w-0 flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-dark-100">{{ v.type }}</p>
                    <p class="text-xs text-gray-500 dark:text-dark-400">{{ v.description }}</p>
                    <p class="text-xs text-gray-400 dark:text-dark-500 mt-1">{{ v.camera }} &middot; {{ new Date(v.time).toLocaleTimeString() }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.custom-marker { background: transparent !important; border: none !important; }
</style>
