import { ref, onUnmounted } from 'vue'

const WS_BASE = import.meta.env.VITE_WS_URL
  || import.meta.env.VITE_BACKEND_URL
  || window.location.origin

function toWsUrl(base = WS_BASE) {
  let url
  try {
    url = new URL(base)
  } catch {
    url = new URL(window.location.origin)
  }
  url.protocol = url.protocol === 'https:' ? 'wss' : 'ws'
  return url.toString().replace(/\/$/, '')
}

export const detectionSocket = {
  socket: null,
  connected: ref(false),
  notifications: ref([]),

  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return
    }

    const token = localStorage.getItem('authToken')
    if (!token) {
      return
    }

    const wsBase = toWsUrl()
    const url = new URL('/ws/detections/', wsBase)
    url.searchParams.set('token', token)

    this.socket = new WebSocket(url.toString())

    this.socket.addEventListener('open', () => {
      this.connected.value = true
    })

    this.socket.addEventListener('message', (event) => {
      let payload
      try {
        payload = JSON.parse(event.data)
      } catch {
        return
      }
      this.notifications.value.unshift(payload)
    })

    this.socket.addEventListener('close', () => {
      this.connected.value = false
    })

    this.socket.addEventListener('error', () => {
      this.connected.value = false
    })
  },

  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.connected.value = false
  },

  clear() {
    this.notifications.value = []
  },
}

onUnmounted(() => {
  detectionSocket.disconnect()
})
