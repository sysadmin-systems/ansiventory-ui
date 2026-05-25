<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
    <div class="bg-bg-1 border border-border rounded-xl w-full max-w-md flex flex-col">

      <!-- header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-border">
        <span class="text-sm font-semibold text-text-1">adicionar variável</span>
        <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="$emit('close')">
          <i class="ti ti-x text-sm" />
        </button>
      </div>

      <!-- body -->
      <div class="p-5 flex flex-col gap-4">
        <div>
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">chave</label>
          <input
            v-model="form.key"
            type="text"
            placeholder="nome_da_variavel"
            class="input text-xs font-mono"
            @keydown.enter="$refs.valueInput.focus()"
          />
        </div>

        <div>
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">valor</label>
          <textarea
            ref="valueInput"
            v-model="form.value"
            placeholder="valor da variável"
            class="input text-xs font-mono resize-y min-h-[80px]"
          />
          <div class="flex gap-2 mt-2">
            <button
              v-for="type in quickTypes"
              :key="type.label"
              class="text-[10px] px-2 py-0.5 rounded border border-border text-text-3 hover:text-text-1 hover:border-border-2 transition-colors"
              @click="form.value = type.value"
            >{{ type.label }}</button>
          </div>
        </div>

        <div v-if="error" class="text-xs text-red-text bg-red-bg border border-red rounded px-3 py-2">
          {{ error }}
        </div>
      </div>

      <!-- footer -->
      <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
        <button class="btn text-xs" @click="$emit('close')">cancelar</button>
        <button class="btn btn-primary text-xs" :disabled="saving || !form.key.trim()" @click="save">
          <i v-if="saving" class="ti ti-loader-2 animate-spin text-xs" />
          <i v-else class="ti ti-plus text-xs" />
          {{ saving ? 'salvando...' : 'adicionar' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Host } from '~/types'

const props = defineProps<{ host: Host }>()
const emit = defineEmits<{ close: []; saved: [] }>()

const { patch } = useApi()
const auth = useAuthStore()
const saving = ref(false)
const error = ref('')

const form = reactive({ key: '', value: '' })

const quickTypes = [
  { label: 'true',  value: 'true' },
  { label: 'false', value: 'false' },
  { label: '""',    value: '""' },
]

function parseValue(v: string): unknown {
  if (v === 'true') return true
  if (v === 'false') return false
  if (v === 'null') return null
  if (!isNaN(Number(v)) && v !== '') return Number(v)
  try { return JSON.parse(v) } catch { return v }
}

async function save() {
  if (!form.key.trim()) return
  error.value = ''
  saving.value = true
  try {
    const updatedVars = {
      ...props.host.vars,
      [form.key.trim()]: parseValue(form.value),
    }
    await patch(`/workspaces/${auth.workspaceId}/hosts/${props.host.id}`, {
      vars: updatedVars,
    })
    emit('saved')
    emit('close')
  } catch (e: any) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
