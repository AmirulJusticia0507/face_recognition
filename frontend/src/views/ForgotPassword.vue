<script setup>
import { push } from 'notivue'
import { ref } from 'vue'
import { authApi } from '../services/api'

const email = ref('')
const loading = ref(false)
const submitted = ref(false)
const resetLink = ref('')

const requestReset = async () => {
  loading.value = true
  try {
    const response = await authApi.forgotPassword(email.value.trim())
    submitted.value = true
    resetLink.value = response.data.reset_link || ''
  } catch (error) {
    push.error({ title: 'Gagal', message: error.response?.data?.error || 'Permintaan reset password gagal.' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Reset Password</h1>
        <p class="text-gray-500 mt-1">Masukkan email akunmu untuk menerima link reset.</p>
      </div>

      <div class="card">
        <div class="card-body">
          <div v-if="submitted" class="space-y-4">
            <p class="text-sm text-gray-600">Jika email terdaftar, instruksi reset password sudah dikirim.</p>
            <a v-if="resetLink" :href="resetLink" class="block text-sm text-primary-600 break-all hover:underline">Buka link reset password</a>
            <router-link to="/login" class="btn-primary w-full block text-center">Kembali ke Login</router-link>
          </div>
          <form v-else @submit.prevent="requestReset" class="space-y-4">
            <div>
              <label class="label">Email</label>
              <input v-model="email" type="email" class="input" placeholder="nama@email.com" required />
            </div>
            <button type="submit" :disabled="loading" class="btn-primary w-full">
              {{ loading ? 'Mengirim...' : 'Kirim Link Reset' }}
            </button>
          </form>
          <div class="mt-6 text-center text-sm">
            <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">Kembali ke Login</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>