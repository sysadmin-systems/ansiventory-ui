<template>
  <div class="flex flex-col h-screen">

    <!-- topbar -->
    <header class="h-12 bg-bg-1 border-b border-border flex items-center px-4 gap-3 flex-shrink-0">
      <span class="text-[11px] font-mono bg-bg-2 border border-border rounded-full px-3 py-0.5 text-text-2 flex items-center gap-1.5">
        <i class="ti ti-layers-intersect text-[11px]" />
        {{ auth.workspace }}
      </span>

      <div class="flex-1 max-w-xs bg-bg-2 border border-border rounded-lg flex items-center px-3 gap-2 h-8">
        <i class="ti ti-search text-text-3 text-sm" />
        <input
          v-model="search"
          type="text"
          placeholder="buscar hostname..."
          class="bg-transparent text-sm text-text-1 placeholder-text-3 outline-none w-full font-mono"
        />
        <button v-if="search" class="text-text-3 hover:text-text-1" @click="search = ''">
          <i class="ti ti-x text-xs" />
        </button>
      </div>

      <div class="flex gap-1.5">
        <button
          v-for="f in ambienteFilters"
          :key="f.value"
          class="h-6 px-2.5 text-xs rounded-full border transition-colors"
          :class="filterAmbiente === f.value
            ? 'bg-blue-bg text-blue-text border-blue'
            : 'bg-transparent text-text-2 border-border hover:border-border-2'"
          @click="filterAmbiente = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <div class="flex-1" />
      <button class="btn btn-primary text-xs" @click="showNewHost = true">
        <i class="ti ti-plus" /> novo host
      </button>
    </header>

    <!-- stat cards -->
    <div class="grid grid-cols-4 gap-2.5 px-4 py-3 border-b border-border bg-bg-0 flex-shrink-0">
      <div class="stat-card">
        <div class="text-xl font-semibold text-blue-text">{{ stats.total }}</div>
        <div class="text-[11px] text-text-2 mt-0.5">total de hosts</div>
      </div>
      <div class="stat-card">
        <div class="text-xl font-semibold text-green-text">{{ stats.ativos }}</div>
        <div class="text-[11px] text-text-2 mt-0.5">ativos</div>
      </div>
      <div class="stat-card">
        <div class="text-xl font-semibold text-blue-text">{{ stats.azure }}</div>
        <div class="text-[11px] text-text-2 mt-0.5">azure</div>
      </div>
      <div class="stat-card">
        <div class="text-xl font-semibold text-amber-text">{{ stats.inativos }}</div>
        <div class="text-[11px] text-text-2 mt-0.5">inativos</div>
      </div>
    </div>

    <!-- header tabela -->
    <div class="px-4 py-1.5 border-b border-border bg-bg-0 flex gap-3 text-[10px] text-text-3 font-medium tracking-wide flex-shrink-0">
      <span class="w-2" />
      <span class="w-48">hostname</span>
      <span class="w-20">ambiente</span>
      <span class="flex-1">município</span>
      <span class="w-48">grupos</span>
      <span class="w-4" />
    </div>

    <!-- lista -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="pending" class="flex items-center justify-center h-32 text-text-3 text-sm gap-2">
        <i class="ti ti-loader-2 animate-spin" /> carregando...
      </div>
      <div v-else-if="filtered.length === 0" class="flex flex-col items-center justify-center h-32 text-text-3 text-sm gap-2">
        <i class="ti ti-server-off text-2xl" />
        nenhum host encontrado
      </div>
      <NuxtLink
        v-for="host in filtered"
        :key="host.id"
        :to="`/hosts/${host.id}`"
        class="flex items-center px-4 py-2.5 border-b border-border hover:bg-bg-2 transition-colors gap-3 cursor-pointer no-underline"
      >
        <div class="w-2 flex items-center">
          <div :class="`w-1.5 h-1.5 rounded-full ${host.ativo ? 'bg-green' : 'bg-text-3'}`" />
        </div>
        <div class="w-48 font-mono text-xs font-medium text-text-1 truncate">{{ host.hostname }}</div>
        <div class="w-20">
          <span :class="`badge badge-${host.ambiente || 'inactive'}`">{{ host.ambiente || '—' }}</span>
        </div>
        <div class="flex-1 text-xs text-text-2 truncate">{{ host.municipio || '—' }}</div>
        <div class="w-48 flex gap-1 flex-wrap">
          <span v-for="g in host.grupos.slice(0, 2)" :key="g" class="tag">{{ g }}</span>
          <span v-if="host.grupos.length > 2" class="tag">+{{ host.grupos.length - 2 }}</span>
        </div>
        <i class="ti ti-chevron-right text-text-3 text-xs w-4" />
      </NuxtLink>
    </div>

    <!-- footer -->
    <div class="px-4 py-2 border-t border-border bg-bg-1 flex-shrink-0">
      <span class="text-[11px] text-text-3">{{ filtered.length }} hosts exibidos</span>
    </div>

    <!-- modal novo host -->
    <HostsNewHostModal
      v-if="showNewHost && grupos"
      :grupos="grupos"
      @close="showNewHost = false"
      @saved="refresh()"
    />

  </div>
</template>

<script setup lang="ts">
import type { Host, Grupo } from '~/types'

definePageMeta({ middleware: 'auth' })

const auth = useAuthStore()
const { get } = useApi()

const search = ref('')
const filterAmbiente = ref('todos')
const showNewHost = ref(false)

const ambienteFilters = [
  { value: 'todos',        label: 'todos' },
  { value: 'azure',        label: 'azure' },
  { value: 'onprem',       label: 'onprem' },
  { value: 'digitalocean', label: 'do' },
]

const { data: grupos } = useAsyncData(
  'grupos-list',
  async () => {
    if (!auth.workspaceId) return [] as Grupo[]
    return get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`)
  },
  { default: () => [] as Grupo[] }
)

const { data: hosts, pending, refresh } = useAsyncData(
  'hosts',
  async () => {
    if (!auth.workspaceId) return [] as Host[]
    return get<Host[]>(`/workspaces/${auth.workspaceId}/hosts`)
  },
  { default: () => [] as Host[] }
)

watch(() => auth.workspaceId, (id) => {
  if (id) refresh()
}, { immediate: true })

// garante reload dos dados após hidratação no cliente
onMounted(() => {
  if (auth.workspaceId) refresh()
})

const filtered = computed(() => {
  let list = hosts.value ?? []
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(h =>
      h.hostname.toLowerCase().includes(q) ||
      h.municipio?.toLowerCase().includes(q)
    )
  }
  if (filterAmbiente.value !== 'todos') {
    list = list.filter(h => h.ambiente === filterAmbiente.value)
  }
  return list
})

const stats = computed(() => ({
  total:    hosts.value?.length ?? 0,
  ativos:   hosts.value?.filter(h => h.ativo).length ?? 0,
  inativos: hosts.value?.filter(h => !h.ativo).length ?? 0,
  azure:    hosts.value?.filter(h => h.ambiente === 'azure').length ?? 0,
}))
</script>
