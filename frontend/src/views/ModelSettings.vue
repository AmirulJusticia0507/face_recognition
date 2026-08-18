<script setup>
import { ref, onMounted } from 'vue'
import { modelSettingsApi } from '../services/api'
import Swal from 'sweetalert2'

const models = ref([
  { name: 'ArcFace', description: 'High accuracy, recommended', status: 'active' },
  { name: 'Facenet', description: 'Good balance of speed/accuracy', status: 'available' },
  { name: 'VGG-Face', description: 'Deep face recognition', status: 'available' },
  { name: 'OpenFace', description: 'Lightweight and fast', status: 'available' },
  { name: 'DeepFace', description: 'Multi-model ensemble', status: 'available' },
  { name: 'DeepID', description: 'Compact model', status: 'available' },
  { name: 'Dlib', description: 'Traditional approach', status: 'available' },
])

const selectedModel = ref('ArcFace')
const loading = ref(false)
const testingModel = ref(false)
const testResult = ref(null)

const config = ref({
  similarity_threshold: 0.4,
  detection_backend: 'opencv',
  enforce_detection: true,
  align: true,
})

const detectionBackends = [
  { value: 'opencv', label: 'OpenCV', description: 'Fast, CPU-based' },
  { value: 'ssd', label: 'SSD', description: 'Single Shot Detector' },
  { value: 'mtcnn', label: 'MTCNN', description: 'Multi-task CNN' },
  { value: 'retinaface', label: 'RetinaFace', description: 'High accuracy' },
  { value: 'mediapipe', label: 'MediaPipe', description: 'Google, lightweight' },
]

const saveSettings = async () => {
  loading.value = true
  try {
    await modelSettingsApi.update({
      default_model: selectedModel.value,
      ...config.value,
    })
    Swal.fire('Success', 'Settings saved successfully', 'success')
  } catch (error) {
    Swal.fire('Error', 'Failed to save settings', 'error')
  } finally {
    loading.value = false
  }
}

const testModel = async () => {
  testingModel.value = true
  testResult.value = null
  try {
    const response = await modelSettingsApi.testModel({ model: selectedModel.value })
    testResult.value = response.data
    Swal.fire({
      title: 'Test Complete',
      html: `<p>Model: <strong>${selectedModel.value}</strong></p><p>Avg. time: <strong>${response.data.avg_time}ms</strong></p><p>Memory: <strong>${response.data.memory_usage}MB</strong></p>`,
      icon: 'success',
    })
  } catch (error) {
    Swal.fire('Error', 'Failed to test model', 'error')
  } finally {
    testingModel.value = false
  }
}

const selectModel = (modelName) => {
  selectedModel.value = modelName
}

onMounted(() => {
  modelSettingsApi.get().then(res => {
    if (res.data.default_model) selectedModel.value = res.data.default_model
    Object.assign(config.value, res.data)
  }).catch(() => {})
})
</script>

<template>
  <div class="space-y-6 max-w-4xl mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Model Settings</h1>
      <p class="text-gray-500 mt-1">Configure face recognition models and parameters</p>
    </div>

    <!-- Model Selection -->
    <div class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold text-gray-900">Default Recognition Model</h2>
      </div>
      <div class="card-body">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            v-for="model in models"
            :key="model.name"
            @click="selectModel(model.name)"
            class="p-4 rounded-lg border-2 text-left transition-all"
            :class="selectedModel === model.name ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'"
          >
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold text-gray-900">{{ model.name }}</h3>
              <div v-if="selectedModel === model.name" class="w-5 h-5 rounded-full bg-primary-600 flex items-center justify-center">
                <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>
            <p class="text-sm text-gray-500">{{ model.description }}</p>
          </button>
        </div>
      </div>
    </div>

    <!-- Configuration -->
    <div class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold text-gray-900">Detection Settings</h2>
      </div>
      <div class="card-body space-y-6">
        <!-- Threshold -->
        <div>
          <label class="label">Similarity Threshold: {{ config.similarity_threshold }}</label>
          <input
            type="range"
            v-model.number="config.similarity_threshold"
            min="0.1"
            max="1.0"
            step="0.05"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div class="flex justify-between text-xs text-gray-400 mt-1">
            <span>0.1 (Strict)</span>
            <span>1.0 (Loose)</span>
          </div>
          <p class="text-sm text-gray-500 mt-2">Higher values require more similarity for a match. Default: 0.4</p>
        </div>

        <!-- Detection Backend -->
        <div>
          <label class="label">Detection Backend</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <button
              v-for="backend in detectionBackends"
              :key="backend.value"
              @click="config.detection_backend = backend.value"
              class="p-3 rounded-lg border-2 text-left transition-all"
              :class="config.detection_backend === backend.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'"
            >
              <p class="font-medium text-gray-900">{{ backend.label }}</p>
              <p class="text-xs text-gray-500">{{ backend.description }}</p>
            </button>
          </div>
        </div>

        <!-- Toggles -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">Enforce Detection</p>
              <p class="text-sm text-gray-500">Require face detection</p>
            </div>
            <button
              @click="config.enforce_detection = !config.enforce_detection"
              class="relative w-12 h-7 rounded-full transition-colors"
              :class="config.enforce_detection ? 'bg-primary-600' : 'bg-gray-300'"
            >
              <span class="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="config.enforce_detection ? 'translate-x-5' : ''"></span>
            </button>
          </div>
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p class="font-medium text-gray-900">Face Alignment</p>
              <p class="text-sm text-gray-500">Align detected faces</p>
            </div>
            <button
              @click="config.align = !config.align"
              class="relative w-12 h-7 rounded-full transition-colors"
              :class="config.align ? 'bg-primary-600' : 'bg-gray-300'"
            >
              <span class="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="config.align ? 'translate-x-5' : ''"></span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end gap-3">
      <button @click="testModel" :disabled="testingModel" class="btn-secondary">
        <span v-if="testingModel" class="flex items-center gap-2">
          <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Testing...
        </span>
        <span v-else>Test Model</span>
      </button>
      <button @click="saveSettings" :disabled="loading" class="btn-primary">
        <span v-if="loading" class="flex items-center gap-2">
          <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Saving...
        </span>
        <span v-else>Save Settings</span>
      </button>
    </div>
  </div>
</template>