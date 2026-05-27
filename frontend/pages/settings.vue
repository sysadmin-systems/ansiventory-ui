<template>
  <div class="flex flex-col h-screen">
    <header class="h-12 bg-bg-1 border-b border-border flex items-center px-4 flex-shrink-0">
      <span class="text-sm font-semibold text-text-1">settings</span>
    </header>

    <div class="flex-1 overflow-y-auto p-4 max-w-2xl">

      <!-- workspace info -->
      <div class="card p-4 mb-4">
        <div class="text-xs font-semibold text-text-2 uppercase tracking-wide mb-3">workspace</div>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-bg border border-blue flex items-center justify-center flex-shrink-0">
            <i class="ti ti-layers-intersect text-blue-text text-lg" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-text-1">{{ workspace?.name }}</div>
            <div class="text-xs text-text-3 mt-0.5 font-mono">{{ workspace?.slug }}</div>
          </div>
          <div class="text-right">
            <div class="text-[10px] text-text-3">hosts</div>
            <div class="text-sm font-semibold text-blue-text">{{ hostCount }}</div>
          </div>
          <div class="text-right">
            <div class="text-[10px] text-text-3">grupos</div>
            <div class="text-sm font-semibold text-blue-text">{{ grupoCount }}</div>
          </div>
        </div>
      </div>

      <!-- tokens de API -->
      <div class="card p-4 mb-4">
        <div class="flex items-center justify-between mb-3">
          <div class="text-xs font-semibold text-text-2 uppercase tracking-wide">tokens de api</div>
          <button class="btn btn-primary text-xs h-7" @click="showNewToken = true">
            <i class="ti ti-plus text-xs" /> novo token
          </button>
        </div>

        <div v-if="tokens?.length === 0" class="text-xs text-text-3 py-3 text-center">
          nenhum token cadastrado
        </div>

        <div v-for="t in tokens" :key="t.id" class="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
          <div class="w-7 h-7 rounded-lg bg-bg-2 border border-border flex items-center justify-center flex-shrink-0">
            <i class="ti ti-key text-text-3 text-sm" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xs font-medium text-text-1">{{ t.descricao }}</div>
            <div class="text-[10px] text-text-3 mt-0.5">criado {{ formatDate(t.created_at) }}</div>
          </div>
          <button
            class="btn btn-ghost h-7 w-7 p-0 justify-center hover:text-red-text hover:bg-red-bg"
            @click="deleteToken(t.id)"
          >
            <i class="ti ti-trash text-xs" />
          </button>
        </div>
      </div>

      <!-- logo -->
      <div class="card p-4 mb-4">
        <div class="text-xs font-semibold text-text-2 uppercase tracking-wide mb-3">logo</div>
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-xl bg-bg-2 border border-border flex items-center justify-center flex-shrink-0">
            <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-12 h-12 object-contain rounded-lg" />
            <i v-else class="ti ti-server-2 text-text-3 text-2xl" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="btn text-xs cursor-pointer">
              <i class="ti ti-photo-up text-xs" /> upload logo
              <input type="file" accept="image/png,image/svg+xml" class="hidden" @change="onLogoUpload" />
            </label>
            <button v-if="logoUrl" class="btn btn-danger text-xs h-7" @click="removeLogo">
              <i class="ti ti-trash text-xs" /> remover
            </button>
            <span class="text-[10px] text-text-3">PNG ou SVG · 128×128px · máx 200kb</span>
          </div>
        </div>
      </div>

      <!-- inventário -->
      <div class="card p-4">
        <div class="text-xs font-semibold text-text-2 uppercase tracking-wide mb-3">inventário ansible</div>
        <div class="text-xs text-text-2 mb-3">
          Use este script no seu <span class="font-mono text-text-1">ansible.cfg</span> para consumir o inventário dinâmico:
        </div>
        <div class="bg-bg-0 border border-border rounded-lg p-3 font-mono text-[10px] text-text-2 leading-relaxed">
          <div class="text-green-text mb-1">#!/usr/bin/env python3</div>
          <div>import urllib.request, os, sys</div>
          <div class="mt-1">url = "http://localhost:8000/inventory/{{ auth.workspace }}"</div>
          <div>token = os.environ["ANSIVENTORY_TOKEN"]</div>
          <div class="mt-1">req = urllib.request.Request(url, headers={"Authorization": f"Bearer {'{token}'}"})</div>
          <div>with urllib.request.urlopen(req) as r:</div>
          <div>&nbsp;&nbsp;&nbsp;&nbsp;print(r.read().decode())</div>
        </div>
        <button class="btn text-xs mt-2" @click="copyScript">
          <i class="ti ti-copy text-xs" /> {{ copiedScript ? 'copiado!' : 'copiar script' }}
        </button>
      </div>

    </div>

    <!-- modal novo token -->
    <div v-if="showNewToken" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background:rgba(0,0,0,0.6)">
      <div class="bg-bg-1 border border-border rounded-xl w-full max-w-md">
        <div class="flex items-center justify-between px-5 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">novo token de api</span>
          <button class="btn btn-ghost h-7 w-7 p-0 justify-center" @click="closeNewToken">
            <i class="ti ti-x text-sm" />
          </button>
        </div>

        <!-- form -->
        <div v-if="!newTokenResult" class="p-5">
          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">descrição</label>
          <input v-model="newTokenDesc" type="text" placeholder="ex: script inventario local" class="input text-xs" />
        </div>

        <!-- resultado — mostra UMA VEZ -->
        <div v-else class="p-5">
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-lg bg-amber-bg border border-amber flex items-center justify-center">
              <i class="ti ti-alert-triangle text-amber-text text-sm" />
            </div>
            <span class="text-sm font-semibold text-amber-text">guarde este token agora</span>
          </div>
          <p class="text-xs text-text-2 mb-3">Este token não será exibido novamente. Copie e guarde em local seguro.</p>
          <div class="bg-bg-0 border border-amber rounded-lg p-3 font-mono text-xs text-text-1 break-all">
            {{ newTokenResult }}
          </div>
          <button class="btn btn-primary w-full justify-center mt-3 text-xs" @click="copyToken">
            <i class="ti ti-copy text-xs" /> {{ copiedToken ? 'copiado!' : 'copiar token' }}
          </button>
        </div>

        <div class="flex justify-end gap-2 px-5 py-4 border-t border-border">
          <button v-if="!newTokenResult" class="btn text-xs" @click="closeNewToken">cancelar</button>
          <button v-if="!newTokenResult" class="btn btn-primary text-xs" :disabled="!newTokenDesc.trim() || saving" @click="createToken">
            <i v-if="saving" class="ti ti-loader-2 animate-spin text-xs" />
            <i v-else class="ti ti-plus text-xs" />
            gerar token
          </button>
          <button v-else class="btn btn-primary text-xs" @click="closeNewToken">
            <i class="ti ti-check text-xs" /> já guardei
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const auth = useAuthStore()
const { get, post, del } = useApi()

const showNewToken = ref(false)
const newTokenDesc = ref('')
const newTokenResult = ref<string | null>(null)
const saving = ref(false)
const copiedToken = ref(false)
const copiedScript = ref(false)
const logoUrl = ref<string | null>(null)

onMounted(() => {
  logoUrl.value = localStorage.getItem('ansiventory_logo')
})

interface TokenOut {
  id: number
  descricao: string | null
  created_at: string
  expires_at: string | null
}

interface WorkspaceOut {
  id: number
  slug: string
  name: string
  created_at: string
}

// estado local para evitar problemas com useAsyncData e workspaceId tardio
const workspace = ref<WorkspaceOut | null>(null)
const hostCount = ref(0)
const grupoCount = ref(0)
const tokens = ref<TokenOut[]>([])

async function loadAll() {
  if (!auth.workspaceId) return
  const [ws, hosts, grupos, tks] = await Promise.all([
    get<WorkspaceOut[]>('/workspaces'),
    get<any[]>(`/workspaces/${auth.workspaceId}/hosts`),
    get<any[]>(`/workspaces/${auth.workspaceId}/grupos`),
    get<TokenOut[]>(`/workspaces/${auth.workspaceId}/tokens`),
  ])
  workspace.value = ws.find(w => w.id === auth.workspaceId) ?? null
  hostCount.value = hosts.length
  grupoCount.value = grupos.length
  tokens.value = tks
}

async function refresh() {
  await loadAll()
}

onMounted(() => { if (auth.workspaceId) loadAll() })
watch(() => auth.workspaceId, (id) => { if (id) loadAll() }, { immediate: true })

function formatDate(d: string) {
  return new Date(d).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

async function createToken() {
  if (!newTokenDesc.value.trim()) return
  saving.value = true
  try {
    const res = await post<{ token: string }>(`/workspaces/${auth.workspaceId}/tokens`, {
      descricao: newTokenDesc.value.trim(),
    })
    newTokenResult.value = res.token
    await refresh()
  } finally {
    saving.value = false
  }
}

async function deleteToken(id: number) {
  await del(`/workspaces/${auth.workspaceId}/tokens/${id}`)
  await refresh()
}

function closeNewToken() {
  showNewToken.value = false
  newTokenDesc.value = ''
  newTokenResult.value = null
}

async function copyToken() {
  if (!newTokenResult.value) return
  await navigator.clipboard.writeText(newTokenResult.value)
  copiedToken.value = true
  setTimeout(() => (copiedToken.value = false), 2000)
}

async function copyScript() {
  const script = `#!/usr/bin/env python3
import urllib.request, os, sys

url = "http://localhost:8000/inventory/${auth.workspace}"
token = os.environ["ANSIVENTORY_TOKEN"]

req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req) as r:
    print(r.read().decode())`
  await navigator.clipboard.writeText(script)
  copiedScript.value = true
  setTimeout(() => (copiedScript.value = false), 2000)
}

function onLogoUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 200 * 1024) { alert('Arquivo muito grande. Máximo 200kb.'); return }
  const reader = new FileReader()
  reader.onload = (ev) => {
    const result = ev.target?.result as string
    logoUrl.value = result
    localStorage.setItem('ansiventory_logo', result)
  }
  reader.readAsDataURL(file)
}

function removeLogo() {
  logoUrl.value = null
  localStorage.removeItem('ansiventory_logo')
}
</script>
