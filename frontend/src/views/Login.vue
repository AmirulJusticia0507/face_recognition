<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '../services/api'
import { goGoogleLogin } from '../services/sso'
import { push } from 'notivue'

const router = useRouter()
const route = useRoute()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const googleLoading = ref(false)
const showPassword = ref(false)
const loginMode = ref('local') // 'local' or 'sso'

const login = async () => {
  if (!form.value.username || !form.value.password) return
  loading.value = true
  try {
    if (loginMode.value === 'sso') {
      const { submitSSOLogin } = await import('../services/sso')
      await submitSSOLogin(form.value.username, form.value.password)
    } else {
      const response = await authApi.login(form.value)
      localStorage.setItem('authToken', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      push.success({ title: 'Login Berhasil', message: `Selamat datang, ${response.data.user?.name || form.value.username}!` })
      router.push('/')
    }
  } catch (error) {
    const msg = error.response?.data?.error || error.message || 'Login failed'
    push.error({ title: 'Login Gagal', message: msg })
  } finally {
    loading.value = false
  }
}

const handleGoogleLogin = async () => {
  googleLoading.value = true
  try {
    await goGoogleLogin()
  } catch (error) {
    push.error({ title: 'Error', message: 'Gagal mengarahkan ke Google login.' })
    googleLoading.value = false
  }
}

onMounted(() => {
  // Check for logout success notification
  if (sessionStorage.getItem('logout_success') === 'true') {
    sessionStorage.removeItem('logout_success')
    push.success({ title: 'Logged Out', message: 'Anda telah berhasil logout.' })
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.734-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900">FaceAI</h1>
        <p class="text-gray-500 mt-1">Sign in to your account</p>
      </div>

      <div class="card">
        <div class="card-body space-y-6">

          <!-- Google Login Button -->
          <button
            @click="handleGoogleLogin"
            :disabled="googleLoading"
            class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="!googleLoading" class="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <svg v-else class="animate-spin h-5 w-5 text-gray-400" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span v-if="googleLoading">Redirecting to Google...</span>
            <span v-else>Continue with Google</span>
          </button>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-3 bg-white text-gray-500">or sign in with credentials</span>
            </div>
          </div>

          <!-- Login Mode Toggle -->
          <div class="flex rounded-lg bg-gray-100 p-1">
            <button
              @click="loginMode = 'local'"
              class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
              :class="loginMode === 'local' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            >
              Local Account
            </button>
            <button
              @click="loginMode = 'sso'"
              class="flex-1 py-2 text-sm font-medium rounded-md transition-all"
              :class="loginMode === 'sso' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            >
              SSO
            </button>
          </div>

          <!-- Login Form -->
          <form @submit.prevent="login" class="space-y-4">
            <div>
              <label class="label">Username or Email</label>
              <input type="text" v-model="form.username" class="input" placeholder="Enter username" required />
            </div>
            <div>
              <label class="label">Password</label>
              <div class="relative">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  v-model="form.password"
                  class="input pr-10"
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                </button>
              </div>
            </div>

            <button type="submit" :disabled="loading" class="btn-primary w-full">
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Signing in...
              </span>
              <span v-else>Sign In</span>
            </button>
          </form>

          <!-- Links -->
          <div class="flex items-center justify-between text-sm pt-2 border-t border-gray-100">
            <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
              Create an account
            </router-link>
            <a href="#" class="text-gray-500 hover:text-gray-700">
              Forgot password?
            </a>
          </div>
        </div>
      </div>

      <p class="text-center text-xs text-gray-400 mt-6">&copy; 2024 FaceAI. All rights reserved.</p>
    </div>
  </div>
</template>
