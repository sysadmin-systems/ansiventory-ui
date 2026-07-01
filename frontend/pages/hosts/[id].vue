<template>
  <div class="flex flex-col h-screen">

    <!-- topbar -->
    <header class="h-14 bg-bg-1 border-b border-border flex items-center px-6 gap-4 flex-shrink-0">
      <NuxtLink to="/hosts" class="btn btn-ghost h-8 w-8 p-0 justify-center flex-shrink-0" title="Voltar">
        <i class="ti ti-arrow-left text-sm" />
      </NuxtLink>

      <div class="w-px h-5 bg-border" />

      <div class="flex items-center gap-3 flex-1 min-w-0">
        <div
          class="w-2 h-2 rounded-full flex-shrink-0"
          :class="host?.ativo ? 'bg-green shadow-[0_0_6px_rgba(61,184,122,0.7)]' : 'bg-text-3'"
        />
        <span class="font-mono text-base font-semibold text-text-1 truncate">{{ host?.hostname }}</span>
        <span v-if="host" :class="`badge badge-${host.ambiente || 'inactive'}`">{{ host.ambiente || '—' }}</span>
        <span v-if="host" :class="`text-xs font-medium ${host.ativo ? 'text-green-text' : 'text-text-3'}`">
          {{ host.ativo ? 'ativo' : 'inativo' }}
        </span>
      </div>

      <button class="btn gap-2" @click="showEditHost = true">
        <i class="ti ti-edit text-sm" /> Editar
      </button>
      <button class="btn btn-danger gap-2" @click="confirmDelete = true">
        <i class="ti ti-trash text-sm" />
      </button>
    </header>

    <!-- meta info -->
    <div v-if="host" class="px-6 py-2.5 border-b border-border bg-bg-0 flex items-center gap-2 flex-wrap flex-shrink-0 min-h-[44px]">
      <span v-if="host.ip_address" class="tag gap-1 font-mono">
        <i class="ti ti-network text-[11px]" />{{ host.ip_address }}
      </span>
      <span v-if="host.vars['ansible_host']" class="tag gap-1 font-mono">
        <i class="ti ti-world text-[11px]" />{{ host.vars['ansible_host'] }}
      </span>
      <span v-for="g in host.grupos" :key="g" class="tag">{{ g }}</span>
      <div class="flex-1" />
      <span class="text-[11px] text-text-3">
        <i class="ti ti-clock text-[11px] mr-1" />atualizado {{ formatDate(host.updated_at) }}
      </span>
    </div>

    <!-- tabs -->
    <div class="px-6 border-b border-border bg-bg-1 flex gap-0 flex-shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="relative flex items-center gap-2 px-4 h-11 text-sm font-medium transition-all"
        :class="activeTab === tab.value
          ? 'text-blue-text'
          : 'text-text-2 hover:text-text-1'"
        @click="activeTab = tab.value"
      >
        <i :class="`ti ${tab.icon} text-sm`" />
        {{ tab.label }}
        <span
          v-if="activeTab === tab.value"
          class="absolute bottom-0 left-2 right-2 h-0.5 bg-blue rounded-t-full"
        />
      </button>
    </div>

    <!-- tab content -->
    <div class="flex-1 overflow-y-auto px-6 py-5">

      <!-- vars do host -->
      <template v-if="activeTab === 'host'">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm font-medium text-text-1">Variáveis do host</p>
            <p class="text-xs text-text-3 mt-0.5">{{ hostVarEntries.length }} variáveis específicas deste host</p>
          </div>
          <button class="btn btn-primary gap-2" @click="showAddVar = true">
            <i class="ti ti-plus text-sm" /> Adicionar var
          </button>
        </div>
        <UiVarsTable :vars="hostVarEntries" @update="onVarUpdate" @remove="onVarRemove" />
      </template>

      <!-- vars efetivas -->
      <template v-if="activeTab === 'effective'">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm font-medium text-text-1">Variáveis efetivas</p>
            <p class="text-xs text-text-3 mt-0.5">{{ effectiveVarEntries.length }} vars — group_vars + host_vars mescladas</p>
          </div>
          <div class="flex items-center gap-3 text-[11px] text-text-3">
            <span class="flex items-center gap-1">
              <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-bg-3 border border-border text-[9px]">
                <i class="ti ti-sitemap text-[8px]" />grupo
              </span>
              vem do grupo
            </span>
            <span class="flex items-center gap-1">
              <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-blue/10 text-blue-text border border-blue/20 text-[9px]">
                <i class="ti ti-server text-[8px]" />override
              </span>
              host sobrescreve grupo
            </span>
          </div>
        </div>
        <UiVarsTable :vars="effectiveVarEntries" @update="onEffectiveVarUpdate" @remove="onEffectiveVarRemove" />

        <!-- modal de confirmação de override -->
        <div v-if="overrideConfirm" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
          <div class="glass-card w-full max-w-sm">
            <div class="p-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl bg-amber/10 border border-amber/30 flex items-center justify-center flex-shrink-0">
                  <i class="ti ti-alert-triangle text-amber-text text-lg" />
                </div>
                <div>
                  <div class="text-sm font-semibold text-text-1">Criar override no host</div>
                  <div class="text-xs text-text-3 mt-0.5">variável de grupo</div>
                </div>
              </div>
              <p class="text-sm text-text-2 mb-3">
                A variável <span class="font-mono text-text-1">{{ overrideConfirm.key }}</span>
                vem do grupo <span class="font-mono text-blue-text">{{ overrideConfirm.group }}</span>.
              </p>
              <p class="text-xs text-text-3 bg-bg-2 rounded-lg p-3 border border-border">
                Salvar criará um override específico neste host, sem alterar o grupo.
                O valor do grupo continuará valendo para os demais membros.
              </p>
            </div>
            <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
              <button class="btn" @click="overrideConfirm = null">Cancelar</button>
              <button class="btn btn-primary gap-2" @click="confirmOverride">
                <i class="ti ti-check text-sm" /> Criar override
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- audit log -->
      <template v-if="activeTab === 'audit'">
        <div v-if="!audit?.length" class="flex flex-col items-center justify-center h-40 gap-3 text-text-3">
          <i class="ti ti-history text-2xl" />
          <span class="text-sm">Nenhum registro de auditoria</span>
        </div>
        <div v-else class="flex flex-col gap-3">
          <div
            v-for="log in audit"
            :key="log.id"
            class="glass-card overflow-hidden"
          >
            <div class="flex items-center gap-3 px-4 py-3 border-b border-border/60">
              <span :class="`badge ${
                log.action === 'create' ? 'badge-onprem' :
                log.action === 'delete' ? 'bg-red/10 text-red-text border-red/30' :
                'badge-azure'
              }`">{{ log.action }}</span>
              <span class="text-xs font-mono text-text-2">{{ log.changed_by }}</span>
              <span class="text-[11px] text-text-3 ml-auto">{{ formatDate(log.changed_at) }}</span>
            </div>
            <pre v-if="log.diff" class="px-4 py-3 text-[11px] font-mono text-text-2 overflow-auto bg-bg-0/50 leading-relaxed">{{ JSON.stringify(log.diff, null, 2) }}</pre>
          </div>
        </div>
      </template>

    </div>

    <!-- modals (fora do conteúdo das abas) -->
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

    <!-- confirm delete -->
    <div v-if="confirmDelete && host" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-sm">
        <div class="p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-red/10 border border-red/30 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-trash text-red-text text-lg" />
            </div>
            <div>
              <div class="text-sm font-semibold text-text-1">Excluir host</div>
              <div class="text-xs text-text-3 mt-0.5">Esta ação não pode ser desfeita</div>
            </div>
          </div>
          <p class="text-sm text-text-2">
            Confirma a exclusão de
            <span class="font-mono text-text-1">{{ host.hostname }}</span>?
            Todas as vars e histórico de auditoria serão removidos.
          </p>
        </div>
        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button class="btn" @click="confirmDelete = false">Cancelar</button>
          <button class="btn btn-danger gap-2" @click="deleteHost">
            <i class="ti ti-trash text-sm" /> Excluir
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Host, HostVars, AuditLog, Grupo, VarDetail } from '~/types'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const auth = useAuthStore()
const { get, patch, del } = useApi()

const hostId = computed(() => route.params.id)
const activeTab = ref('host')

const tabs = [
  { value: 'host',      label: 'Vars do host',   icon: 'ti-variable' },
  { value: 'effective', label: 'Vars efetivas',   icon: 'ti-layers-intersect' },
  { value: 'audit',     label: 'Audit log',       icon: 'ti-history' },
]

const showEditHost = ref(false)
const showAddVar = ref(false)
const confirmDelete = ref(false)
const overrideConfirm = ref<{ key: string; value: unknown; group: string } | null>(null)

const grupos = ref<Grupo[]>([])
const host = ref<Host | null>(null)
const effectiveVars = ref<HostVars | null>(null)
const audit = ref<AuditLog[]>([])

async function loadData() {
  if (!auth.workspaceId) return
  const [h, g, ev, al] = await Promise.all([
    get<Host>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}`),
    get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`),
    get<HostVars>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}/vars`),
    get<AuditLog[]>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}/audit`),
  ])
  host.value = h
  grupos.value = g
  effectiveVars.value = ev
  audit.value = al
}

async function refreshHost() { if (auth.workspaceId) host.value = await get<Host>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}`) }
async function refreshVars() { if (auth.workspaceId) effectiveVars.value = await get<HostVars>(`/workspaces/${auth.workspaceId}/hosts/${hostId.value}/vars`) }

onMounted(() => loadData())
watch(() => auth.workspaceId, (id) => { if (id) loadData() })

const hostVarEntries = computed(() =>
  Object.entries(host.value?.vars ?? {}).map(([k, v]) => ({ key: k, value: v }))
)

const effectiveVarEntries = computed(() =>
  Object.entries(effectiveVars.value?.vars_detail ?? effectiveVars.value?.vars_final ?? {}).map(([k, detail]) => {
    if (effectiveVars.value?.vars_detail) {
      const d = detail as VarDetail
      return { key: k, value: d.value, source: d.source, group: d.group, overrides: d.overrides }
    }
    return { key: k, value: detail as unknown }
  })
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

async function onEffectiveVarUpdate(key: string, value: unknown) {
  if (!host.value) return
  const detail = effectiveVars.value?.vars_detail?.[key]
  if (detail?.source === 'group') {
    overrideConfirm.value = { key, value, group: detail.group ?? '' }
    return
  }
  await patch(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`, {
    vars: { ...host.value.vars, [key]: value },
  })
  refreshHost()
  refreshVars()
}

async function onEffectiveVarRemove(key: string) {
  if (!host.value) return
  const updatedVars = { ...host.value.vars }
  delete updatedVars[key]
  await patch(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`, { vars: updatedVars })
  refreshHost()
  refreshVars()
}

async function confirmOverride() {
  if (!overrideConfirm.value || !host.value) return
  await patch(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`, {
    vars: { ...host.value.vars, [overrideConfirm.value.key]: overrideConfirm.value.value },
  })
  overrideConfirm.value = null
  refreshHost()
  refreshVars()
}

function onSaved() {
  refreshHost()
  refreshVars()
}

async function deleteHost() {
  if (!host.value) return
  await del(`/workspaces/${auth.workspaceId}/hosts/${host.value.id}`)
  await navigateTo('/hosts')
}
</script>