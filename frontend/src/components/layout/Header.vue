<script setup>
import { computed } from 'vue'
import { useSidebarStore } from '../../stores/sidebar'
import { useAuthStore } from '../../stores/auth'
import { performLogout } from '../../services/sso'
import { useRouter } from 'vue-router'

const sidebarStore = useSidebarStore()
const authStore = useAuthStore()
const router = useRouter()

const userName = computed(() => authStore.userName || 'Admin User')
const userEmail = computed(() => authStore.userEmail || 'admin@faceai.com')
const userAvatar = computed(() => authStore.userAvatar)

const menuItems = [
  { label: 'Profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', action: () => router.push('/profile') },
  { label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z', action: () => router.push('/settings') },
  { divider: true },
  { label: 'Logout', icon: 'M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1', action: handleLogout, class: 'text-red-600' }
]

function handleLogout() {
  performLogout()
}
</script>

<template>
  <header class="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm">
    <div class="flex items-center justify-between h-16 px-4 lg:px-6">
      <!-- Left Side - Mobile Menu Button -->
      <div class="flex items-center gap-4">
        <button
          @click="sidebarStore.toggleMobile"
          class="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
          aria-label="Toggle menu"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <!-- Breadcrumb / Page Title -->
        <div class="hidden lg:block">
          <slot name="header-title">
            <h1 class="text-lg font-semibold text-gray-900">Dashboard</h1>
          </slot>
        </div>
      </div>

      <!-- Right Side - User Menu & Notifications -->
      <div class="flex items-center gap-3">
        <!-- Notifications -->
        <button class="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors" aria-label="Notifications">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <!-- User Menu -->
        <div class="relative" id="user-menu">
          <button
            @click="$refs.userMenu?.classList.toggle('hidden')"
            class="flex items-center gap-3 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="User menu"
            aria-expanded="false"
            aria-haspopup="true"
          >
            <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center overflow-hidden">
              <img v-if="userAvatar" :src="userAvatar" :alt="userName" class="w-full h-full object-cover" />
              <svg v-else class="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
              <p class="text-xs text-gray-500">{{ userEmail }}</p>
            </div>
            <svg class="w-4 h-4 text-gray-500 hidden md:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <div
            ref="userMenu"
            class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 hidden z-50"
            role="menu"
            aria-orientation="vertical"
          >
            <template v-for="(item, index) in menuItems" :key="index">
              <hr v-if="item.divider" class="my-1 border-gray-100" />
              <button
                v-else
                @click="item.action"
                :class="['flex items-center gap-3 w-full px-4 py-2 text-sm transition-colors', item.class || 'text-gray-700 hover:bg-gray-50']"
                role="menuitem"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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