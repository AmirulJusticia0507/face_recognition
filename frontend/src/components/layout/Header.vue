<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSidebarStore } from '../../stores/sidebar'
import { useAuthStore } from '../../stores/auth'
import { useDarkModeStore } from '../../stores/darkMode'
import { performLogout } from '../../services/sso'
import { dashboardApi } from '../../services/api'
import { useRouter } from 'vue-router'

const sidebarStore = useSidebarStore()
const authStore = useAuthStore()
const darkModeStore = useDarkModeStore()
const router = useRouter()

const userName = computed(() => authStore.userName || 'Admin User')
const userEmail = computed(() => authStore.userEmail || 'admin@faceai.com')
const userAvatar = computed(() => authStore.userAvatar)

// Notification state
const showNotifications = ref(false)
const notifications = ref([])
const notifLoading = ref(false)
const notifRead = ref(false)

const unreadCount = computed(() => notifRead.value ? 0 : notifications.value.length)

const fetchNotifications = async () => {
  notifLoading.value = true
  try {
    const res = await dashboardApi.getRecentActivity({ limit: 5 })
    notifications.value = res.data || []
  } catch {
    notifications.value = []
  } finally {
    notifLoading.value = false
  }
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    notifRead.value = true
    if (notifications.value.length === 0) fetchNotifications()
  }
}

const getNotifIcon = (type) => ({
  comparison: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  person: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
  violation: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  camera: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z',
}[type] || 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9')

const getNotifColor = (type) => ({
  comparison: 'bg-blue-100 text-blue-600',
  person: 'bg-green-100 text-green-600',
  violation: 'bg-red-100 text-red-600',
  camera: 'bg-purple-100 text-purple-600',
}[type] || 'bg-gray-100 text-gray-600')

// Close dropdown on outside click
const handleOutsideClick = (e) => {
  if (!e.target.closest('#notif-dropdown') && !e.target.closest('#notif-btn')) {
    showNotifications.value = false
  }
  if (!e.target.closest('#user-menu')) {
    userMenuEl.value?.classList.add('hidden')
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  fetchNotifications()
})
onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const userMenuEl = ref(null)

const menuItems = [
  { label: 'Profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', action: () => router.push('/profile') },
  { label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z', action: () => router.push('/settings') },
  { divider: true },
  { label: 'Logout', icon: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1', action: () => performLogout(), class: 'text-red-600' }
]
</script>

<template>
  <header class="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm dark:bg-dark-900 dark:border-dark-700">
    <div class="flex items-center justify-between h-16 px-4 lg:px-6">
      <!-- Left: Mobile menu toggle -->
      <div class="flex items-center gap-4">
        <button
          @click="sidebarStore.toggleMobile"
          class="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors dark:text-dark-400 dark:hover:bg-dark-700"
          aria-label="Toggle menu"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      <!-- Right: Actions -->
      <div class="flex items-center gap-2">

        <!-- Dark Mode Toggle -->
        <button
          @click="darkModeStore.toggle"
          class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors dark:text-dark-400 dark:hover:bg-dark-700"
          :aria-label="darkModeStore.isDark ? 'Light mode' : 'Dark mode'"
        >
          <svg v-if="darkModeStore.isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>

        <!-- Notifications -->
        <div class="relative">
          <button
            id="notif-btn"
            @click.stop="toggleNotifications"
            class="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors dark:text-dark-400 dark:hover:bg-dark-700"
            aria-label="Notifikasi"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <!-- Badge unread -->
            <span
              v-if="unreadCount > 0"
              class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"
            ></span>
          </button>

          <!-- Notification Dropdown -->
          <div
            v-if="showNotifications"
            id="notif-dropdown"
            class="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-100 z-50 dark:bg-dark-800 dark:border-dark-600 overflow-hidden"
          >
            <!-- Header -->
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-dark-700">
              <h3 class="font-semibold text-gray-900 dark:text-white text-sm">Notifikasi</h3>
              <span v-if="notifications.length" class="text-xs text-gray-400">{{ notifications.length }} aktivitas</span>
            </div>

            <!-- List -->
            <div class="max-h-72 overflow-y-auto divide-y divide-gray-50 dark:divide-dark-700">
              <div v-if="notifLoading" class="p-4 text-center text-gray-400 text-sm">
                <svg class="animate-spin h-5 w-5 mx-auto" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                </svg>
              </div>
              <div v-else-if="notifications.length === 0" class="p-6 text-center text-gray-400 text-sm">
                Tidak ada aktivitas terbaru
              </div>
              <div
                v-else
                v-for="notif in notifications"
                :key="notif.id"
                class="flex items-start gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors cursor-default"
              >
                <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5', getNotifColor(notif.type)]">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getNotifIcon(notif.type)" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-gray-700 dark:text-gray-300 leading-snug">{{ notif.description }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ notif.timestamp }}</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-4 py-2 border-t border-gray-100 dark:border-dark-700">
              <button
                @click="router.push('/history'); showNotifications = false"
                class="text-xs text-primary-600 hover:text-primary-700 font-medium w-full text-center py-1"
              >
                Lihat semua history →
              </button>
            </div>
          </div>
        </div>

        <!-- User Menu -->
        <div class="relative" id="user-menu">
          <button
            @click.stop="userMenuEl?.classList.toggle('hidden')"
            class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors dark:hover:bg-dark-700"
            aria-label="User menu"
          >
            <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden">
              <img v-if="userAvatar" :src="userAvatar" :alt="userName" class="w-full h-full object-cover" />
              <svg v-else class="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-medium text-gray-900 dark:text-dark-100">{{ userName }}</p>
              <p class="text-xs text-gray-500 dark:text-dark-400">{{ userEmail }}</p>
            </div>
            <svg class="w-4 h-4 text-gray-500 hidden md:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <div
            ref="userMenuEl"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 hidden z-50 dark:bg-dark-800 dark:border-dark-600"
          >
            <template v-for="(item, index) in menuItems" :key="index">
              <hr v-if="item.divider" class="my-1 border-gray-100 dark:border-dark-700" />
              <button
                v-else
                @click="item.action(); userMenuEl?.classList.add('hidden')"
                :class="['flex items-center gap-3 w-full px-4 py-2 text-sm transition-colors', item.class || 'text-gray-700 hover:bg-gray-50 dark:text-dark-200 dark:hover:bg-dark-700']"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
                </svg>
                {{ item.label }}
              </button>
            </template>
          </div>
        </div>

      </div>
    </div>
  </header>
</template>