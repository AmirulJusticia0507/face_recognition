<script setup>
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'
import { authApi, violationLogsApi, dashboardApi } from '../services/api'

const router = useRouter()

const user = ref({
  name: '',
  username: '',
  email: '',
  avatar: null,
  photo_count: 0,
  joined_date: ''
})

const stats = ref({
  violations: 0,
  comparisons: 0,
})

const recentActivity = ref([])
const loading = ref(true)

const fetchProfile = async () => {
  loading.value = true
  try {
    const [profileRes, statsRes, activityRes] = await Promise.all([
      authApi.getProfile(),
      violationLogsApi.getStats(),
      dashboardApi.getRecentActivity({ limit: 5 }),
    ])

    const d = profileRes.data
    user.value = {
      name: d.name || d.username || '',
      username: d.username || '',
      email: d.email || '',
      avatar: d.avatar || null,
      photo_count: d.photo_count || 0,
      joined_date: d.date_joined
        ? new Date(d.date_joined).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
        : '-'
    }

    stats.value = {
      violations: statsRes.data?.total ?? 0,
      comparisons: statsRes.data?.comparisons ?? 0,
    }

    recentActivity.value = activityRes.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  const result = await Swal.fire({
    title: 'Yakin ingin logout?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Logout',
    cancelButtonText: 'Batal',
    confirmButtonColor: '#ef4444',
  })
  if (!result.isConfirmed) return
  try {
    await authApi.logout()
  } catch (e) {
    console.error(e)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('expires_at')
    localStorage.removeItem('refresh_expires_at')
    localStorage.removeItem('token_response')
    router.push('/login')
  }
}

const getActivityIcon = (type) => {
  const icons = {
    comparison: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    person: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    violation: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    camera: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z',
  }
  return icons[type] || icons.comparison
}

const getActivityColor = (type) => {
  const colors = {
    comparison: 'bg-blue-100 text-blue-600',
    person: 'bg-green-100 text-green-600',
    violation: 'bg-red-100 text-red-600',
    camera: 'bg-purple-100 text-purple-600',
  }
  return colors[type] || colors.comparison
}

onMounted(fetchProfile)
</script>

<template>
<div class="min-h-screen bg-gray-50 dark:bg-dark-950 py-8">
  <div class="max-w-2xl mx-auto px-4 space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Profil Saya</h1>
        <p class="text-gray-500 text-sm mt-0.5">Kelola akun dan pengaturan pribadi</p>
      </div>
      <button
        @click="handleLogout"
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-red-600 hover:bg-red-50 transition-colors text-sm font-medium"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Logout
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card card-body animate-pulse space-y-4">
      <div class="flex gap-4 items-center">
        <div class="w-20 h-20 rounded-full bg-gray-200"></div>
        <div class="flex-1 space-y-2">
          <div class="h-5 bg-gray-200 rounded w-1/3"></div>
          <div class="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    </div>

    <!-- Profile Card -->
    <div v-else class="card card-body">
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <!-- Avatar -->
        <div class="w-24 h-24 rounded-full overflow-hidden bg-primary-100 flex items-center justify-center flex-shrink-0 ring-4 ring-primary-50">
          <img v-if="user.avatar" :src="user.avatar" :alt="user.name" class="w-full h-full object-cover" />
          <svg v-else class="w-12 h-12 text-primary-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>

        <!-- Info -->
        <div class="flex-1 text-center sm:text-left">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ user.name || 'Nama tidak tersedia' }}</h2>
          <p class="text-gray-500 text-sm">@{{ user.username }}</p>
          <p class="text-gray-400 text-sm mt-1">{{ user.email || '-' }}</p>
          <p class="text-gray-400 text-xs mt-2">Member sejak {{ user.joined_date }}</p>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-gray-100">
        <div class="text-center p-4 rounded-xl bg-primary-50">
          <div class="text-2xl font-bold text-primary-600">{{ user.photo_count }}</div>
          <div class="text-xs text-gray-500 mt-1">Foto Terdaftar</div>
        </div>
        <div class="text-center p-4 rounded-xl bg-red-50">
          <div class="text-2xl font-bold text-red-500">{{ stats.violations }}</div>
          <div class="text-xs text-gray-500 mt-1">Total Violations</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="grid grid-cols-2 gap-3 mt-6">
        <button @click="router.push('/settings')" class="btn-primary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Setelan
        </button>
        <button @click="router.push('/people')" class="btn-secondary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Data Orang
        </button>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <div class="card-body border-b border-gray-100">
        <h2 class="font-semibold text-gray-900 dark:text-white">Aktivitas Terbaru</h2>
      </div>
      <div class="divide-y divide-gray-100">
        <div v-if="loading" class="p-4 text-center text-gray-400 text-sm">Memuat...</div>
        <div v-else-if="recentActivity.length === 0" class="p-8 text-center text-gray-400 text-sm">
          Belum ada aktivitas
        </div>
        <div
          v-else
          v-for="activity in recentActivity"
          :key="activity.id"
          class="px-4 py-3 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start gap-3">
            <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', getActivityColor(activity.type)]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getActivityIcon(activity.type)" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-700 dark:text-gray-300">{{ activity.description }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ activity.timestamp }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>
</template>
