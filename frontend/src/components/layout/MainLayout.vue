<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useSidebarStore } from '../../stores/sidebar'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import Footer from './Footer.vue'

const route = useRoute()
const sidebarStore = useSidebarStore()

const isAuthPage = computed(() =>
  ['login', 'register'].includes(route.name?.toLowerCase() || '')
)

const mainClasses = computed(() => {
  const base = 'min-h-screen bg-gray-50 dark:bg-dark-950 transition-all duration-300'
  const sidebarWidth = sidebarStore.isCollapsed ? 'lg:ml-20' : 'lg:ml-64'
  return `${base} ${sidebarWidth}`
})
</script>

<template>
  <!-- Auth pages: tampil tanpa Sidebar/Header -->
  <div v-if="isAuthPage" class="min-h-screen bg-gray-50 dark:bg-dark-950">
    <router-view />
  </div>

  <!-- App pages: pakai full layout -->
  <div v-else :class="mainClasses">
    <!-- Sidebar Overlay for Mobile -->
    <div
      v-if="sidebarStore.isMobileOpen"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
      @click="sidebarStore.closeMobile"
    />

    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content Wrapper -->
    <div class="flex flex-col min-h-screen">
      <!-- Header -->
      <Header />

      <!-- Main Content -->
      <main class="flex-1 p-4 lg:p-6 lg:pl-8">
        <router-view />
      </main>

      <!-- Footer -->
      <Footer />
    </div>
  </div>
</template>