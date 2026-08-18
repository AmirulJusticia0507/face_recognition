<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="text-center">
      <div class="text-9xl font-bold text-primary-600 mb-4">404</div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h1>
      <p class="text-gray-500 mb-8 max-w-md mx-auto">
        The page you are looking for does not exist or has been moved.
      </p>
      <div class="flex items-center justify-center gap-3">
        <button @click="router.back()" class="btn-secondary">Go Back</button>
        <router-link to="/" class="btn-primary">Go Home</router-link>
      </div>
    </div>
  </div>
</template>