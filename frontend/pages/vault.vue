<template>
  <div class="flex flex-col h-screen">

    <header class="h-14 bg-bg-1 border-b border-border flex items-center px-6 gap-4 flex-shrink-0">
      <div class="w-8 h-8 rounded-lg bg-amber/10 border border-amber/20 flex items-center justify-center flex-shrink-0">
        <i class="ti ti-lock text-amber-text text-sm" />
      </div>
      <div>
        <h1 class="text-sm font-semibold text-text-1 leading-none">Vault Tool</h1>
        <p class="text-[11px] text-text-3 mt-0.5">Criptografe e descriptografe variáveis Ansible Vault</p>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="grid grid-cols-2 gap-6 max-w-4xl">

        <!-- encrypt -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-4 border-b border-border flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber/10 border border-amber/20 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-lock text-amber-text text-sm" />
            </div>
            <div>
              <div class="text-sm font-semibold text-text-1">Criptografar</div>
              <div class="text-[11px] text-text-3">Plaintext → Ansible Vault</div>
            </div>
          </div>
          <div class="p-5 flex flex-col gap-4">
            <div>
              <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Valor em plaintext</label>
              <textarea v-model="enc.input" placeholder="minha_senha_secreta" class="input font-mono text-sm resize-y min-h-[80px]" />
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Vault ID</label>
                <input v-model="enc.vaultId" type="text" placeholder="default" class="input font-mono text-sm" />
              </div>
              <div>
                <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Senha</label>
                <div class="relative">
                  <input v-model="enc.password" :type="showEncPassword ? 'text' : 'password'" placeholder="••••••••" class="input text-sm pr-9" />
                  <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-text-3 hover:text-text-2 transition-colors" @click="showEncPassword = !showEncPassword">
                    <i :class="`ti ${showEncPassword ? 'ti-eye-off' : 'ti-eye'} text-sm`" />
                  </button>
                </div>
              </div>
            </div>

            <button
              class="btn btn-primary w-full justify-center gap-2"
              :disabled="!enc.input.trim() || !enc.password.trim()"
              @click="encrypt"
            >
              <i class="ti ti-lock text-sm" /> Criptografar
            </button>

            <div v-if="enc.error" class="flex items-start gap-2.5 text-xs text-red-text bg-red/10 border border-red/30 rounded-lg px-4 py-3">
              <i class="ti ti-alert-circle text-base flex-shrink-0 mt-0.5" /> {{ enc.error }}
            </div>

            <div v-if="enc.output">
              <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Resultado</label>
              <div class="bg-bg-0 border border-border rounded-lg p-3 font-mono text-[11px] text-amber-text break-all leading-relaxed min-h-[60px] whitespace-pre-wrap">{{ enc.output }}</div>
              <div class="flex flex-col gap-2 mt-2">
                <button class="btn w-full justify-center gap-2 text-sm" @click="copy(enc.output, 'enc')">
                  <i class="ti ti-copy text-sm" />
                  {{ copied === 'enc' ? 'Copiado!' : 'Copiar resultado' }}
                </button>
                <button class="btn w-full justify-center gap-2 text-sm border-amber/30 text-amber-text hover:bg-amber/10" @click="copyVaultJson(enc.output)">
                  <i class="ti ti-braces text-sm" />
                  {{ copied === 'enc-json' ? 'Copiado!' : 'Copiar como __ansible_vault' }}
                </button>
              </div>
              <div class="mt-3 bg-bg-0 border border-amber/20 rounded-lg p-3">
                <div class="text-[10px] font-semibold text-text-3 uppercase tracking-wide mb-1.5">Prévia — pronto para colar no campo vars</div>
                <div class="font-mono text-[10px] text-text-2 break-all leading-relaxed">{{ vaultJsonPreview(enc.output) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- decrypt -->
        <div class="glass-card overflow-hidden">
          <div class="px-5 py-4 border-b border-border flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-green/10 border border-green/20 flex items-center justify-center flex-shrink-0">
              <i class="ti ti-lock-open text-green-text text-sm" />
            </div>
            <div>
              <div class="text-sm font-semibold text-text-1">Descriptografar</div>
              <div class="text-[11px] text-text-3">Ansible Vault → Plaintext</div>
            </div>
          </div>
          <div class="p-5 flex flex-col gap-4">
            <div>
              <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Valor vault</label>
              <textarea v-model="dec.input" placeholder="$ANSIBLE_VAULT;1.1;AES256&#10;3836313631363364..." class="input font-mono text-[11px] resize-y min-h-[80px]" />
            </div>

            <div>
              <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Senha</label>
              <div class="relative">
                <input v-model="dec.password" :type="showDecPassword ? 'text' : 'password'" placeholder="••••••••" class="input text-sm pr-9" />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-text-3 hover:text-text-2 transition-colors" @click="showDecPassword = !showDecPassword">
                  <i :class="`ti ${showDecPassword ? 'ti-eye-off' : 'ti-eye'} text-sm`" />
                </button>
              </div>
            </div>

            <button
              class="btn btn-success w-full justify-center gap-2"
              :disabled="!dec.input.trim() || !dec.password.trim()"
              @click="decrypt"
            >
              <i class="ti ti-lock-open text-sm" /> Descriptografar
            </button>

            <div v-if="dec.error" class="flex items-start gap-2.5 text-xs text-red-text bg-red/10 border border-red/30 rounded-lg px-4 py-3">
              <i class="ti ti-alert-circle text-base flex-shrink-0 mt-0.5" /> {{ dec.error }}
            </div>

            <div v-if="dec.output !== null">
              <label class="text-xs font-semibold text-text-2 block mb-2 uppercase tracking-wide">Resultado</label>
              <div class="bg-bg-0 border border-green/20 rounded-lg p-3 font-mono text-sm text-green-text break-all leading-relaxed min-h-[60px]">{{ dec.output }}</div>
              <button class="btn w-full justify-center mt-2 gap-2 text-sm" @click="copy(dec.output!, 'dec')">
                <i class="ti ti-copy text-sm" />
                {{ copied === 'dec' ? 'Copiado!' : 'Copiar resultado' }}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
const { post } = useApi()

const enc = reactive({ input: '', vaultId: 'default', password: '', output: '', error: '' })
const dec = reactive({ input: '', password: '', output: null as string | null, error: '' })
const showEncPassword = ref(false)
const showDecPassword = ref(false)
const copied = ref<'enc' | 'dec' | 'enc-json' | null>(null)

async function encrypt() {
  enc.error = ''
  enc.output = ''
  try {
    const res = await post<{ result: string }>('/vault/encrypt', {
      value: enc.input,
      vault_id: enc.vaultId,
      password: enc.password,
    })
    enc.output = res.result
  } catch (e: any) {
    enc.error = e.message
  }
}

async function decrypt() {
  dec.error = ''
  dec.output = null
  try {
    const res = await post<{ result: string }>('/vault/decrypt', {
      encrypted: dec.input,
      password: dec.password,
    })
    dec.output = res.result
  } catch (e: any) {
    dec.error = e.message
  }
}

async function copy(text: string, which: 'enc' | 'dec') {
  await navigator.clipboard.writeText(text)
  copied.value = which
  setTimeout(() => (copied.value = null), 2000)
}

// Converte o output do vault para o formato __ansible_vault que o campo vars espera.
// JSON.stringify já converte quebras reais em \n no JSON — sem replace manual,
// que causaria \\n duplo e quebraria a decifragem no Ansible.
function toVaultJson(vaultStr: string): string {
  return JSON.stringify({ __ansible_vault: vaultStr.replace(/\r\n/g, '\n') }, null, 2)
}

function vaultJsonPreview(vaultStr: string): string {
  return toVaultJson(vaultStr)
}

async function copyVaultJson(vaultStr: string) {
  await navigator.clipboard.writeText(toVaultJson(vaultStr))
  copied.value = 'enc-json'
  setTimeout(() => (copied.value = null), 2000)
}
</script>
