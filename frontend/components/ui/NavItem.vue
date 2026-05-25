<template>
  <NuxtLink
    :to="to"
    class="w-9 h-9 rounded-lg flex items-center justify-center transition-all"
    :class="isActive
      ? 'bg-blue-bg text-blue-text'
      : 'text-text-3 hover:text-text-2 hover:bg-bg-2'"
    :title="label"
  >
    <i :class="`ti ${icon} text-[17px]`" />
  </NuxtLink>
</template>

<script setup lang="ts">
const props = defineProps<{
  to: string
  icon: string
  label: string
}>()

const route = useRoute()
const isActive = computed(() => route.path.startsWith(props.to))
</script>
