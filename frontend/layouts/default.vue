<template>
  <div class="min-h-screen bg-bg-0 flex">

    <!-- sidebar -->
    <aside class="w-60 bg-bg-1 border-r border-border flex flex-col flex-shrink-0 fixed h-full z-10">

      <!-- logo + brand -->
      <div class="px-4 py-5 border-b border-border flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-blue/15 border border-blue/40 flex items-center justify-center shadow-glow-sm flex-shrink-0">
            <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-7 h-7 object-contain rounded-lg" />
            <i v-else class="ti ti-server-2 text-blue-text text-lg" />
          </div>
          <div>
            <div class="text-sm font-bold text-text-1 leading-tight tracking-tight">Ansiventory</div>
            <div class="text-[10px] text-text-3 leading-tight">inventário Ansible</div>
          </div>
        </div>
      </div>

      <!-- workspace badge -->
      <div class="px-4 py-3 border-b border-border flex-shrink-0">
        <div class="flex items-center gap-2 bg-bg-2 rounded-lg px-3 py-2 border border-border">
          <i class="ti ti-layers-intersect text-[11px] text-blue-text flex-shrink-0" />
          <span class="text-[11px] font-mono text-text-2 truncate">{{ auth.workspace }}</span>
          <div class="ml-auto w-1.5 h-1.5 rounded-full bg-green flex-shrink-0" />
        </div>
      </div>

      <!-- navigation -->
      <nav class="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-0.5">
        <p class="text-[10px] font-semibold text-text-3 tracking-widest uppercase px-3 mb-2">Navegação</p>
        <UiNavItem to="/hosts" icon="ti-server" label="Hosts" />
        <UiNavItem to="/grupos" icon="ti-sitemap" label="Grupos" />
        <UiNavItem to="/vault" icon="ti-lock" label="Vault" />
      </nav>

      <!-- bottom -->
      <div class="px-3 py-3 border-t border-border flex-shrink-0 flex flex-col gap-0.5">
        <UiNavItem to="/settings" icon="ti-settings" label="Configurações" />
        <button
          class="nav-item text-red-text hover:bg-red/10 hover:text-red-text"
          @click="auth.logout()"
        >
          <i class="ti ti-logout text-base flex-shrink-0" />
          <span>Sair</span>
        </button>
      </div>
    </aside>

    <!-- main content -->
    <div class="flex-1 flex flex-col ml-60 min-w-0">
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
