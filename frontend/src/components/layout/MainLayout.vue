<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSidebarStore } from '../../stores/sidebar'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import Footer from './Footer.vue'

const router = useRouter()
const route = useRoute()
const sidebarStore = useSidebarStore()

const isAuthPage = computed(() => {
  return ['/login', '/register'].includes(route.path)
})

const mainClasses = computed(() => {
  const base = 'min-h-screen bg-gray-50 transition-all duration-300'
  const sidebarWidth = sidebarStore.isCollapsed ? 'lg:ml-20' : 'lg:ml-64'
  return `${base} ${sidebarWidth}`
})
</script>

<template>
  <div :class="mainClasses" @click="sidebarStore.closeMobile">
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