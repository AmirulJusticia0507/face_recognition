import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSidebarStore = defineStore('sidebar', () => {
  const isCollapsed = ref(false)
  const isMobileOpen = ref(false)

  const toggleCollapsed = () => {
    isCollapsed.value = !isCollapsed.value
    saveToLocalStorage()
  }

  const setCollapsed = (value) => {
    isCollapsed.value = value
    saveToLocalStorage()
  }

  const toggleMobile = () => {
    isMobileOpen.value = !isMobileOpen.value
  }

  const closeMobile = () => {
    isMobileOpen.value = false
  }

  const saveToLocalStorage = () => {
    localStorage.setItem('sidebarCollapsed', JSON.stringify(isCollapsed.value))
  }

  const initFromLocalStorage = () => {
    const saved = localStorage.getItem('sidebarCollapsed')
    if (saved !== null) {
      isCollapsed.value = JSON.parse(saved)
    }
  }

  return {
    isCollapsed,
    isMobileOpen,
    toggleCollapsed,
    setCollapsed,
    toggleMobile,
    closeMobile,
    initFromLocalStorage
  }
})