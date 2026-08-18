<script setup>
const currentYear = new Date().getFullYear()

const footerLinks = [
  { name: 'Documentation', href: '#' },
  { name: 'API Reference', href: '#' },
  { name: 'Privacy Policy', href: '#' },
  { name: 'Terms of Service', href: '#' },
]

const socialLinks = [
  { name: 'GitHub', icon: 'M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.003 10.003 0 0022 12c0-5.523-4.477-10-10-10z' },
  { name: 'Twitter', icon: 'M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z' },
  { name: 'LinkedIn', icon: 'M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2zM4 6a2 2 0 100-4 2 2 0 000 4z' },
]
</script>

<template>
  <footer class="bg-white border-t border-gray-200">
    <div class="max-w-7xl mx-auto px-4 lg:px-6 py-4">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Copyright -->
        <div class="text-center md:text-left">
          <p class="text-sm text-gray-500">
            &copy; {{ currentYear }} FaceAI. All rights reserved.
          </p>
          <p class="text-xs text-gray-400 mt-1">
            Face Recognition System
          </p>
        </div>

        <!-- Footer Links -->
        <nav class="flex flex-wrap items-center justify-center gap-4 md:gap-6" aria-label="Footer navigation">
          <a
            v-for="link in footerLinks"
            :key="link.name"
            :href="link.href"
            class="text-sm text-gray-500 hover:text-primary-600 transition-colors"
          >
            {{ link.name }}
          </a>
        </nav>

        <!-- Social Links -->
        <div class="flex items-center justify-center gap-4">
          <a
            v-for="social in socialLinks"
            :key="social.name"
            :href="social.href"
            class="text-gray-400 hover:text-primary-600 transition-colors"
            aria-label="social.name"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path :d="social.icon" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>