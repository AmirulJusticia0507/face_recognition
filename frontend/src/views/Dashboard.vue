<script setup>
import { onMounted, ref } from 'vue'
import { dashboardApi } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  totalComparisons: 0,
  totalPeople: 0,
  totalViolations: 0,
  accuracyRate: 0,
})

const recentActivity = ref([])
const chartData = ref({ labels: [], datasets: [] })
const loading = ref(true)

const fetchDashboardData = async () => {
  try {
    loading.value = true
    const [statsRes, activityRes, chartRes] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getRecentActivity({ limit: 10 }),
      dashboardApi.getChartData({ days: 7 }),
    ])
    stats.value = statsRes.data
    recentActivity.value = activityRes.data
    chartData.value = chartRes.data
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const getActivityIcon = (type) => {
  const icons = {
    comparison: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    person: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    violation: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    camera: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z',
  }
  return icons[type] || icons.comparison
}

const getActivityColor = (type) => {
  const colors = {
    comparison: 'bg-blue-100 text-blue-600',
    person: 'bg-green-100 text-green-600',
    violation: 'bg-red-100 text-red-600',
    camera: 'bg-purple-100 text-purple-600',
  }
  return colors[type] || colors.comparison
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-500 mt-1">Overview of your face recognition system</p>
      </div>
      <div class="flex items-center gap-3">
        <button class="btn-secondary" @click="fetchDashboardData" :disabled="loading">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Total Comparisons</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ formatNumber(stats.totalComparisons) }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Registered People</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ formatNumber(stats.totalPeople) }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Violations Detected</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ formatNumber(stats.totalViolations) }}</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Accuracy Rate</p>
              <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.accuracyRate }}%</p>
            </div>
            <div class="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts & Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chart -->
      <div class="lg:col-span-2 card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Comparison Activity (Last 7 Days)</h2>
        </div>
        <div class="card-body">
          <div class="h-64" v-if="!loading">
            <canvas id="activityChart"></canvas>
          </div>
          <div class="h-64 flex items-center justify-center" v-else>
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">Recent Activity</h2>
          <router-link to="/history" class="text-sm text-primary-600 hover:text-primary-700">View All</router-link>
        </div>
        <div class="card-body p-0">
          <div class="divide-y divide-gray-100" v-if="!loading">
            <div 
              v-for="activity in recentActivity" 
              :key="activity.id" 
              class="px-4 py-3 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start gap-3">
                <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', getActivityColor(activity.type)]">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getActivityIcon(activity.type)" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900">{{ activity.description }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ activity.timestamp }}</p>
                </div>
              </div>
            </div>
            <div class="px-4 py-3 text-center" v-if="recentActivity.length === 0">
              <p class="text-gray-500">No recent activity</p>
            </div>
          </div>
          <div class="h-48 flex items-center justify-center" v-else>
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold text-gray-900">Quick Actions</h2>
      </div>
      <div class="card-body">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <router-link to="/face-comparison" class="group p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all">
            <div class="w-10 h-10 rounded-lg bg-blue-100 group-hover:bg-blue-600 group-hover:text-white transition-colors flex items-center justify-center mb-3">
              <svg class="w-5 h-5 text-blue-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="font-medium text-gray-900 group-hover:text-primary-600">Compare Faces</h3>
            <p class="text-sm text-gray-500 mt-1">Compare two faces</p>
          </router-link>

          <router-link to="/identify" class="group p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all">
            <div class="w-10 h-10 rounded-lg bg-green-100 group-hover:bg-green-600 group-hover:text-white transition-colors flex items-center justify-center mb-3">
              <svg class="w-5 h-5 text-green-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <h3 class="font-medium text-gray-900 group-hover:text-primary-600">Identify Person</h3>
            <p class="text-sm text-gray-500 mt-1">Find matching person</p>
          </router-link>

          <router-link to="/people/register" class="group p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all">
            <div class="w-10 h-10 rounded-lg bg-purple-100 group-hover:bg-purple-600 group-hover:text-white transition-colors flex items-center justify-center mb-3">
              <svg class="w-5 h-5 text-purple-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <h3 class="font-medium text-gray-900 group-hover:text-primary-600">Register Person</h3>
            <p class="text-sm text-gray-500 mt-1">Add new person</p>
          </router-link>

          <router-link to="/live-camera" class="group p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all">
            <div class="w-10 h-10 rounded-lg bg-orange-100 group-hover:bg-orange-600 group-hover:text-white transition-colors flex items-center justify-center mb-3">
              <svg class="w-5 h-5 text-orange-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              </svg>
            </div>
            <h3 class="font-medium text-gray-900 group-hover:text-primary-600">Live Camera</h3>
            <p class="text-sm text-gray-500 mt-1">Real-time detection</p>
          </router-link>

          <router-link to="/violation-logs" class="group p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all">
            <div class="w-10 h-10 rounded-lg bg-red-100 group-hover:bg-red-600 group-hover:text-white transition-colors flex items-center justify-center mb-3">
              <svg class="w-5 h-5 text-red-600 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="font-medium text-gray-900 group-hover:text-primary-600">Violation Logs</h3>
            <p class="text-sm text-gray-500 mt-1">View violations</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>