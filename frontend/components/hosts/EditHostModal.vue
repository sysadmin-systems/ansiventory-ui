<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
    <div class="bg-bg-1 border border-border rounded-xl w-full max-w-lg flex flex-col max-h-[90vh]">

      <!-- header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-border flex-shrink-0">
        <span class="text-sm font-semibold text-text-1">editar host</span>
        <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="$emit('close')">
          <i class="ti ti-x text-sm" />
        </button>
      </div>

      <!-- body -->
      <div class="overflow-y-auto p-5 flex flex-col gap-4">

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">hostname</label>
            <input v-model="form.hostname" type="text" class="input text-xs font-mono" />
          </div>
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">ip address</label>
            <input v-model="form.ip_address" type="text" placeholder="0.0.0.0" class="input text-xs font-mono" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">município</label>
            <input v-model="form.municipio" type="text" class="input text-xs" />
          </div>
          <div>
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">ambiente</label>
            <select v-model="form.ambiente" class="input text-xs">
              <option value="">—</option>
              <option value="azure">azure</option>
              <option value="onprem">onprem</option>
              <option value="digitalocean">digitalocean</option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <label class="text-[11px] text-text-2 font-medium">ativo</label>
          <button
            class="w-10 h-5 rounded-full relative transition-colors"
            :class="form.ativo ? 'bg-green' : 'bg-bg-3'"
            @click="form.ativo = !form.ativo"
          >
            <span
              class="absolute top-0.5 w-4 h-4 rounded-full bg-text-1 transition-all"
              :class="form.ativo ? 'left-5' : 'left-0.5'"
            />
          </button>
          <span class="text-xs" :class="form.ativo ? 'text-green-text' : 'text-text-3'">
            {{ form.ativo ? 'ativo' : 'inativo' }}
          </span>
        </div>

        <div>
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">grupos</label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span
              v-for="g in form.grupo_ids"
              :key="g"
              class="tag flex items-center gap-1"
            >
              {{ grupoNome(g) }}
              <button class="hover:text-red-text transition-colors" @click="removeGrupo(g)">
                <i class="ti ti-x text-[10px]" />
              </button>
            </span>
          </div>
          <select class="input text-xs" @change="addGrupo($event)">
            <option value="">+ adicionar grupo</option>
            <option
              v-for="g in availableGrupos"
              :key="g.id"
              :value="g.id"
            >{{ g.nome }}</option>
          </select>
        </div>

      </div>

      <!-- footer -->
      <div class="flex justify-end gap-2 px-5 py-4 border-t border-border flex-shrink-0">
        <button class="btn text-xs" @click="$emit('close')">cancelar</button>
        <button class="btn btn-primary text-xs" :disabled="saving" @click="save">
          <i v-if="saving" class="ti ti-loader-2 animate-spin text-xs" />
          <i v-else class="ti ti-check text-xs" />
          {{ saving ? 'salvando...' : 'salvar' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Host, Grupo } from '~/types'

const props = defineProps<{
  host: Host
  grupos: Grupo[]
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const { patch } = useApi()
const auth = useAuthStore()
const saving = ref(false)

const form = reactive({
  hostname: props.host.hostname,
  ip_address: props.host.ip_address ?? '',
  municipio: props.host.municipio ?? '',
  ambiente: props.host.ambiente ?? '',
  ativo: props.host.ativo,
  grupo_ids: props.host.grupos
    .map(nome => props.grupos.find(g => g.nome === nome)?.id)
    .filter(Boolean) as number[],
})

const availableGrupos = computed(() =>
  props.grupos.filter(g => !form.grupo_ids.includes(g.id))
)

function grupoNome(id: number) {
  return props.grupos.find(g => g.id === id)?.nome ?? String(id)
}

function addGrupo(e: Event) {
  const id = Number((e.target as HTMLSelectElement).value)
  if (id && !form.grupo_ids.includes(id)) form.grupo_ids.push(id)
  ;(e.target as HTMLSelectElement).value = ''
}

function removeGrupo(id: number) {
  form.grupo_ids = form.grupo_ids.filter(g => g !== id)
}

async function save() {
  saving.value = true
  try {
    await patch(`/workspaces/${auth.workspaceId}/hosts/${props.host.id}`, {
      hostname: form.hostname,
      ip_address: form.ip_address || null,
      municipio: form.municipio || null,
      ambiente: form.ambiente || null,
      ativo: form.ativo,
      grupo_ids: form.grupo_ids,
    })
    emit('saved')
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>
