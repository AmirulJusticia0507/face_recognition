<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import Swal from 'sweetalert2'

const CCTV_API = import.meta.env.VITE_API_URL || ''

const name = ref('')
const source = ref('jogjakota')
const stream_url = ref('')
const latitude = ref('')
const longitude = ref('')
const status = ref('online')
const description = ref('')
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
    const response = await fetch(CCTV_API + 'cameras/', {
      headers: { 'Accept': 'application/json' }
    })
    if (response.ok) {
      cameras.value = await response.json()
    }
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
    }
    const method = isEditing.value ? 'PUT' : 'POST'
    const endpoint = isEditing.value
      ? CCTV_API + 'cameras/' + cameraId.value + '/'
      : CCTV_API + 'cameras/'

    const response = await fetch(endpoint, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const data = await response.json()
    if (response.ok) {
      loadCameras()
      resetForm()
      Swal.fire('Berhasil', isEditing.value ? 'Kamera berhasil diperbarui' : 'Kamera berhasil ditambahkan', 'success')
    } else {
      Swal.fire('Error', data.detail || 'Gagal menyimpan camera', 'error')
    }
  } catch (err) {
    Swal.fire('Error', 'Gagal menghubungi server', 'error')
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
  cameraId.value = camera.id
  isEditing.value = true
}

const deleteCamera = async (id) => {
  if (!confirm('Yakin menghapus camera ini?')) return
  try {
    await fetch(CCTV_API + 'cameras/' + id + '/', { method: 'DELETE' })
    loadCameras()
    Swal.fire('Dihapus', 'Camera berhasil dihapus dari daftar', 'success')
  } catch (err) {
    Swal.fire('Error', 'Gagal menghapus camera', 'error')
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
            <th>Sumber</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(cam, i) in cameras" :key="cam.id">
            <td class="text-gray-500">{{ i + 1 }}</td>
            <td class="font-medium">{{ cam.name }}</td>
            <td><span class="capitalize">{{ cam.source }}</span></td>
            <td>
              <span :class="['px-2', 'py-1', 'rounded', cam.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
                {{ cam.status }}
              </span>
            </td>
            <td class="text-right">
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