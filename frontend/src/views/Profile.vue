<script setup>
import { ref, onMounted, watch } from 'vue'
import Swal from 'sweetalert2'
import { useSidebarStore } from '../stores/sidebar'
import { useRouter } from 'vue-router'

const router = useRouter()
const store = useSidebarStore()

const user = ref({
  name: '',
  email: '',
  avatar: null,
  photo_count: 0,
  joined_date: ''
})

const loading = ref(false)
const changePasswordLoading = ref(false)

const fetchUser = async () => {
  loading.value = true
  try {
    const response = await fetch(import.meta.env.VITE_API_URL || '/api/auth/profile/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('authToken') || ''}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      user.value = {
        name: data.name || '',
        email: data.email || '',
        avatar: data.avatar,
        photo_count: data.photo_count || 0,
        joined_date: data.joined_date ? new Date(data.joined_date).toLocaleDateString('id-ID') : ''
      }
    } else {
       Swal.fire('error', 'Error', 'Gagal memuat profil')
    }
  } catch (error) {
     Swal.fire('error', 'Error', 'Gagal menghubungi server')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  if (confirm('Yakin ingin logout?')) {
    try {
      await fetch(import.meta.env.VITE_API_URL || '/api/auth/logout/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('authToken') || ''}`
        }
      })
      localStorage.removeItem('access_token')
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('expires_at')
      localStorage.removeItem('refresh_expires_at')
      localStorage.removeItem('token_response')
      router.push('/login')
       Swal.fire('success', 'Berhasil', 'Anda telah logout')
    } catch (error) {
       Swal.fire('error', 'Error', 'Gagal logout')
      router.push('/login')
    }
  }
}
</script>

<template>
<div class="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100 py-8">
  <div class="max-w-2xl mx-auto">
    
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Profil Saya</h1>
          <p class="text-gray-600">Kelola akun dan pengaturan pribadi</p>
        </div>
        <a href="/login" class="text-sm text-primary-600 hover:text-primary-500 transition-colors">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 01-2-2H3a2 2 0 01-2-2m10 7l-5 5m5-5H9m6 4h7a2 2 0 002-2v-4.998a2 2 0 00-2-2H5a2 2 0 00-2 2v4.998a2 2 0 002 2h6a2 2 0 002-2V5a2 2 0 00-2-2H8m0 5a2 2 0 012-2h2a2 2 0 012 2v1a2 2 0 01-2 2h-2v-2zm0 8a2 2 0 012-2h2a2 2 0 012 2v1a2 2 0 01-2 2h-2v-2z"/></svg>
          Logout
        </a>
      </div>
    </div>

    <!-- Profile Card -->
    <div class="card bg-white rounded-2xl shadow-lg p-6 md:p-8">
      <div class="text-center mb-8">
        <!-- Avatar -->
        <div class="w-32 h-32 mx-auto rounded-full overflow-hidden bg-gray-200 mb-4">
          <img v-if="user.avatar" :src="user.avatar" alt="User avatar" class="w-full h-full object-cover">
          <img v-else class="w-full h-full object-cover" src="/vite.svg" alt="Default avatar">
        </div>
        
        <h2 class="text-2xl font-semibold text-gray-900">{{ user.name || 'Nama Tidak Terisi' }}</h2>
        <p class="text-gray-500">Member sejak {{ user.joined_date }}</p>
        
        <p class="text-gray-400 mt-1">{{ user.photo_count }} foto diunggah</p>
      </div>

      <!-- Profile Stats -->
      <div class="grid grid-cols-2 gap-4 mb-8">
        <div>
          <div class="text-2xl font-bold text-primary-600">{{ user.photo_count }}</div>
          <div class="text-sm text-gray-500">Foto</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-primary-600">1.234</div>
          <div class="text-sm text-gray-500">Violations</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-8 pt-8 border-t border-gray-100">
        <div class="grid grid-cols-2 gap-4">
          <button @click="router.push('/settings')" class="px-6 py-3 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-500 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v16m8-8H4m10 7l-5 5m5-5H9m6 4h7a2 2 0 002-2v-4.998a2 2 0 00-2-2H5a2 2 0 00-2 2v4.998a2 2 0 002 2h6a2 2 0 002-2V5a2 2 0 00-2-2H8m0 5a2 2 0 012-2h2a2 2 0 012 2v1a2 2 0 01-2 2h-2v-2z"/></svg>
            Setelan
          </button>
          <button @click="router.push('/people')" class="px-6 py-3 rounded-lg bg-gray-100 text-gray-700 font-medium hover:bg-gray-50 transition-colors">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            Orang
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Stats or Recent Activity -->
    <div class="mt-8 pt-8 border-t border-gray-100">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Aktivitas Terbaru</h2>
      <div class="space-y-3">
        <div class="flex items-center px-3 py-2 rounded-lg bg-gray-50">
          <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9 2v-1M12 5l9-2-9-2v1M5 11h13a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v2zm8-4h.01M15 10a3 3 0 013 3v1.95a3 3 0 01-3 3H6a3 3 0 01-3-3V7z"/></svg>
            <span class="ml-2 text-gray-500">12 violation terdeteksi</span>
          </div>
        </div>
        <div class="flex items-center px-3 py-2 rounded-lg bg-gray-50">
          <div class="w-8 h-8 rounded-full bg-success-100 flex items-center justify-center">
            <svg class="w-4 h-4 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9 2v-1M12 5l9-2-9-2v1M5 11h13a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v2zm8-4h.01M15 10a3 3 0 013 3v1.95a3 3 0 01-3 3H6a3 3 0 01-3-3V7z"/></svg>
            <span class="ml-2 text-gray-500">Diversi 123 minggu ini</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
</template>