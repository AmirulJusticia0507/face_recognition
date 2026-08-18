<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Notivue, push } from 'notivue'
import { useSidebarStore } from './stores/sidebar'
import { useAuthStore } from './stores/auth'
import { handleGoogleCallback } from './services/sso'
import MainLayout from './components/layout/MainLayout.vue'

const route = useRoute()
const sidebarStore = useSidebarStore()
const authStore = useAuthStore()

onMounted(async () => {
  sidebarStore.initFromLocalStorage()
  authStore.loadUserFromStorage()

  // Handle Google OAuth callback
  const code = route.query.code
  if (code && route.name === 'Login') {
    try {
      await handleGoogleCallback(code)
    } catch (err) {
      console.error('Google callback error:', err)
      push.error({ title: 'Error', message: 'Gagal memproses login Google.' })
    }
  }
})
</script>

<template>
  <Notivue />
  <MainLayout />
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
</style>
