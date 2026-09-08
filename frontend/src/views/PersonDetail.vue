<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { personApi } from '../services/api'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()

const person = ref(null)
const photos = ref([])
const loading = ref(true)
const photosLoading = ref(true)
const uploadLoading = ref(false)
const newPhotos = ref([])
const newPreviews = ref([])
const dragActive = ref(false)
const fileInput = ref(null)

const fetchPerson = async () => {
  loading.value = true
  try {
    const res = await personApi.get(route.params.id)
    person.value = res.data
  } catch {
    Swal.fire('Error', 'Gagal memuat data orang.', 'error')
    router.push('/people')
  } finally {
    loading.value = false
  }
}

const fetchPhotos = async () => {
  photosLoading.value = true
  try {
    const res = await personApi.getPhotos(route.params.id)
    photos.value = res.data
  } catch {
    photos.value = []
  } finally {
    photosLoading.value = false
  }
}

const handleFileDrop = (e) => {
  dragActive.value = false
  const files = Array.from(e.dataTransfer?.files || e.target.files || []).filter(f =>
    f.type.startsWith('image/')
  )
  addFiles(files)
}

const addFiles = (files) => {
  files.forEach(file => {
    newPhotos.value.push(file)
    const reader = new FileReader()
    reader.onload = (e) => newPreviews.value.push(e.target.result)
    reader.readAsDataURL(file)
  })
}

const removeNewPhoto = (index) => {
  newPhotos.value.splice(index, 1)
  newPreviews.value.splice(index, 1)
}

const uploadPhotos = async () => {
  if (!newPhotos.value.length) return
  uploadLoading.value = true
  try {
    const formData = new FormData()
    newPhotos.value.forEach(f => formData.append('photos', f))
    const res = await personApi.uploadPhotos(route.params.id, formData)
    Swal.fire('Berhasil', res.data.message || 'Foto berhasil diunggah.', 'success')
    newPhotos.value = []
    newPreviews.value = []
    fetchPhotos()
    fetchPerson()
  } catch (err) {
    Swal.fire('Error', err.response?.data?.error || 'Gagal mengunggah foto.', 'error')
  } finally {
    uploadLoading.value = false
  }
}

const deletePhoto = async (photoId) => {
  const result = await Swal.fire({
    title: 'Hapus foto?',
    text: 'Foto ini akan dihapus permanen.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#ef4444',
  })
  if (!result.isConfirmed) return
  try {
    await personApi.deletePhoto(route.params.id, photoId)
    Swal.fire('Dihapus', 'Foto berhasil dihapus.', 'success')
    fetchPhotos()
    fetchPerson()
  } catch {
    Swal.fire('Error', 'Gagal menghapus foto.', 'error')
  }
}

const confirmDeletePerson = async () => {
  const result = await Swal.fire({
    title: 'Hapus orang ini?',
    text: `${person.value.name} dan semua fotonya akan dihapus permanen.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Hapus',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#ef4444',
  })
  if (!result.isConfirmed) return
  try {
    await personApi.delete(route.params.id)
    Swal.fire('Dihapus', 'Data berhasil dihapus.', 'success')
    router.push('/people')
  } catch {
    Swal.fire('Error', 'Gagal menghapus data.', 'error')
  }
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('id-ID', {
  day: 'numeric', month: 'long', year: 'numeric'
}) : '-'

onMounted(() => {
  fetchPerson()
  fetchPhotos()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Back + Header -->
    <div class="flex items-center gap-4">
      <button @click="router.push('/people')" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors" aria-label="Kembali">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="flex-1">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Detail Orang</h1>
        <p class="text-gray-500 text-sm mt-0.5">Informasi lengkap dan foto terdaftar</p>
      </div>
      <div v-if="person" class="flex gap-2">
        <router-link :to="`/people/register?edit=${person.id}`" class="btn-secondary text-sm">
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Edit
        </router-link>
        <button @click="confirmDeletePerson" class="btn-danger text-sm">
          <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Hapus
        </button>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card card-body animate-pulse space-y-4">
      <div class="flex gap-4">
        <div class="w-20 h-20 rounded-full bg-gray-200"></div>
        <div class="flex-1 space-y-3 pt-2">
          <div class="h-5 bg-gray-200 rounded w-1/3"></div>
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    </div>

    <!-- Person Info Card -->
    <div v-else-if="person" class="card card-body">
      <div class="flex flex-col sm:flex-row gap-6">
        <!-- Avatar -->
        <div class="flex-shrink-0">
          <div class="w-24 h-24 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden ring-4 ring-primary-50">
            <img v-if="person.avatar" :src="person.avatar" :alt="person.name" class="w-full h-full object-cover" />
            <svg v-else class="w-12 h-12 text-primary-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>

        <!-- Info -->
        <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Nama</p>
            <p class="font-semibold text-gray-900 dark:text-white">{{ person.name }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Identifier</p>
            <p class="font-mono text-sm text-gray-700 dark:text-gray-300">{{ person.identifier }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Email</p>
            <p class="text-gray-700 dark:text-gray-300">{{ person.email || '-' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Telepon</p>
            <p class="text-gray-700 dark:text-gray-300">{{ person.phone || '-' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Alamat</p>
            <p class="text-gray-700 dark:text-gray-300">{{ person.address || '-' }}</p>
          </div>
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Terdaftar</p>
            <p class="text-gray-700 dark:text-gray-300">{{ formatDate(person.created_at) }}</p>
          </div>
          <div v-if="person.notes" class="sm:col-span-2">
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-0.5">Catatan</p>
            <p class="text-gray-700 dark:text-gray-300">{{ person.notes }}</p>
          </div>
        </div>

        <!-- Stats -->
        <div class="flex-shrink-0 flex flex-row sm:flex-col gap-4 sm:gap-3 items-center sm:items-end">
          <div class="text-center sm:text-right">
            <p class="text-2xl font-bold text-primary-600">{{ person.photo_count || 0 }}</p>
            <p class="text-xs text-gray-400">Foto</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Photo Gallery -->
    <div class="card">
      <div class="card-body border-b border-gray-100">
        <h2 class="font-semibold text-gray-900 dark:text-white">Foto Terdaftar</h2>
      </div>
      <div class="card-body">
        <div v-if="photosLoading" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div v-for="n in 4" :key="n" class="aspect-square bg-gray-100 rounded-xl animate-pulse"></div>
        </div>
        <div v-else-if="photos.length" class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          <div
            v-for="photo in photos"
            :key="photo.id"
            class="relative group aspect-square rounded-xl overflow-hidden bg-gray-100"
          >
            <img :src="photo.image" :alt="`Photo ${photo.id}`" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <button
                @click="deletePhoto(photo.id)"
                class="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                aria-label="Hapus foto"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
            <div class="absolute bottom-1 left-1 right-1 text-xs text-white/80 text-center truncate">
              {{ photo.uploaded_at ? new Date(photo.uploaded_at).toLocaleDateString('id-ID') : '' }}
            </div>
          </div>
        </div>
        <div v-else class="py-10 text-center text-gray-400">
          <svg class="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p class="text-sm">Belum ada foto terdaftar</p>
        </div>
      </div>
    </div>

    <!-- Upload New Photos -->
    <div class="card">
      <div class="card-body border-b border-gray-100">
        <h2 class="font-semibold text-gray-900 dark:text-white">Tambah Foto Baru</h2>
      </div>
      <div class="card-body space-y-4">
        <!-- Drop Zone -->
        <div
          @dragover.prevent="dragActive = true"
          @dragleave="dragActive = false"
          @drop.prevent="handleFileDrop"
          @click="fileInput?.click()"
          :class="['border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
            dragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50']"
        >
          <svg class="w-10 h-10 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="text-sm text-gray-500">Drag & drop foto ke sini, atau <span class="text-primary-600 font-medium">klik untuk pilih</span></p>
          <p class="text-xs text-gray-400 mt-1">JPG, PNG, WEBP hingga 10MB</p>
          <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleFileDrop" />
        </div>

        <!-- Previews -->
        <div v-if="newPreviews.length" class="grid grid-cols-3 sm:grid-cols-6 gap-3">
          <div
            v-for="(src, i) in newPreviews"
            :key="i"
            class="relative group aspect-square rounded-xl overflow-hidden bg-gray-100"
          >
            <img :src="src" class="w-full h-full object-cover" />
            <button
              @click="removeNewPhoto(i)"
              class="absolute top-1 right-1 w-5 h-5 bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs"
              aria-label="Hapus"
            >✕</button>
          </div>
        </div>

        <button
          v-if="newPhotos.length"
          @click="uploadPhotos"
          :disabled="uploadLoading"
          class="btn-primary w-full sm:w-auto"
        >
          <svg v-if="uploadLoading" class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
          </svg>
          {{ uploadLoading ? 'Mengunggah...' : `Upload ${newPhotos.length} Foto` }}
        </button>
      </div>
    </div>
  </div>
</template>
