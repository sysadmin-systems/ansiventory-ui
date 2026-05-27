<template>
  <div class="flex flex-col h-screen">

    <header class="h-14 bg-bg-1 border-b border-border flex items-center px-6 gap-4 flex-shrink-0">
      <div class="w-8 h-8 rounded-lg bg-blue/10 border border-blue/20 flex items-center justify-center flex-shrink-0">
        <i class="ti ti-settings text-blue-text text-sm" />
      </div>
      <div>
        <h1 class="text-sm font-semibold text-text-1 leading-none">Configurações</h1>
        <p class="text-[11px] text-text-3 mt-0.5">Workspace, tokens e preferências</p>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl flex flex-col gap-5">

        <!-- workspace info -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center gap-2">
            <i class="ti ti-layers-intersect text-blue-text text-sm" />
            <span class="text-xs font-semibold text-text-2 uppercase tracking-widest">Workspace</span>
          </div>
          <div class="p-5">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-blue/10 border border-blue/20 flex items-center justify-center flex-shrink-0">
                <i class="ti ti-layers-intersect text-blue-text text-xl" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-base font-semibold text-text-1">{{ workspace?.name }}</div>
                <div class="text-xs text-text-3 mt-0.5 font-mono">{{ workspace?.slug }}</div>
              </div>
              <div class="flex gap-6">
                <div class="text-center">
                  <div class="text-lg font-bold text-blue-text leading-none">{{ hostCount }}</div>
                  <div class="text-[10px] text-text-3 mt-1 uppercase tracking-wide">hosts</div>
                </div>
                <div class="text-center">
                  <div class="text-lg font-bold text-blue-text leading-none">{{ grupoCount }}</div>
                  <div class="text-[10px] text-text-3 mt-1 uppercase tracking-wide">grupos</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- api tokens -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center justify-between">
            <div class="flex items-center gap-2">
              <i class="ti ti-key text-blue-text text-sm" />
              <span class="text-xs font-semibold text-text-2 uppercase tracking-widest">Tokens de API</span>
            </div>
            <button class="btn btn-primary text-sm gap-2" @click="showNewToken = true">
              <i class="ti ti-plus text-sm" /> Novo token
            </button>
          </div>
          <div class="divide-y divide-border">
            <div v-if="tokens?.length === 0" class="flex flex-col items-center justify-center py-10 gap-3 text-text-3">
              <i class="ti ti-key text-2xl" />
              <span class="text-sm">Nenhum token cadastrado</span>
            </div>
            <div v-for="t in tokens" :key="t.id" class="flex items-center gap-4 px-5 py-3.5">
              <div class="w-8 h-8 rounded-lg bg-bg-3 border border-border flex items-center justify-center flex-shrink-0">
                <i class="ti ti-key text-text-3 text-sm" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-text-1">{{ t.descricao }}</div>
                <div class="text-[11px] text-text-3 mt-0.5">criado {{ formatDate(t.created_at) }}</div>
              </div>
              <button
                class="btn btn-ghost h-8 w-8 p-0 justify-center hover:text-red-text hover:bg-red/10"
                title="Revogar token"
                @click="deleteToken(t.id)"
              >
                <i class="ti ti-trash text-sm" />
              </button>
            </div>
          </div>
        </div>

        <!-- logo -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center gap-2">
            <i class="ti ti-photo text-blue-text text-sm" />
            <span class="text-xs font-semibold text-text-2 uppercase tracking-widest">Logo</span>
          </div>
          <div class="p-5 flex items-center gap-5">
            <div class="w-16 h-16 rounded-xl bg-bg-2 border border-border flex items-center justify-center flex-shrink-0">
              <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-12 h-12 object-contain rounded-lg" />
              <i v-else class="ti ti-server-2 text-text-3 text-2xl" />
            </div>
            <div class="flex flex-col gap-2">
              <label class="btn cursor-pointer gap-2">
                <i class="ti ti-photo-up text-sm" /> Fazer upload
                <input type="file" accept="image/png,image/svg+xml" class="hidden" @change="onLogoUpload" />
              </label>
              <button v-if="logoUrl" class="btn btn-danger gap-2" @click="removeLogo">
                <i class="ti ti-trash text-sm" /> Remover
              </button>
              <span class="text-[11px] text-text-3">PNG ou SVG · 128×128px · máx 200kb</span>
            </div>
          </div>
        </div>

        <!-- ansible inventory script -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-3.5 border-b border-border flex items-center gap-2">
            <i class="ti ti-terminal text-blue-text text-sm" />
            <span class="text-xs font-semibold text-text-2 uppercase tracking-widest">Script de inventário Ansible</span>
          </div>
          <div class="p-5">
            <p class="text-sm text-text-2 mb-4">
              Use este script no seu <code class="font-mono text-xs bg-bg-3 px-1.5 py-0.5 rounded text-text-1">ansible.cfg</code> para consumir o inventário dinâmico:
            </p>
            <div class="bg-bg-0 border border-border rounded-xl p-4 font-mono text-[11px] text-text-2 leading-relaxed">
              <div class="text-green-text">#!/usr/bin/env python3</div>
              <div class="mt-1">import urllib.request, os, sys</div>
              <div class="mt-2 text-blue-text">url = <span class="text-amber-text">"http://localhost:8000/inventory/{{ auth.workspace }}"</span></div>
              <div>token = os.environ[<span class="text-amber-text">"ANSIVENTORY_TOKEN"</span>]</div>
              <div class="mt-2">req = urllib.request.Request(url, headers={"Authorization": f"Bearer {'{token}'}"})</div>
              <div>with urllib.request.urlopen(req) as r:</div>
              <div>&nbsp;&nbsp;&nbsp;&nbsp;print(r.read().decode())</div>
            </div>
            <button class="btn mt-3 gap-2 text-sm" @click="copyScript">
              <i class="ti ti-copy text-sm" />
              {{ copiedScript ? 'Copiado!' : 'Copiar script' }}
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- modal novo token -->
    <div v-if="showNewToken" class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm" style="background:rgba(7,9,15,0.7)">
      <div class="glass-card w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-border">
          <span class="text-sm font-semibold text-text-1">Novo token de API</span>
          <button class="btn btn-ghost h-8 w-8 p-0 justify-center" @click="closeNewToken">
            <i class="ti ti-x text-sm" />
          </button>
        </div>

        <div v-if="!newTokenResult" class="p-6">
          <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Descrição</label>
          <input v-model="newTokenDesc" type="text" placeholder="ex: script inventário local" class="input" />
        </div>

        <div v-else class="p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-amber/10 border border-amber/30 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-alert-triangle text-amber-text text-lg" />
            </div>
            <div>
              <div class="text-sm font-semibold text-amber-text">Guarde este token agora</div>
              <div class="text-xs text-text-3 mt-0.5">Ele não será exibido novamente</div>
            </div>
          </div>
          <div class="bg-bg-0 border border-amber/30 rounded-xl p-4 font-mono text-sm text-text-1 break-all">
            {{ newTokenResult }}
          </div>
          <button class="btn btn-primary w-full justify-center mt-4 gap-2" @click="copyToken">
            <i class="ti ti-copy text-sm" />
            {{ copiedToken ? 'Copiado!' : 'Copiar token' }}
          </button>
        </div>

        <div class="flex justify-end gap-2 px-6 py-4 border-t border-border">
          <button v-if="!newTokenResult" class="btn" @click="closeNewToken">Cancelar</button>
          <button v-if="!newTokenResult" class="btn btn-primary" :disabled="!newTokenDesc.trim() || saving" @click="createToken">
            <i v-if="saving" class="ti ti-loader-2 animate-spin text-sm" />
            <i v-else class="ti ti-plus text-sm" />
            Gerar token
          </button>
          <button v-else class="btn btn-primary" @click="closeNewToken">
            <i class="ti ti-check text-sm" /> Já guardei
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
    await loadAll()
  } finally {
    saving.value = false
  }
}

async function deleteToken(id: number) {
  await del(`/workspaces/${auth.workspaceId}/tokens/${id}`)
  await loadAll()
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
