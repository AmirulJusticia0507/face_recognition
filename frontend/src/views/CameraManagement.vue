<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import Swal from 'sweetalert2'
import { cameraApi } from '../services/api'

const name = ref('')
const source = ref('jogjakota')
const stream_url = ref('')
const latitude = ref('')
const longitude = ref('')
const status = ref('online')
const description = ref('')
const building = ref('')
const room = ref('')
const floor = ref('')
const auto_scan = ref(false)
const scan_interval_seconds = ref(30)
const isEditing = ref(false)
const cameraId = ref(null)

const cameras = ref([])
const loading = ref(false)

const sourceOptions = [
  { value: 'jogjakota', label: 'Jogja Kota' },
  { value: 'sleman', label: 'Sleman' },
  { value: 'bantul', label: 'Bantul' },
  { value: 'ai_cctv', label: 'AI CCTV' },
]

const statusOptions = [
  { value: 'online', label: 'Online' },
  { value: 'offline', label: 'Offline' },
  { value: 'maintenance', label: 'Maintenance' },
]

const loadCameras = async () => {
  loading.value = true
  try {
    const response = await cameraApi.list()
    cameras.value = response.data
  } catch (err) {
    console.warn('Camera API not available')
    cameras.value = []
  } finally {
    loading.value = false
  }
}

const saveCamera = async () => {
  loading.value = true
  try {
    const payload = {
      name: name.value,
      source: source.value,
      stream_url: stream_url.value,
      latitude: parseFloat(latitude.value) || null,
      longitude: parseFloat(longitude.value) || null,
      status: status.value,
      description: description.value,
      building: building.value || '',
      room: room.value || '',
      floor: floor.value || '',
      auto_scan: auto_scan.value,
      scan_interval_seconds: parseInt(scan_interval_seconds.value) || 30,
    }
    let data
    if (isEditing.value) {
      const response = await cameraApi.update(cameraId.value, payload)
      data = response.data
    } else {
      const response = await cameraApi.create(payload)
      data = response.data
    }

    loadCameras()
    resetForm()
    Swal.fire('Berhasil', isEditing.value ? 'Kamera berhasil diperbarui' : 'Kamera berhasil ditambahkan', 'success')
  } catch (err) {
    const msg = err.response?.data?.detail
      || JSON.stringify(err.response?.data || {})
      || 'Gagal menyimpan camera'
    Swal.fire('Error', msg !== '{}' ? msg : 'Gagal menghubungi server', 'error')
    console.error(err)
  } finally {
    loading.value = false
  }
}

const editCamera = (camera) => {
  name.value = camera.name
  source.value = camera.source
  stream_url.value = camera.stream_url || ''
  latitude.value = camera.latitude != null ? String(camera.latitude) : ''
  longitude.value = camera.longitude != null ? String(camera.longitude) : ''
  status.value = camera.status
  description.value = camera.description || ''
  building.value = camera.building || ''
  room.value = camera.room || ''
  floor.value = camera.floor || ''
  auto_scan.value = camera.auto_scan || false
  scan_interval_seconds.value = camera.scan_interval_seconds || 30
  cameraId.value = camera.id
  isEditing.value = true
}

const deleteCamera = async (id) => {
  if (!confirm('Yakin menghapus camera ini?')) return
  try {
    await cameraApi.delete(id)
    loadCameras()
    Swal.fire('Dihapus', 'Camera berhasil dihapus dari daftar', 'success')
  } catch (err) {
    Swal.fire('Error', 'Gagal menghapus camera', 'error')
  }
}

const scanNow = async (camera) => {
  try {
    const res = await cameraApi.scan(camera.id)
    const data = res.data.results[0]
    if (data.status === 'error') {
      Swal.fire('Error', data.error, 'error')
    } else {
      Swal.fire({
        icon: 'success',
        title: 'Scan selesai',
        html: `Wajah terdeteksi: <strong>${data.face_count}</strong><br>
          Kesamaan: <strong>${data.similarity_percent}%</strong>`,
        timer: 2000,
        showConfirmButton: false,
      })
      loadCameras()
    }
  } catch (err) {
    Swal.fire('Error', 'Gagal melakukan scan kamera', 'error')
  }
}

const toggleAutoScan = async (camera) => {
  try {
    await cameraApi.update(camera.id, { auto_scan: !camera.auto_scan })
    camera.auto_scan = !camera.auto_scan
    loadCameras()
  } catch (err) {
    Swal.fire('Error', 'Gagal mengubah auto-scan', 'error')
  }
}

const resetForm = () => {
  name.value = ''
  source.value = 'jogjakota'
  stream_url.value = ''
  latitude.value = ''
  longitude.value = ''
  status.value = 'online'
  description.value = ''
  building.value = ''
  room.value = ''
  floor.value = ''
  auto_scan.value = false
  scan_interval_seconds.value = 30
  cameraId.value = null
  isEditing.value = false
}
</script>

<template>
<div class="p-6">
  <h1 class="text-2xl font-bold text-gray-900 mb-6">Manajemen Kamera CCTV</h1>

  <!-- Form Kamera -->
  <div class="card mb-6">
    <div class="card-header">Tambah Kamera Baru</div>
    <div class="card-body">
      <form @submit.prevent="saveCamera">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nama Kamera</label>
            <input v-model="name" type="text" class="shadow w-full py-2 rounded" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sumber</label>
            <select v-model="source" class="shadow w-full py-2 rounded">
              <option v-for="opt in sourceOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Stream URL</label>
            <input v-model="stream_url" type="url" class="shadow w-full py-2 rounded" placeholder="https://..." />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
            <input v-model="latitude" type="number" class="shadow w-full py-2 rounded" placeholder="-7.7928" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
            <input v-model="longitude" type="number" class="shadow w-full py-2 rounded" placeholder="110.3659" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="status" class="shadow w-full py-2 rounded">
              <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deskripsi</label>
            <textarea v-model="description" rows="2" class="shadow w-full py-2 rounded"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Gedung/Lokasi</label>
            <input v-model="building" type="text" class="shadow w-full py-2 rounded" placeholder="Misal: Gedung A" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ruangan</label>
            <input v-model="room" type="text" class="shadow w-full py-2 rounded" placeholder="Misal: Lantai 2, Ruang 203" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Lantai</label>
            <input v-model="floor" type="text" class="shadow w-full py-2 rounded" placeholder="Misal: 2" />
          </div>
          <div class="flex items-end">
            <label class="flex items-center gap-2 text-sm text-gray-700">
              <input v-model.bool="auto_scan" type="checkbox" class="h-4 w-4 rounded" />
              Aktifkan auto-scan otomatis
            </label>
          </div>
          <div v-if="auto_scan" class="flex items-end">
            <label class="block text-sm font-medium text-gray-700 mb-1">Interval (detik)</label>
            <input v-model.number="scan_interval_seconds" type="number" min="5" class="shadow w-full py-2 rounded" />
          </div>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <button type="button" @click="resetForm" class="px-3 py-1 text-sm text-gray-500 hover:bg-gray-100">Batal</button>
          <button type="submit" class="px-3 py-1 bg-primary-600 text-white font-medium">Simpan</button>
        </div>
      </form>
    </div>
  </div>

  <!-- Daftar Kamera -->
  <div v-if="!isEditing" class="card">
    <div class="card-header">Daftar Kamera</div>
    <div class="card-body">
      <p v-if="loading">Memuat...</p>
      <p v-else-if="cameras.length === 0">Tidak ada camera terdaftar</p>
      <table v-if="!loading && cameras.length > 0" class="min-w-full table-auto mt-4">
        <thead>
          <tr class="bg-gray-100 text-xs text-gray-500 uppercase">
            <th>#</th>
            <th>Nama</th>
            <th>Lokasi</th>
            <th>Ruangan</th>
            <th>Stream URL</th>
            <th>Auto Scan</th>
            <th>Scan Terakhir</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(cam, i) in cameras" :key="cam.id">
            <td class="text-gray-500">{{ i + 1 }}</td>
            <td class="font-medium">{{ cam.name }}</td>
            <td>{{ cam.building || '-' }}</td>
            <td>{{ cam.room || '-' }}</td>
            <td class="text-xs text-gray-500 truncate max-w-xs">{{ cam.stream_url || '-' }}</td>
            <td>
              <label class="flex items-center gap-2 text-sm">
                <input type="checkbox" :checked="cam.auto_scan" @change="toggleAutoScan(cam)" class="h-4 w-4 rounded" />
                {{ cam.scan_interval_seconds || 30 }}s
              </label>
            </td>
            <td class="text-xs text-gray-400">{{ cam.last_scanned_at ? new Date(cam.last_scanned_at).toLocaleString() : '-' }}</td>
            <td class="text-right">
              <button @click="scanNow(cam)" class="text-green-600 text-sm hover:underline mr-2">Scan</button>
              <button @click="editCamera(cam)" class="text-primary-600 text-sm hover:underline">Edit</button>
              <button @click="deleteCamera(cam.id)" class="text-red-600 text-sm hover:underline ml-2">Hapus</button>
            </td>
          </tr>
        </tbody>
        </table>
      </div>
    </div>
  </div>
</template>