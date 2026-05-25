<template>
  <div class="flex flex-col h-screen">

    <!-- topbar -->
    <header class="h-12 bg-bg-1 border-b border-border flex items-center px-4 gap-3 flex-shrink-0">
      <NuxtLink to="/hosts" class="btn btn-ghost h-8 px-2">
        <i class="ti ti-arrow-left text-sm" />
      </NuxtLink>

      <span class="font-mono text-sm font-semibold text-text-1">{{ host?.hostname }}</span>
      <span v-if="host" :class="`badge badge-${host.ambiente || 'inactive'}`">{{ host.ambiente || '—' }}</span>

      <div v-if="host" class="flex items-center gap-1.5 ml-1">
        <div :class="`w-1.5 h-1.5 rounded-full ${host.ativo ? 'bg-green' : 'bg-text-3'}`" />
        <span :class="`text-xs ${host.ativo ? 'text-green-text' : 'text-text-3'}`">
          {{ host.ativo ? 'ativo' : 'inativo' }}
        </span>
      </div>

      <div class="flex-1" />
      <button class="btn text-xs" @click="showEditHost = true"><i class="ti ti-edit" /> editar</button>
      <button class="btn btn-danger text-xs"><i class="ti ti-trash" /></button>
    </header>

    <!-- meta info -->
    <div v-if="host" class="px-4 py-2.5 border-b border-border bg-bg-0 flex items-center gap-2.5 flex-wrap flex-shrink-0">
      <span v-if="host.ip_address" class="tag flex items-center gap-1">
        <i class="ti ti-network text-[11px]" />{{ host.ip_address }}
      </span>
      <span v-if="host.vars['ansible_host']" class="tag flex items-center gap-1">
        <i class="ti ti-world text-[11px]" />{{ host.vars['ansible_host'] }}
      </span>
      <span v-for="g in host.grupos" :key="g" class="tag">{{ g }}</span>
      <div class="flex-1" />
      <span class="text-[11px] text-text-3">
        atualizado {{ formatDate(host.updated_at) }}
      </span>
    </div>

    <!-- abas -->
    <div class="px-4 py-2 border-b border-border bg-bg-0 flex gap-1 flex-shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="flex items-center gap-1.5 px-3 h-8 rounded text-xs transition-all"
        :class="activeTab === tab.value
          ? 'bg-bg-3 text-text-1'
          : 'text-text-2 hover:text-text-1 hover:bg-bg-2'"
        @click="activeTab = tab.value"
      >
        <i :class="`ti ${tab.icon} text-sm`" />
        {{ tab.label }}
      </button>
    </div>

    <!-- conteúdo das abas -->
    <div class="flex-1 overflow-y-auto px-4 py-3">

      <!-- vars do host -->
      <template v-if="activeTab === 'host'">
        <div class="flex items-center justify-between mb-3">
          <span class="text-[11px] text-text-3">{{ hostVarEntries.length }} variáveis específicas deste host</span>
          <button class="btn btn-primary text-xs h-7" @click="showAddVar = true"><i class="ti ti-plus text-xs" /> add var</button>
        </div>
        <UiVarsTable :vars="hostVarEntries" @update="onVarUpdate" @remove="onVarRemove" />

  <!-- modais -->
  <HostsEditHostModal
    v-if="showEditHost && host && grupos"
    :host="host"
    :grupos="grupos"
    @close="showEditHost = false"
    @saved="onSaved"
  />
  <HostsAddVarModal
    v-if="showAddVar && host"
    :host="host"
    @close="showAddVar = false"
    @saved="onSaved"
  />
</template>

      <!-- vars efetivas (merged) -->
      <template v-if="activeTab === 'effective'">
        <div class="flex items-center justify-between mb-3">
          <span class="text-[11px] text-text-3">{{ effectiveVarEntries.length }} variáveis efetivas (group_vars + host_vars)</span>
        </div>
        <UiVarsTable :vars="effectiveVarEntries" :readonly="true" />
      </template>

      <!-- audit log -->
      <template v-if="activeTab === 'audit'">
        <div v-if="!audit?.length" class="text-sm text-text-3 mt-4">nenhum registro de auditoria.</div>
        <div v-for="log in audit" :key="log.id" class="border border-border rounded-lg p-3 mb-2 bg-bg-1">
          <div class="flex items-center gap-2 mb-1">
            <span :class="`badge ${log.action === 'create' ? 'badge-onprem' : log.action === 'delete' ? 'bg-red-bg text-red-text' : 'badge-azure'}`">
              {{ log.action }}
            </span>
            <span class="text-xs text-text-2 font-mono">{{ log.changed_by }}</span>
            <span class="text-[11px] text-text-3 ml-auto">{{ formatDate(log.changed_at) }}</span>
          </div>
          <pre v-if="log.diff" class="text-[10px] font-mono text-text-2 overflow-auto">{{ JSON.stringify(log.diff, null, 2) }}</pre>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Host, HostVars, AuditLog, Grupo } from '~/types'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const auth = useAuthStore()
const { get } = useApi()

const hostId = computed(() => route.params.id)
const activeTab = ref('host')

const tabs = [
  { value: 'host',      label: 'vars do host',    icon: 'ti-variable' },
  { value: 'effective', label: 'vars efetivas',    icon: 'ti-layers-intersect' },
  { value: 'audit',     label: 'audit log',        icon: 'ti-history' },
]

const showEditHost = ref(false)
const showAddVar = ref(false)

const { data: grupos } = useAsyncData(
  'grupos',
  async () => {
    if (!auth.workspaceId) return []
    return get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`)
  },
  { default: () => [] as Grupo[] }
)

const { data: host, refresh: refreshHost } = useAsyncData(
  `host-${hostId.value}`,
  async () => {
    if (!auth.workspaceId) return null
    return get<Host>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}`)
  }
)

const { data: effectiveVars, refresh: refreshVars } = useAsyncData(
  `host-vars-${hostId.value}`,
  async () => {
    if (!auth.workspaceId) return null
    return get<HostVars>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}/vars`)
  }
)

const { data: audit, refresh: refreshAudit } = useAsyncData(
  `host-audit-${hostId.value}`,
  async () => {
    if (!auth.workspaceId) return null
    return get<AuditLog[]>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}/audit`)
  }
)

// garante que recarrega quando workspaceId estiver disponível
watch(() => auth.workspaceId, (id) => {
  if (id) {
    refreshHost()
    refreshVars()
    refreshAudit()
  }
}, { immediate: true })

onMounted(() => {
  if (auth.workspaceId) {
    refreshHost()
    refreshVars()
    refreshAudit()
  }
})

const hostVarEntries = computed(() =>
  Object.entries(host.value?.vars ?? {}).map(([k, v]) => ({ key: k, value: v }))
)

const effectiveVarEntries = computed(() =>
  Object.entries(effectiveVars.value?.vars_final ?? {}).map(([k, v]) => ({ key: k, value: v }))
)

function formatDate(d: string) {
  return new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

async function onVarUpdate(key: string, value: unknown) {
  if (!host.value) return
  const updatedVars = { ...host.value.vars, [key]: value }
  await patch(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`, { vars: updatedVars })
  refreshHost()
}

async function onVarRemove(key: string) {
  if (!host.value) return
  const updatedVars = { ...host.value.vars }
  delete updatedVars[key]
  await patch(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`, { vars: updatedVars })
  refreshHost()
}

function onSaved() {
  refreshHost()
  refreshVars()
}
</script>
