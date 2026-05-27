<template>
  <div class="flex h-screen">

    <!-- sidebar de grupos -->
    <div class="w-56 bg-bg-1 border-r border-border flex flex-col flex-shrink-0">
      <div class="h-12 border-b border-border flex items-center px-4 gap-2 flex-shrink-0">
        <span class="text-sm font-semibold text-text-1">grupos</span>
        <div class="flex-1" />
        <button class="btn btn-primary text-xs h-7 px-2" @click="showNewGrupo = true">
          <i class="ti ti-plus text-xs" />
        </button>
      </div>
      <div class="flex-1 overflow-y-auto p-2">
        <button
          v-for="g in grupos"
          :key="g.id"
          class="w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between gap-2 mb-0.5"
          :class="selectedId === g.id ? 'bg-blue-bg text-blue-text' : 'text-text-2 hover:bg-bg-2 hover:text-text-1'"
          @click="selectedId = g.id"
        >
          <span class="font-mono text-xs truncate">{{ g.nome }}</span>
          <span class="text-[10px] opacity-60 flex-shrink-0">{{ Object.keys(g.vars).length }} vars</span>
        </button>
      </div>
    </div>

    <!-- conteúdo -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <div v-if="!selected" class="flex-1 flex items-center justify-center text-text-3 text-sm gap-2">
        <i class="ti ti-arrow-left text-xl" /> selecione um grupo
      </div>

      <template v-else>
        <div class="h-12 bg-bg-1 border-b border-border flex items-center px-4 gap-3 flex-shrink-0">
          <span class="font-mono text-sm font-semibold text-text-1">{{ selected.nome }}</span>
          <span class="text-[11px] text-text-3">{{ Object.keys(selected.vars).length }} variáveis</span>
          <div class="flex-1" />
          <button class="btn text-xs h-7" @click="showEditGrupo = true"><i class="ti ti-edit text-xs" /> renomear</button>
          <button class="btn btn-danger text-xs h-7" @click="confirmDelete = true"><i class="ti ti-trash text-xs" /></button>
        </div>

        <div class="px-4 py-2.5 border-b border-border bg-bg-0 flex items-center gap-2 flex-wrap flex-shrink-0">
          <span class="text-[11px] text-text-3 mr-1">hosts:</span>
          <span
            v-for="h in membros" :key="h.id"
            class="tag font-mono cursor-pointer hover:text-text-1 transition-colors"
            @click="navigateTo(`/hosts/${h.id}`)"
          >{{ h.hostname }}</span>
          <span v-if="membros.length === 0" class="text-[11px] text-text-3">nenhum host</span>
        </div>

        <div class="flex-1 overflow-y-auto p-4">
          <div class="flex items-center justify-between mb-3">
            <span class="text-[11px] text-text-3">variáveis do grupo · aplicadas a todos os hosts membros</span>
            <button class="btn btn-primary text-xs h-7" @click="showAddVar = true">
              <i class="ti ti-plus text-xs" /> add var
            </button>
          </div>
          <UiVarsTable :vars="varEntries" @update="onVarUpdate" @remove="onVarRemove" />
        </div>
      </template>
    </div>

    <!-- modal novo grupo -->
    <div v-if="showNewGrupo" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
      <div class="bg-bg-1 border border-border rounded-xl w-full max-w-sm">
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">novo grupo</span>
          <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="showNewGrupo = false"><i class="ti ti-x text-sm" /></button>
        </div>
        <div class="p-5">
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">nome do grupo</label>
          <input v-model="newGrupoNome" type="text" placeholder="linux_webservers" class="input text-xs font-mono" />
          <div v-if="newGrupoError" class="mt-2 text-xs text-red-text">{{ newGrupoError }}</div>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button class="btn text-xs" @click="showNewGrupo = false">cancelar</button>
          <button class="btn btn-primary text-xs" :disabled="savingGrupo" @click="createGrupo">
            <i v-if="savingGrupo" class="ti ti-loader-2 animate-spin text-xs" /><i v-else class="ti ti-plus text-xs" /> criar
          </button>
        </div>
      </div>
    </div>

    <!-- modal renomear -->
    <div v-if="showEditGrupo && selected" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
      <div class="bg-bg-1 border border-border rounded-xl w-full max-w-sm">
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">renomear grupo</span>
          <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="showEditGrupo = false"><i class="ti ti-x text-sm" /></button>
        </div>
        <div class="p-5">
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">novo nome</label>
          <input v-model="editGrupoNome" type="text" class="input text-xs font-mono" />
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button class="btn text-xs" @click="showEditGrupo = false">cancelar</button>
          <button class="btn btn-primary text-xs" @click="renameGrupo"><i class="ti ti-check text-xs" /> salvar</button>
        </div>
      </div>
    </div>

    <!-- modal add var -->
    <div v-if="showAddVar" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
      <div class="bg-bg-1 border border-border rounded-xl w-full max-w-md">
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">adicionar variável</span>
          <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="showAddVar = false"><i class="ti ti-x text-sm" /></button>
        </div>
        <div class="p-5 flex flex-col gap-4">
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">chave</label>
            <input v-model="newVarKey" type="text" placeholder="nome_da_variavel" class="input text-xs font-mono" />
          </div>
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">valor</label>
            <textarea v-model="newVarValue" class="input text-xs font-mono resize-y min-h-[80px]" />
          </div>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button class="btn text-xs" @click="showAddVar = false">cancelar</button>
          <button class="btn btn-primary text-xs" :disabled="!newVarKey.trim()" @click="addVar">
            <i class="ti ti-plus text-xs" /> adicionar
          </button>
        </div>
      </div>
    </div>

    <!-- confirmação delete -->
    <div v-if="confirmDelete" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
      <div class="bg-bg-1 border border-border rounded-xl w-full max-w-sm">
        <div class="p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-9 h-9 rounded-lg bg-red-bg border border-red flex items-center justify-center flex-shrink-0">
              <i class="ti ti-trash text-red-text" />
            </div>
            <div>
              <div class="text-sm font-semibold text-text-1">excluir grupo</div>
              <div class="text-xs text-text-2 mt-0.5">esta ação não pode ser desfeita</div>
            </div>
          </div>
          <p class="text-xs text-text-2">
            Tem certeza que deseja excluir o grupo
            <span class="font-mono text-text-1">{{ selected?.nome }}</span>?
            Os hosts não serão afetados.
          </p>
        </div>
        <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button class="btn text-xs" @click="confirmDelete = false">cancelar</button>
          <button class="btn btn-danger text-xs" @click="deleteGrupo"><i class="ti ti-trash text-xs" /> excluir</button>
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

const { data: grupos, refresh: refreshGrupos } = useAsyncData(
  'grupos-page',
  async () => {
    if (!auth.workspaceId) return [] as Grupo[]
    return get<Grupo[]>(`/workspaces/${auth.workspaceId}/grupos`)
  },
  { default: () => [] as Grupo[] }
)

const { data: allHosts } = useAsyncData(
  'hosts-for-grupos',
  async () => {
    if (!auth.workspaceId) return [] as Host[]
    return get<Host[]>(`/workspaces/${auth.workspaceId}/hosts`)
  },
  { default: () => [] as Host[] }
)

onMounted(() => { if (auth.workspaceId) refreshGrupos() })
watch(() => auth.workspaceId, (id) => { if (id) refreshGrupos() }, { immediate: true })

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
