<script setup>
import { ref, computed } from 'vue'
import { push } from 'notivue'
import { forensicApi } from '../services/api'

const selectedFile = ref(null)
const previewUrl = ref(null)
const dragActive = ref(false)
const analyzing = ref(false)
const result = ref(null)
const method = ref('ela')
const history = ref([])
const showHistory = ref(false)

const methods = [
  { id: 'ela', name: 'ELA', desc: 'Error Level Analysis', available: true },
  { id: 'noise', name: 'Noise', desc: 'Analisis Derau', available: true },
  { id: 'sharpening', name: 'Sharpening', desc: 'Deteksi Ketajaman', available: true },
  { id: 'median_filter', name: 'Median', desc: 'Median Filter Det.', available: true },
  { id: 'copy_move', name: 'Copy-Move', desc: 'Deteksi Copy-Move', available: true },
  { id: 'jpeg_ghost', name: 'JPEG Ghost', desc: 'JPEG Ghost Det.', available: true },
  { id: 'metadata', name: 'Metadata', desc: 'Metadata Forensics', available: false },
]

const currentMethod = computed(() => methods.find(m => m.id === method.value))

const suspiciousPct = computed(() => {
  if (!result.value) return 0
  return result.value.suspicious_pct ?? result.value.inconsistency_pct ?? result.value.double_compress_pct ?? 0
})

const statValue1 = computed(() => {
  if (method.value === 'copy_move') return result.value?.total_matches ?? '-'
  if (method.value === 'jpeg_ghost') return result.value?.original_quality ?? '-'
  return result.value?.mean_error ?? result.value?.mean_noise ?? result.value?.mean_sharpness ?? result.value?.mean_residue ?? '-'
})

const statValue2 = computed(() => {
  if (method.value === 'copy_move') return result.value?.cluster_count ?? '-'
  if (method.value === 'jpeg_ghost') return result.value?.ghost_quality ?? '-'
  return result.value?.max_error ?? result.value?.max_noise ?? result.value?.max_sharpness ?? result.value?.max_residue ?? '-'
})

const statLabel1 = computed(() => {
  const labels = { ela: 'Mean Error', noise: 'Mean Noise', sharpening: 'Mean Sharpness', median_filter: 'Mean Residue', jpeg_ghost: 'Original Q', copy_move: 'Total Matches' }
  return labels[method.value] || 'Value 1'
})

const statLabel2 = computed(() => {
  const labels = { ela: 'Max Error', noise: 'Max Noise', sharpening: 'Max Sharpness', median_filter: 'Max Residue', jpeg_ghost: 'Ghost Q', copy_move: 'Clusters' }
  return labels[method.value] || 'Value 2'
})

const statLabel3 = computed(() => {
  const labels = { ela: 'Area Suspicious', noise: 'Inconsistency', sharpening: 'Area Suspicious', median_filter: 'Inconsistency', jpeg_ghost: 'Double Compress', copy_move: 'Forgery Coverage' }
  return labels[method.value] || 'Suspicious'
})

const maxQualityError = computed(() => {
  if (!result.value?.quality_scores) return 1
  return Math.max(...result.value.quality_scores.map(s => s[1]), 1)
})

function handleDrag(e) {
  e.preventDefault()
  dragActive.value = e.type === 'dragenter'
}

function handleDrop(e) {
  e.preventDefault()
  dragActive.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    selectFile(file)
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) selectFile(file)
}

function selectFile(file) {
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  result.value = null
}

function removeFile() {
  selectedFile.value = null
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = null
  result.value = null
}

async function analyze() {
  if (!selectedFile.value) return

  const selectedMethod = methods.find(m => m.id === method.value)
  if (!selectedMethod.available) {
    push.warning({ title: 'Metode belum tersedia', message: `${selectedMethod.name} akan diimplementasikan di tahap berikutnya.` })
    return
  }

  analyzing.value = true
  result.value = null

  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('method', method.value)

    const res = await forensicApi.analyze(formData)
    result.value = res.data
    push.success({ title: 'Analisis selesai', message: `${currentMethod.value.name} analysis berhasil.` })
  } catch (err) {
    push.error({ title: 'Gagal', message: err.response?.data?.error || 'Terjadi kesalahan saat analisis.' })
  } finally {
    analyzing.value = false
  }
}

async function loadHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value && history.value.length === 0) {
    try {
      const res = await forensicApi.getHistory()
      history.value = res.data
    } catch (err) {
      push.error({ title: 'Gagal memuat riwayat' })
    }
  }
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Forensic Analysis</h1>
      <p class="text-gray-500 mt-1">Analisis manipulasi gambar menggunakan berbagai metode forensik digital</p>
    </div>

    <!-- Method Selection -->
    <div class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold text-gray-900">Pilih Metode Analisis</h2>
      </div>
      <div class="card-body">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
          <button
            v-for="m in methods"
            :key="m.id"
            @click="method = m.id"
            :class="[
              'relative p-4 rounded-xl border-2 transition-all duration-200 text-left',
              method === m.id
                ? 'border-primary-500 bg-primary-50 ring-1 ring-primary-500'
                : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50',
              !m.available && 'opacity-50'
            ]"
          >
            <div class="font-semibold text-sm" :class="method === m.id ? 'text-primary-700' : 'text-gray-900'">{{ m.name }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ m.desc }}</div>
            <span
              v-if="!m.available"
              class="absolute top-2 right-2 text-[10px] bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full"
            >Soon</span>
            <span
              v-if="m.available"
              class="absolute top-2 right-2 w-2 h-2 rounded-full bg-green-400"
            ></span>
          </button>
        </div>
      </div>
    </div>

    <!-- Upload + Results Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Upload Area -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">Upload Gambar</h2>
          <button
            v-if="selectedFile"
            @click="removeFile"
            class="text-sm text-red-500 hover:text-red-700"
          >Hapus</button>
        </div>
        <div class="card-body">
          <div
            v-if="!previewUrl"
            @dragenter="handleDrag"
            @dragleave="handleDrag"
            @dragover="handleDrag"
            @drop="handleDrop"
            :class="[
              'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors',
              dragActive ? 'border-primary-400 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
            ]"
            @click="$refs.fileInput.click()"
          >
            <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p class="text-gray-600 font-medium">Seret & lepas gambar di sini</p>
            <p class="text-sm text-gray-400 mt-1">atau klik untuk memilih file</p>
            <p class="text-xs text-gray-400 mt-2">Mendukung JPG, PNG, WebP</p>
          </div>

          <div v-else class="space-y-4">
            <div class="relative rounded-xl overflow-hidden border border-gray-200">
              <img :src="previewUrl" class="w-full h-auto max-h-80 object-contain bg-gray-50" />
              <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-3">
                <p class="text-white text-sm font-medium truncate">{{ selectedFile.name }}</p>
                <p class="text-white/70 text-xs">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
              </div>
            </div>

            <button
              @click="analyze"
              :disabled="analyzing"
              class="btn-primary w-full flex items-center justify-center gap-2"
            >
              <svg v-if="analyzing" class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {{ analyzing ? 'Menganalisis...' : 'Analisis ' + currentMethod.name }}
            </button>
          </div>

          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleFileSelect"
          />
        </div>
      </div>

      <!-- Results Area -->
      <div class="card">
        <div class="card-header">
          <h2 class="text-lg font-semibold text-gray-900">Hasil Analisis</h2>
        </div>
        <div class="card-body">
          <div v-if="!result && !analyzing" class="text-center py-16 text-gray-400">
            <svg class="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Hasil analisis akan muncul di sini</p>
          </div>

          <div v-if="analyzing" class="text-center py-16">
            <div class="inline-flex items-center gap-3 text-primary-600">
              <svg class="animate-spin w-8 h-8" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <span class="text-lg font-medium">Sedang menganalisis...</span>
            </div>
            <p class="text-gray-400 text-sm mt-2">Memproses gambar dengan {{ currentMethod.name }}</p>
          </div>

          <div v-if="result && !analyzing" class="space-y-5">
            <!-- Heatmap Image (dynamic key) -->
            <div class="rounded-xl overflow-hidden border border-gray-200">
              <img
                :src="'data:image/jpeg;base64,' + (result.ela_image_base64 || result.noise_map_base64 || result.sharpening_map_base64 || result.median_map_base64 || result.ghost_image_base64 || result.copymove_image_base64)"
                class="w-full h-auto max-h-72 object-contain bg-gray-900"
              />
            </div>

            <!-- Statistics Grid -->
            <div class="grid grid-cols-3 gap-3">
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-gray-900">
                  {{ statValue1 }}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ statLabel1 }}
                </div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-gray-900">
                  {{ statValue2 }}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ statLabel2 }}
                </div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold" :class="suspiciousPct > 5 ? 'text-red-600' : suspiciousPct > 1 ? 'text-yellow-600' : 'text-green-600'">
                  {{ suspiciousPct }}%
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {{ statLabel3 }}
                </div>
              </div>
            </div>

            <!-- JPEG Ghost extra info -->
            <div v-if="method === 'jpeg_ghost' && result.quality_scores" class="bg-gray-50 rounded-xl p-4">
              <h3 class="font-semibold text-gray-900 mb-3">Quality-Error Curve</h3>
              <div class="flex items-end gap-px h-24">
                <div
                  v-for="(pair, idx) in result.quality_scores"
                  :key="idx"
                  class="flex-1 rounded-t transition-all duration-300"
                  :class="pair[0] === result.original_quality ? 'bg-primary-500' : pair[0] === result.ghost_quality ? 'bg-red-500' : 'bg-gray-300'"
                  :style="{ height: (pair[1] / maxQualityError * 100) + '%' }"
                  :title="'Q' + pair[0] + ': ' + pair[1]"
                ></div>
              </div>
              <div class="flex justify-between text-[10px] text-gray-400 mt-1">
                <span>Q1</span>
                <span>Q50</span>
                <span>Q99</span>
              </div>
              <div class="flex gap-4 mt-2 text-xs">
                <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-primary-500 inline-block"></span> Kualitas Asli ({{ result.original_quality }})</span>
                <span v-if="result.ghost_quality" class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-red-500 inline-block"></span> Ghost Quality ({{ result.ghost_quality }})</span>
              </div>
            </div>

            <!-- Analysis Conclusion -->
            <div class="bg-gray-50 rounded-xl p-4">
              <h3 class="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Kesimpulan Analisis
              </h3>
              <p class="text-sm text-gray-700 leading-relaxed" v-html="result.analysis.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')"></p>
            </div>

            <!-- Suspicion Level Bar -->
            <div>
              <div class="flex items-center justify-between text-sm mb-1">
                <span class="text-gray-600">Tingkat Kecurigaan</span>
                <span
                  class="font-semibold"
                  :class="suspiciousPct > 20 ? 'text-red-600' : suspiciousPct > 5 ? 'text-yellow-600' : 'text-green-600'"
                >
                  {{ suspiciousPct > 20 ? 'Tinggi' : suspiciousPct > 5 ? 'Sedang' : 'Rendah' }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  class="h-2.5 rounded-full transition-all duration-500"
                  :class="suspiciousPct > 20 ? 'bg-red-500' : suspiciousPct > 5 ? 'bg-yellow-500' : 'bg-green-500'"
                  :style="{ width: Math.min(suspiciousPct, 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- History Section -->
    <div class="card">
      <div class="card-header flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900">Riwayat Analisis</h2>
        <button @click="loadHistory" class="btn-secondary text-sm">
          {{ showHistory ? 'Sembunyikan' : 'Tampilkan Riwayat' }}
        </button>
      </div>
      <div v-if="showHistory" class="card-body">
        <div v-if="history.length === 0" class="text-center py-8 text-gray-400">
          Belum ada riwayat analisis
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-gray-500 border-b">
                <th class="pb-2 font-medium">ID</th>
                <th class="pb-2 font-medium">Metode</th>
                <th class="pb-2 font-medium">Tanggal</th>
                <th class="pb-2 font-medium">Ringkasan</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in history" :key="log.id" class="border-b border-gray-100 hover:bg-gray-50">
                <td class="py-3 font-mono text-gray-600">#{{ log.id }}</td>
                <td class="py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
                    {{ log.method_display }}
                  </span>
                </td>
                <td class="py-3 text-gray-600">{{ new Date(log.created_at).toLocaleString('id-ID') }}</td>
                <td class="py-3 text-gray-600 text-xs max-w-xs truncate">{{ log.analysis_text }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>