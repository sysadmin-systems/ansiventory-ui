<template>
  <div class="flex h-screen">

    <!-- secondary sidebar: group list -->
    <div class="w-64 bg-bg-1 border-r border-border flex flex-col flex-shrink-0">
      <div class="px-4 py-4 border-b border-border flex-shrink-0">
        <div class="flex items-center justify-between mb-0.5">
          <h2 class="text-sm font-semibold text-text-1">Grupos</h2>
          <button class="btn btn-primary h-8 w-8 p-0 justify-center" title="Novo grupo" @click="showNewGrupo = true">
            <i class="ti ti-plus text-sm" />
          </button>
        </div>
        <p class="text-[11px] text-text-3">{{ grupos?.length ?? 0 }} grupos</p>
      </div>

      <div class="flex-1 overflow-y-auto p-2">
        <button
          v-for="g in grupos"
          :key="g.id"
          class="w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-center justify-between gap-2 mb-0.5 group"
          :class="selectedId === g.id
            ? 'bg-blue/10 text-blue-text border border-blue/20'
            : 'text-text-2 hover:bg-bg-2 hover:text-text-1 border border-transparent'"
          @click="selectedId = g.id"
        >
          <span class="font-mono text-xs truncate flex-1">{{ g.nome }}</span>
          <span
            class="text-[10px] px-1.5 py-0.5 rounded flex-shrink-0 font-medium"
            :class="selectedId === g.id ? 'bg-blue/20 text-blue-text' : 'bg-bg-3 text-text-3'"
          >
            {{ Object.keys(g.vars).length }}
          </span>
        </button>

        <div v-if="!grupos?.length" class="flex flex-col items-center justify-center py-10 gap-3">
          <i class="ti ti-sitemap text-2xl text-text-3" />
          <span class="text-xs text-text-3 text-center">Nenhum grupo criado</span>
        </div>
      </div>
    </div>

    <!-- main content -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- empty state -->
      <div v-if="!selected" class="flex-1 flex flex-col items-center justify-center gap-4 text-text-3">
        <div class="w-16 h-16 rounded-2xl bg-bg-2 border border-border flex items-center justify-center">
          <i class="ti ti-sitemap text-2xl" />
        </div>
        <div class="text-center">
          <p class="text-text-2 text-sm font-medium">Selecione um grupo</p>
          <p class="text-text-3 text-xs mt-1">Escolha um grupo na lista à esquerda</p>
        </div>
      </div>

      <template v-else>
        <!-- topbar -->
        <header class="h-14 bg-bg-1 border-b border-border flex items-center px-6 gap-4 flex-shrink-0">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div class="w-8 h-8 rounded-lg bg-blue/10 border border-blue/20 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-sitemap text-blue-text text-sm" />
            </div>
            <div class="min-w-0">
              <h1 class="text-sm font-semibold text-text-1 font-mono leading-none truncate">{{ selected.nome }}</h1>
              <p class="text-[11px] text-text-3 mt-0.5">{{ Object.keys(selected.vars).length }} variáveis</p>
            </div>
          </div>
          <button class="btn text-xs gap-2" @click="showEditGrupo = true">
            <i class="ti ti-edit text-sm" /> Renomear
          </button>
          <button class="btn btn-danger text-xs gap-2" @click="confirmDelete = true">
            <i class="ti ti-trash text-sm" />
          </button>
        </header>

        <!-- hosts members -->
        <div class="px-6 py-2.5 border-b border-border bg-bg-0 flex items-center gap-2 flex-wrap flex-shrink-0 min-h-[44px]">
          <span class="text-[11px] font-medium text-text-3 flex-shrink-0">
            <i class="ti ti-server text-[11px] mr-1" />hosts:
          </span>
          <span
            v-for="h in membros" :key="h.id"
            class="tag font-mono cursor-pointer"
            @click="navigateTo(`/hosts/${h.id}`)"
          >{{ h.hostname }}</span>
          <span v-if="membros.length === 0" class="text-[11px] text-text-3 italic">nenhum host neste grupo</span>
        </div>

        <!-- vars area -->
        <div class="flex-1 overflow-y-auto p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-sm font-medium text-text-1">Variáveis do grupo</p>
              <p class="text-xs text-text-3 mt-0.5">Aplicadas a todos os hosts membros</p>
            </div>
            <button class="btn btn-primary text-sm gap-2" @click="showAddVar = true">
              <i class="ti ti-plus text-sm" /> Adicionar var
            </button>
          </div>
          <UiVarsTable :vars="varEntries" @update="onVarUpdate" @remove="onVarRemove" />
        </div>
      </template>
    </div>

    <!-- modals -->
    <!-- novo grupo -->
    <div v-if="showNewGrupo" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-sm">
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">Novo grupo</span>
          <button class="btn btn-ghost h-8 w-8 p-0 justify-center" @click="showNewGrupo = false">
            <i class="ti ti-x text-sm" />
          </button>
        </div>
        <div class="p-6">
          <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Nome do grupo</label>
          <input v-model="newGrupoNome" type="text" placeholder="linux_webservers" class="input font-mono" />
          <div v-if="newGrupoError" class="mt-2 text-xs text-red-text flex items-center gap-1.5">
            <i class="ti ti-alert-circle text-sm" /> {{ newGrupoError }}
          </div>
        </div>
        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button class="btn" @click="showNewGrupo = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="savingGrupo" @click="createGrupo">
            <i v-if="savingGrupo" class="ti ti-loader-2 animate-spin" />
            <i v-else class="ti ti-plus" />
            Criar
          </button>
        </div>
      </div>
    </div>

    <!-- renomear -->
    <div v-if="showEditGrupo && selected" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-sm">
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">Renomear grupo</span>
          <button class="btn btn-ghost h-8 w-8 p-0 justify-center" @click="showEditGrupo = false">
            <i class="ti ti-x text-sm" />
          </button>
        </div>
        <div class="p-6">
          <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Novo nome</label>
          <input v-model="editGrupoNome" type="text" class="input font-mono" />
        </div>
        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button class="btn" @click="showEditGrupo = false">Cancelar</button>
          <button class="btn btn-primary" @click="renameGrupo">
            <i class="ti ti-check" /> Salvar
          </button>
        </div>
      </div>
    </div>

    <!-- add var -->
    <div v-if="showAddVar" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">Adicionar variável</span>
          <button class="btn btn-ghost h-8 w-8 p-0 justify-center" @click="showAddVar = false">
            <i class="ti ti-x text-sm" />
          </button>
        </div>
        <div class="p-6 flex flex-col gap-4">
          <div>
            <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Chave</label>
            <input v-model="newVarKey" type="text" placeholder="nome_da_variavel" class="input font-mono" />
          </div>
          <div>
            <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Valor</label>
            <textarea v-model="newVarValue" class="input font-mono resize-y min-h-[80px]" />
          </div>
        </div>
        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button class="btn" @click="showAddVar = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="!newVarKey.trim()" @click="addVar">
            <i class="ti ti-plus" /> Adicionar
          </button>
        </div>
      </div>
    </div>

    <!-- confirm delete -->
    <div v-if="confirmDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-sm">
        <div class="p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-red/10 border border-red/30 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-trash text-red-text text-lg" />
            </div>
            <div>
              <div class="text-sm font-semibold text-text-1">Excluir grupo</div>
              <div class="text-xs text-text-3 mt-0.5">Esta ação não pode ser desfeita</div>
            </div>
          </div>
          <p class="text-sm text-text-2">
            Confirma a exclusão do grupo
            <span class="font-mono text-text-1">{{ selected?.nome }}</span>?
            Os hosts não serão afetados.
          </p>
        </div>
        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button class="btn" @click="confirmDelete = false">Cancelar</button>
          <button class="btn btn-danger" @click="deleteGrupo">
            <i class="ti ti-trash" /> Excluir
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Grupo, Host } from '~/types'

definePageMeta({ middleware: 'auth' })

const auth = useAuthStore()
const { get, post, patch, del } = useApi()

const selectedId = ref<number | null>(null)
const showNewGrupo = ref(false)
const showEditGrupo = ref(false)
const showAddVar = ref(false)
const confirmDelete = ref(false)
const savingGrupo = ref(false)
const newGrupoNome = ref('')
const newGrupoError = ref('')
const editGrupoNome = ref('')
const newVarKey = ref('')
const newVarValue = ref('')

// usando ref + fetch direto para evitar cache do useAsyncData com workspaceId tardio
const grupos = ref<Grupo[]>([])
const allHosts = ref<Host[]>([])

async function loadData() {
  if (!auth.workspaceId) return
  const [g, h] = await Promise.all([
    get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`),
    get<Host[]>(`/workspaces/${auth.workspaceId}/hosts`),
  ])
  grupos.value = g
  allHosts.value = h
}

async function refreshGrupos() {
  if (!auth.workspaceId) return
  grupos.value = await get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`)
}

onMounted(() => loadData())
watch(() => auth.workspaceId, (id) => { if (id) loadData() })

const selected = computed(() => grupos.value?.find(g => g.id === selectedId.value) ?? null)
watch(selected, (g) => { if (g) editGrupoNome.value = g.nome })

const membros = computed(() =>
  (allHosts.value ?? []).filter(h => h.grupos.includes(selected.value?.nome ?? ''))
)

const varEntries = computed(() =>
  Object.entries(selected.value?.vars ?? {}).map(([key, value]) => ({ key, value }))
)

function parseValue(v: string): unknown {
  if (v === 'true') return true
  if (v === 'false') return false
  if (v === 'null') return null
  if (!isNaN(Number(v)) && v.trim() !== '') return Number(v)
  try { return JSON.parse(v) } catch { return v }
}

async function onVarUpdate(key: string, value: unknown) {
  if (!selected.value) return
  await patch(`/workspaces/${auth.workspaceId}/grupos/${selected.value.id}`, {
    vars: { ...selected.value.vars, [key]: value }
  })
  await refreshGrupos()
}

async function onVarRemove(key: string) {
  if (!selected.value) return
  const vars = { ...selected.value.vars }
  delete vars[key]
  await patch(`/workspaces/${auth.workspaceId}/grupos/${selected.value.id}`, { vars })
  await refreshGrupos()
}

async function addVar() {
  if (!selected.value || !newVarKey.value.trim()) return
  const vars = { ...selected.value.vars, [newVarKey.value.trim()]: parseValue(newVarValue.value) }
  await patch(`/workspaces/${auth.workspaceId}/grupos/${selected.value.id}`, { vars })
  newVarKey.value = ''
  newVarValue.value = ''
  showAddVar.value = false
  await refreshGrupos()
}

async function createGrupo() {
  if (!newGrupoNome.value.trim()) return
  newGrupoError.value = ''
  savingGrupo.value = true
  try {
    const g = await post<Grupo>(`/workspaces/${auth.workspaceId}/grupos`, {
      nome: newGrupoNome.value.trim(), vars: {},
    })
    await refreshGrupos()
    selectedId.value = g.id
    newGrupoNome.value = ''
    showNewGrupo.value = false
  } catch (e: any) {
    newGrupoError.value = e.message
  } finally {
    savingGrupo.value = false
  }
}

async function renameGrupo() {
  if (!selected.value || !editGrupoNome.value.trim()) return
  await patch(`/workspaces/${auth.workspaceId}/grupos/${selected.value.id}`, { nome: editGrupoNome.value.trim() })
  await refreshGrupos()
  showEditGrupo.value = false
}

async function deleteGrupo() {
  if (!selected.value) return
  await del(`/workspaces/${auth.workspaceId}/grupos/${selected.value.id}`)
  await refreshGrupos()
  selectedId.value = null
  confirmDelete.value = false
}
</script>