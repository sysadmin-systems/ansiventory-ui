<template>
  <div class="flex flex-col h-screen">
    <header class="h-12 bg-bg-1 border-b border-border flex items-center px-4 flex-shrink-0">
      <span class="text-sm font-semibold text-text-1">settings</span>
    </header>
    <div class="flex-1 flex items-center justify-center text-text-3 text-sm gap-2">
      <i class="ti ti-settings text-xl" />
      em desenvolvimento
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
</script>
