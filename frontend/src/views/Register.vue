<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../services/api'

const router = useRouter()
const form = ref({ username: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const showPassword = ref(false)

const register = async () => {
  if (!form.value.username || !form.value.email || !form.value.password) return
  if (form.value.password !== form.value.confirmPassword) {
    alert('Passwords do not match')
    return
  }
  loading.value = true
  try {
    await authApi.register(form.value)
    alert('Registration successful! Please login.')
    router.push('/login')
  } catch (error) {
    alert(error.response?.data?.error || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.734-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">FaceAI</h1>
        <p class="text-gray-500 mt-1">Create your account</p>
      </div>

      <div class="card">
        <div class="card-body">
          <form @submit.prevent="register" class="space-y-4">
            <div>
              <label class="label">Username</label>
              <input type="text" v-model="form.username" class="input" placeholder="Enter username" required />
            </div>
            <div>
              <label class="label">Email</label>
              <input type="email" v-model="form.email" class="input" placeholder="Enter email" required />
            </div>
            <div>
              <label class="label">Password</label>
              <input :type="showPassword ? 'text' : 'password'" v-model="form.password" class="input" placeholder="Enter password" required />
            </div>
            <div>
              <label class="label">Confirm Password</label>
              <input :type="showPassword ? 'text' : 'password'" v-model="form.confirmPassword" class="input" placeholder="Confirm password" required />
            </div>
            <div class="flex items-center gap-2">
              <input type="checkbox" v-model="showPassword" id="showPassword" class="rounded" />
              <label for="showPassword" class="text-sm text-gray-600">Show passwords</label>
            </div>
            <button type="submit" :disabled="loading" class="btn-primary w-full">
              <span v-if="loading">Creating account...</span>
              <span v-else>Sign Up</span>
            </button>
          </form>

          <div class="mt-6 text-center">
            <p class="text-sm text-gray-500">
              Already have an account?
              <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">Sign In</router-link>
            </p>
          </div>
        </div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-6">&copy; 2024 FaceAI. All rights reserved.</p>
    </div>
  </div>
</template>