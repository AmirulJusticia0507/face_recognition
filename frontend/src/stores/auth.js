import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const userName = computed(() => user.value?.name || user.value?.preferred_username || '')
  const userEmail = computed(() => user.value?.email || '')
  const userAvatar = computed(() => user.value?.picture || null)

  function setUser(userData) {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  function loadUserFromStorage() {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch {
        user.value = null
      }
    }
  }

  function setAccessToken(token) {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  async function logout() {
    user.value = null
    accessToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('expires_at')
    localStorage.removeItem('refresh_expires_at')
    localStorage.removeItem('token_response')
    localStorage.removeItem('user')
    localStorage.removeItem('authToken')
  }

  // Auto-load user on store init
  loadUserFromStorage()

  return {
    user,
    accessToken,
    isAuthenticated,
    userName,
    userEmail,
    userAvatar,
    setUser,
    loadUserFromStorage,
    setAccessToken,
    logout,
  }
})
