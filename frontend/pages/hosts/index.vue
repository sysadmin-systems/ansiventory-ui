<template>
  <div class="flex flex-col h-screen">

    <!-- topbar -->
    <header class="h-14 bg-bg-1 border-b border-border flex items-center px-6 gap-4 flex-shrink-0">
      <div>
        <h1 class="text-sm font-semibold text-text-1 leading-none">Hosts</h1>
        <p class="text-[11px] text-text-3 mt-0.5">inventário de servidores</p>
      </div>

      <div class="w-px h-6 bg-border mx-1" />

      <div class="flex-1 max-w-sm bg-bg-2 border border-border rounded-lg flex items-center px-3 gap-2 h-9 focus-within:border-blue/50 focus-within:ring-2 focus-within:ring-blue/10 transition-all">
        <i class="ti ti-search text-text-3 text-sm flex-shrink-0" />
        <input
          v-model="search"
          type="text"
          placeholder="buscar hostname ou município..."
          class="bg-transparent text-sm text-text-1 placeholder-text-3 outline-none w-full font-mono"
        />
        <button v-if="search" class="text-text-3 hover:text-text-1 transition-colors" @click="search = ''">
          <i class="ti ti-x text-xs" />
        </button>
      </div>

      <div class="flex gap-1.5">
        <button
          v-for="f in ambienteFilters"
          :key="f.value"
          class="h-7 px-3 text-xs font-medium rounded-lg border transition-all duration-150"
          :class="filterAmbiente === f.value
            ? 'bg-blue/15 text-blue-text border-blue/40 shadow-glow-sm'
            : 'bg-transparent text-text-3 border-border hover:text-text-2 hover:border-border-2 hover:bg-bg-3'"
          @click="filterAmbiente = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <div class="flex-1" />
      <button class="btn btn-primary gap-2" @click="showNewHost = true">
        <i class="ti ti-plus text-sm" />
        <span>Novo host</span>
      </button>
    </header>

    <!-- stat cards -->
    <div class="grid grid-cols-4 gap-4 px-6 py-4 border-b border-border bg-bg-0 flex-shrink-0">
      <div class="stat-card stat-card-blue">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-3xl font-bold text-blue-text leading-none">{{ stats.total }}</div>
            <div class="text-xs text-text-3 mt-2 font-medium uppercase tracking-wider">Total de hosts</div>
          </div>
          <div class="w-10 h-10 rounded-xl bg-blue/10 border border-blue/20 flex items-center justify-center flex-shrink-0">
            <i class="ti ti-server text-blue-text text-lg" />
          </div>
        </div>
      </div>
      <div class="stat-card stat-card-green">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-3xl font-bold text-green-text leading-none">{{ stats.ativos }}</div>
            <div class="text-xs text-text-3 mt-2 font-medium uppercase tracking-wider">Ativos</div>
          </div>
          <div class="w-10 h-10 rounded-xl bg-green/10 border border-green/20 flex items-center justify-center flex-shrink-0">
            <i class="ti ti-circle-check text-green-text text-lg" />
          </div>
        </div>
      </div>
      <div class="stat-card stat-card-azure">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-3xl font-bold text-azure-text leading-none">{{ stats.azure }}</div>
            <div class="text-xs text-text-3 mt-2 font-medium uppercase tracking-wider">Azure</div>
          </div>
          <div class="w-10 h-10 rounded-xl bg-azure/10 border border-azure/20 flex items-center justify-center flex-shrink-0">
            <i class="ti ti-brand-azure text-azure-text text-lg" />
          </div>
        </div>
      </div>
      <div class="stat-card stat-card-amber">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-3xl font-bold text-amber-text leading-none">{{ stats.inativos }}</div>
            <div class="text-xs text-text-3 mt-2 font-medium uppercase tracking-wider">Inativos</div>
          </div>
          <div class="w-10 h-10 rounded-xl bg-amber/10 border border-amber/20 flex items-center justify-center flex-shrink-0">
            <i class="ti ti-server-off text-amber-text text-lg" />
          </div>
        </div>
      </div>
    </div>

    <!-- table header -->
    <div class="px-6 py-2 border-b border-border bg-bg-0 flex items-center gap-4 text-[10px] text-text-3 font-semibold tracking-widest uppercase flex-shrink-0">
      <span class="w-4" />
      <span class="w-52">Hostname</span>
      <span class="w-24">Ambiente</span>
      <span class="flex-1">Município</span>
      <span class="w-56">Grupos</span>
      <span class="w-4" />
    </div>

    <!-- list -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="pending" class="flex items-center justify-center h-40 text-text-3 text-sm gap-3">
        <i class="ti ti-loader-2 animate-spin text-blue-text text-xl" />
        <span>Carregando hosts...</span>
      </div>
      <div v-else-if="filtered.length === 0" class="flex flex-col items-center justify-center h-48 gap-4">
        <div class="w-14 h-14 rounded-2xl bg-bg-2 border border-border flex items-center justify-center">
          <i class="ti ti-server-off text-2xl text-text-3" />
        </div>
        <div class="text-center">
          <p class="text-text-2 text-sm font-medium">Nenhum host encontrado</p>
          <p class="text-text-3 text-xs mt-1">Tente ajustar os filtros de busca</p>
        </div>
      </div>
      <NuxtLink
        v-for="host in filtered"
        :key="host.id"
        :to="`/hosts/${host.id}`"
        class="group flex items-center px-6 py-3 border-b border-border/50 hover:bg-bg-1 transition-colors gap-4 cursor-pointer no-underline"
      >
        <div class="w-4 flex items-center justify-center flex-shrink-0">
          <div
            class="w-2 h-2 rounded-full transition-all duration-200"
            :class="host.ativo
              ? 'bg-green shadow-[0_0_6px_rgba(61,184,122,0.6)]'
              : 'bg-text-3'"
          />
        </div>
        <div class="w-52 font-mono text-sm font-medium text-text-1 truncate group-hover:text-blue-text transition-colors">
          {{ host.hostname }}
        </div>
        <div class="w-24">
          <span :class="`badge badge-${host.ambiente || 'inactive'}`">{{ host.ambiente || '—' }}</span>
        </div>
        <div class="flex-1 text-sm text-text-2 truncate">{{ host.municipio || '—' }}</div>
        <div class="w-56 flex gap-1.5 flex-wrap">
          <span v-for="g in host.grupos.slice(0, 2)" :key="g" class="tag">{{ g }}</span>
          <span v-if="host.grupos.length > 2" class="tag opacity-60">+{{ host.grupos.length - 2 }}</span>
        </div>
        <i class="ti ti-chevron-right text-text-3 text-sm w-4 group-hover:text-blue-text group-hover:translate-x-0.5 transition-all" />
      </NuxtLink>
    </div>

    <!-- footer -->
    <div class="px-6 py-2.5 border-t border-border bg-bg-1 flex items-center justify-between flex-shrink-0">
      <div class="flex items-center gap-2 text-xs text-text-3">
        <i class="ti ti-database text-[11px]" />
        <span>{{ filtered.length }} de {{ hosts?.length ?? 0 }} hosts exibidos</span>
      </div>
      <div v-if="search || filterAmbiente !== 'todos'" class="text-xs text-blue-text">
        <button class="hover:underline" @click="search = ''; filterAmbiente = 'todos'">Limpar filtros</button>
      </div>
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
  { value: 'todos',        label: 'Todos' },
  { value: 'azure',        label: 'Azure' },
  { value: 'onprem',       label: 'Onprem' },
  { value: 'digitalocean', label: 'DO' },
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
