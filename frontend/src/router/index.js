import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: 'Dashboard', requiresAuth: true }
  },
  {
    path: '/face-comparison',
    name: 'FaceComparison',
    component: () => import('../views/FaceComparison.vue'),
    meta: { title: 'Face Comparison', requiresAuth: true }
  },
  {
    path: '/identify',
    name: 'Identify',
    component: () => import('../views/Identify.vue'),
    meta: { title: 'Identifikasi', requiresAuth: true }
  },
  {
    path: '/people',
    name: 'People',
    component: () => import('../views/People.vue'),
    meta: { title: 'Data Orang', requiresAuth: true }
  },
  {
    path: '/people/register',
    name: 'RegisterPerson',
    component: () => import('../views/RegisterPerson.vue'),
    meta: { title: 'Registrasi Orang', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { title: 'History', requiresAuth: true }
  },
  {
    path: '/model-settings',
    name: 'ModelSettings',
    component: () => import('../views/ModelSettings.vue'),
    meta: { title: 'Model Settings', requiresAuth: true }
  },
  {
    path: '/live-camera',
    name: 'LiveCamera',
    component: () => import('../views/LiveCamera.vue'),
    meta: { title: 'Live Camera', requiresAuth: true }
  },
  {
    path: '/pose-estimation',
    name: 'PoseEstimation',
    component: () => import('../views/PoseEstimation.vue'),
    meta: { title: 'Pose Estimation', requiresAuth: true }
  },
  {
    path: '/etle-camera',
    name: 'EtleCamera',
    component: () => import('../views/EtleCamera.vue'),
    meta: { title: 'ETLE Camera', requiresAuth: true }
  },
  {
    path: '/violation-logs',
    name: 'ViolationLogs',
    component: () => import('../views/ViolationLogs.vue'),
    meta: { title: 'Violation Logs', requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { title: 'About', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: 'Login', requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: 'Register', requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '404 - Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} | FaceAI`
  
  // Check auth - use both access_token (SSO) and authToken (legacy)
  const isAuthenticated = localStorage.getItem('access_token') || localStorage.getItem('authToken')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
