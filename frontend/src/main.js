import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createNotivue } from 'notivue'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const notivue = createNotivue({
  position: 'top-right',
  limit: 5,
  enqueue: true,
  notifications: {
    global: {
      duration: 3000,
    },
  },
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(notivue)
app.mount('#app')
