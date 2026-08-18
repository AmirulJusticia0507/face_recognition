<script setup>
const features = [
  { title: 'Face Comparison', description: 'Compare two face images to determine similarity using advanced deep learning models.', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { title: 'Face Identification', description: 'Identify unknown faces against a database of registered individuals.', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
  { title: 'Live Camera Detection', description: 'Real-time face detection and expression analysis through webcam.', icon: 'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z' },
  { title: 'Pose Estimation', description: 'Analyze face pose quality including lighting, occlusion, and sharpness.', icon: 'M17 14v6m-3-3h6M6 10h2a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2zm10 0h2a2 2 0 002-2V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v2a2 2 0 002 2zM6 20h2a2 2 0 002-2v-2a2 2 0 00-2-2H6a2 2 0 00-2 2v2a2 2 0 002 2z' },
  { title: 'ETLE Camera', description: 'Electronic Traffic Law Enforcement with automated violation detection.', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
  { title: 'Violation Logs', description: 'Track and manage detected traffic violations with detailed logs.', icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' },
]

const techStack = [
  { name: 'Django', description: 'Backend framework' },
  { name: 'Vue.js 3', description: 'Frontend framework' },
  { name: 'Tailwind CSS', description: 'UI styling' },
  { name: 'DeepFace', description: 'Face recognition' },
  { name: 'OpenCV', description: 'Computer vision' },
  { name: 'REST Framework', description: 'API endpoints' },
]

const team = [
  { name: 'FaceAI Team', role: 'Development Team' },
]
</script>

<template>
  <div class="space-y-12">
    <!-- Hero -->
    <div class="text-center max-w-3xl mx-auto">
      <div class="w-20 h-20 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.734-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      <h1 class="text-4xl font-bold text-gray-900 mb-4">About FaceAI</h1>
      <p class="text-lg text-gray-600">
        FaceAI is a comprehensive face recognition system built with Django and Vue.js. 
        It leverages state-of-the-art deep learning models for face comparison, identification, 
        real-time detection, and traffic law enforcement.
      </p>
    </div>

    <!-- Features -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 text-center mb-8">Features</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="feature in features" :key="feature.title" class="card hover:shadow-md transition-shadow">
          <div class="card-body">
            <div class="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center mb-4">
              <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feature.icon" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ feature.title }}</h3>
            <p class="text-gray-500">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Tech Stack -->
    <div class="card">
      <div class="card-header">
        <h2 class="text-2xl font-bold text-gray-900">Technology Stack</h2>
      </div>
      <div class="card-body">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div v-for="tech in techStack" :key="tech.name" class="text-center p-4 bg-gray-50 rounded-xl">
            <p class="font-semibold text-gray-900">{{ tech.name }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ tech.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Team -->
    <div class="text-center">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Development Team</h2>
      <p class="text-gray-500 max-w-2xl mx-auto">
        Built as a face recognition research project. This system demonstrates the integration of 
        multiple deep learning models for real-world face analysis applications.
      </p>
    </div>
  </div>
</template>