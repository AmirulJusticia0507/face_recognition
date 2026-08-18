<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSidebarStore } from '../../stores/sidebar'

const router = useRouter()
const route = useRoute()
const sidebarStore = useSidebarStore()

const isCollapsed = computed(() => sidebarStore.isCollapsed)
const isMobileOpen = computed(() => sidebarStore.isMobileOpen)

const navigation = [
  { name: 'Dashboard', path: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Face Comparison', path: '/face-comparison', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { name: 'Identifikasi', path: '/identify', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
  { name: 'Data Orang', path: '/people', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
  { name: 'History', path: '/history', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  { name: 'Model Settings', path: '/model-settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
  { name: 'Live Camera', path: '/live-camera', icon: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M9 19a5 5 0 005 5h.01a5 5 0 005-5H9z' },
  { name: 'Pose Estimation', path: '/pose-estimation', icon: 'M17 14v6m-3-3h6M6 10h2a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2zm10 0h2a2 2 0 002-2V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v2a2 2 0 002 2zM6 20h2a2 2 0 002-2v-2a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2z' },
  { name: 'ETLE Camera', path: '/etle-camera', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
  { name: 'Violation Logs', path: '/violation-logs', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
  { name: 'Forensic Analysis', path: '/forensic-analysis', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7' },
  { name: 'About', path: '/about', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
]

const navigate = (path) => {
  router.push(path)
  sidebarStore.closeMobile()
}
</script>

<template>
  <aside
    :class="[
      'fixed top-0 left-0 z-50 h-screen flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ease-in-out dark:bg-dark-900 dark:border-dark-700',
      isCollapsed ? 'w-20' : 'w-64',
      isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
    ]"
  >
    <!-- Logo + Toggle -->
    <div class="flex items-center h-16 px-4 border-b border-gray-200 dark:border-dark-700 shrink-0">
      <!-- Logo icon (always visible) -->
      <div class="w-10 h-10 rounded-lg bg-primary-600 flex items-center justify-center shrink-0">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.734-.988-2.386l-.548-.547z" />
        </svg>
      </div>

      <!-- Brand name (hidden when collapsed) -->
      <span v-show="!isCollapsed" class="ml-3 font-bold text-xl text-gray-900 dark:text-dark-100 whitespace-nowrap">FaceAI</span>

      <!-- Toggle button -->
      <button
        @click="sidebarStore.toggleCollapsed"
        class="ml-auto p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors dark:text-dark-400 dark:hover:bg-dark-700 dark:hover:text-dark-200 shrink-0"
        :aria-label="isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <!-- Collapse arrow (shown when expanded) -->
        <svg v-if="!isCollapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
        <!-- Expand arrow (shown when collapsed) -->
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-4 px-2" aria-label="Main navigation">
      <ul class="space-y-1" role="list">
        <li v-for="item in navigation" :key="item.path" class="relative group">
          <button
            @click="navigate(item.path)"
            :class="[
              'sidebar-link w-full',
              !isCollapsed ? '' : 'justify-center px-0',
              route.path === item.path ? 'active' : ''
            ]"
            :aria-current="route.path === item.path ? 'page' : undefined"
          >
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
            </svg>
            <span v-show="!isCollapsed" class="truncate">{{ item.name }}</span>
          </button>

          <!-- Tooltip when collapsed -->
          <div
            v-show="isCollapsed"
            class="absolute left-full top-1/2 -translate-y-1/2 ml-3 px-3 py-1.5 bg-gray-800 text-white text-sm rounded-lg shadow-lg whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 pointer-events-none z-50 dark:bg-dark-700"
          >
            {{ item.name }}
          </div>
        </li>
      </ul>
    </nav>

    <!-- Footer -->
    <div class="p-4 border-t border-gray-200 dark:border-dark-700 shrink-0" v-show="!isCollapsed">
      <div class="text-xs text-gray-500 dark:text-dark-400 text-center">
        <p>FaceAI v1.0.0</p>
        <p class="mt-1">Face Recognition System</p>
      </div>
    </div>
  </aside>
</template>