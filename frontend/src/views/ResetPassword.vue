<script setup>
import { push } from 'notivue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '../services/api'

const route = useRoute()
const router = useRouter()
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const resetPassword = async () => {
  loading.value = true
  try {
    await authApi.resetPassword({
      uid: route.params.uid,
      token: route.params.token,
      password: password.value,
      confirm_password: confirmPassword.value,
    })
    push.success({ title: 'Berhasil', message: 'Password berhasil diubah.' })
    router.push('/login')
  } catch (error) {
    push.error({ title: 'Gagal', message: error.response?.data?.error || 'Link reset tidak valid atau sudah kedaluwarsa.' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Buat Password Baru</h1>
        <p class="text-gray-500 mt-1">Gunakan password yang kuat dan mudah kamu ingat.</p>
      </div>

      <div class="card">
        <div class="card-body">
          <form @submit.prevent="resetPassword" class="space-y-4">
            <div>
              <label class="label">Password Baru</label>
              <input v-model="password" type="password" class="input" minlength="8" required />
            </div>
            <div>
              <label class="label">Konfirmasi Password</label>
              <input v-model="confirmPassword" type="password" class="input" minlength="8" required />
            </div>
            <button type="submit" :disabled="loading" class="btn-primary w-full">
              {{ loading ? 'Menyimpan...' : 'Simpan Password Baru' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>