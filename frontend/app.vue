<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>

    <Transition name="auth-check">
      <div
        v-if="auth.checking && route.path !== '/login'"
        class="fixed inset-0 bg-bg-0 z-[9999] flex items-center justify-center"
      >
        <i class="ti ti-loader-2 animate-spin text-blue-text text-2xl" />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()

useHead({
  link: [
    {
      rel: 'stylesheet',
      href: 'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css',
    },
    {
      rel: 'preconnect',
      href: 'https://fonts.googleapis.com',
    },
    {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
    },
  ],
})
</script>