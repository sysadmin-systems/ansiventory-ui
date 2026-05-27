export default defineNuxtConfig({
  devtools: { enabled: process.env.NODE_ENV !== 'production' },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
  ],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_API_BASE || 'http://localhost:8000',
    },
  },

  nitro: {
    devProxy: {
      '/api': {
        target: process.env.NUXT_API_BASE || 'http://localhost:8000',
        changeOrigin: true,
        prependPath: false,
      },
    },
  },

  app: {
    head: {
      title: 'Ansiventory UI',
      meta: [
        { name: 'description', content: 'Inventário dinâmico Ansible' },
        { 'http-equiv': 'X-Content-Type-Options', content: 'nosniff' },
        { name: 'referrer', content: 'strict-origin-when-cross-origin' },
      ],
    },
  },

  compatibilityDate: '2024-11-01',
})
