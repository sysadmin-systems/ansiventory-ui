<template>
  <div class="border border-border rounded-lg overflow-hidden">
    <table class="w-full text-xs">
      <thead>
        <tr class="bg-bg-2 border-b border-border">
          <th class="text-left px-3 py-2 text-[10px] text-text-3 font-medium tracking-wide w-1/3">chave</th>
          <th class="text-left px-3 py-2 text-[10px] text-text-3 font-medium tracking-wide">valor</th>
          <th v-if="!readonly" class="w-16 px-2 py-2 text-[10px] text-text-3 font-medium text-right">ações</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="entry in vars"
          :key="entry.key"
          class="border-b border-border last:border-0 group"
          :class="editingKey === entry.key ? 'bg-bg-2' : 'hover:bg-bg-2'"
        >
          <td class="px-3 py-2 font-mono text-text-2 align-top">{{ entry.key }}</td>

          <!-- modo edição -->
          <td v-if="editingKey === entry.key" class="px-3 py-1.5 align-top" colspan="2">
            <div class="flex gap-2 items-start">
              <textarea
                v-model="editValue"
                class="input text-xs font-mono resize-y flex-1"
                style="min-height:32px"
                @keydown.escape="cancelEdit"
                @keydown.ctrl.enter="saveEdit(entry.key)"
              />
              <div class="flex flex-col gap-1 flex-shrink-0">
                <button class="btn btn-primary text-xs h-7 px-2" @click="saveEdit(entry.key)">
                  <i class="ti ti-check text-xs" />
                </button>
                <button class="btn text-xs h-7 px-2" @click="cancelEdit">
                  <i class="ti ti-x text-xs" />
                </button>
              </div>
            </div>
          </td>

          <!-- modo visualização -->
          <template v-else>
            <td class="px-3 py-2 align-top">
              <span v-if="isVault(entry.value)" class="vault-badge">
                <i class="ti ti-lock text-[10px]" />vault
              </span>
              <span v-else-if="entry.value === true" class="font-mono text-green-text">true</span>
              <span v-else-if="entry.value === false" class="font-mono text-text-3">false</span>
              <span v-else-if="entry.value === null" class="font-mono text-text-3">null</span>
              <span v-else-if="typeof entry.value === 'object'" class="font-mono text-text-2 text-[10px] break-all">
                {{ JSON.stringify(entry.value).slice(0, 120) }}{{ JSON.stringify(entry.value).length > 120 ? '...' : '' }}
              </span>
              <span v-else class="font-mono text-text-1 break-all">{{ entry.value }}</span>
            </td>
            <td v-if="!readonly" class="px-2 py-2 text-right align-top">
              <div class="flex gap-1 justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  class="w-6 h-6 rounded flex items-center justify-center text-text-3 hover:text-text-1 hover:bg-bg-3 transition-colors"
                  title="editar"
                  @click="startEdit(entry.key, entry.value)"
                >
                  <i class="ti ti-pencil text-xs" />
                </button>
                <button
                  class="w-6 h-6 rounded flex items-center justify-center text-text-3 hover:text-red-text hover:bg-red-bg transition-colors"
                  title="remover"
                  @click="$emit('remove', entry.key)"
                >
                  <i class="ti ti-trash text-xs" />
                </button>
              </div>
            </td>
          </template>
        </tr>

        <tr v-if="vars.length === 0">
          <td :colspan="readonly ? 2 : 3" class="px-3 py-6 text-center text-text-3">
            nenhuma variável
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  vars: { key: string; value: unknown }[]
  readonly?: boolean
}>()

const emit = defineEmits<{
  remove: [key: string]
  update: [key: string, value: unknown]
}>()

const editingKey = ref<string | null>(null)
const editValue = ref('')

function isVault(v: unknown): boolean {
  if (typeof v === 'object' && v !== null && '__ansible_vault' in v) return true
  if (typeof v === 'string' && v.startsWith('$ANSIBLE_VAULT')) return true
  return false
}

function startEdit(key: string, value: unknown) {
  editingKey.value = key
  if (typeof value === 'object' && value !== null) {
    editValue.value = JSON.stringify(value, null, 2)
  } else {
    editValue.value = String(value ?? '')
  }
}

function cancelEdit() {
  editingKey.value = null
  editValue.value = ''
}

function parseValue(v: string): unknown {
  if (v === 'true') return true
  if (v === 'false') return false
  if (v === 'null') return null
  if (!isNaN(Number(v)) && v.trim() !== '') return Number(v)
  try { return JSON.parse(v) } catch { return v }
}

function saveEdit(key: string) {
  emit('update', key, parseValue(editValue.value))
  cancelEdit()
}
</script>
