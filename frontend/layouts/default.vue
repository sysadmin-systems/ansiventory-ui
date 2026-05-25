<template>
  <div class="min-h-screen bg-bg-0 flex">
    <!-- sidebar -->
    <aside class="w-14 bg-bg-1 border-r border-border flex flex-col items-center py-3 gap-1 flex-shrink-0 fixed h-full z-10">
      <!-- logo -->
      <div class="w-9 h-9 rounded-lg bg-blue-bg border border-blue flex items-center justify-center mb-2 flex-shrink-0">
        <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-7 h-7 object-contain rounded" />
        <i v-else class="ti ti-server-2 text-blue-text text-lg" />
      </div>

      <UiNavItem to="/hosts" icon="ti-server" label="Hosts" />
      <UiNavItem to="/grupos" icon="ti-sitemap" label="Grupos" />
      <UiNavItem to="/vault" icon="ti-lock" label="Vault Tool" />

      <div class="flex-1" />
      <div class="w-7 h-px bg-border my-1" />
      <UiNavItem to="/settings" icon="ti-settings" label="Settings" />
      <button
        class="w-9 h-9 rounded-lg flex items-center justify-center text-text-3 hover:text-red-text hover:bg-red-bg transition-all"
        title="Sair"
        @click="auth.logout()"
      >
        <i class="ti ti-logout text-[17px]" />
      </button>
    </aside>

    <!-- main -->
    <div class="flex-1 flex flex-col ml-14">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const logoUrl = ref<string | null>(null)

onMounted(() => {
  const stored = localStorage.getItem('ansiventory_logo')
  if (stored) logoUrl.value = stored
})
</script>
