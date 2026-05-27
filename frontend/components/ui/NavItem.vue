<template>
  <NuxtLink :to="to" :class="['nav-item', { active: isActive }]">
    <i :class="`ti ${icon} text-base flex-shrink-0`" />
    <span>{{ label }}</span>
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
