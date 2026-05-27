<template>
  <div class="flex flex-col h-screen">
    <header class="h-12 bg-bg-1 border-b border-border flex items-center px-4 flex-shrink-0">
      <span class="text-sm font-semibold text-text-1">vault tool</span>
      <span class="text-xs text-text-2 ml-3">criptografe e descriptografe variáveis ansible-vault</span>
    </header>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="grid grid-cols-2 gap-4 max-w-4xl">

        <!-- criptografar -->
        <div class="card p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-7 h-7 rounded-lg bg-amber-bg border border-amber flex items-center justify-center">
              <i class="ti ti-lock text-amber-text text-sm" />
            </div>
            <span class="text-sm font-semibold text-text-1">criptografar</span>
          </div>

          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">valor em plaintext</label>
          <textarea v-model="enc.input" placeholder="minha_senha_secreta" class="input font-mono text-xs resize-y min-h-[80px]" />

          <div class="grid grid-cols-2 gap-2 mt-3">
            <div>
              <label class="text-[11px] text-text-2 block mb-1.5 font-medium">vault id</label>
              <input v-model="enc.vaultId" type="text" placeholder="default" class="input text-xs font-mono h-8" />
            </div>
            <div>
              <label class="text-[11px] text-text-2 block mb-1.5 font-medium">vault password</label>
              <div class="relative">
                <input v-model="enc.password" :type="showEncPassword ? 'text' : 'password'" placeholder="••••••••" class="input text-xs h-8 pr-8" />
                <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 text-text-3 hover:text-text-2" @click="showEncPassword = !showEncPassword">
                  <i :class="`ti ${showEncPassword ? 'ti-eye-off' : 'ti-eye'} text-xs`" />
                </button>
              </div>
            </div>
          </div>

          <button class="btn btn-primary w-full justify-center mt-3" :disabled="!enc.input.trim() || !enc.password.trim()" @click="encrypt">
            <i class="ti ti-lock" /> criptografar
          </button>

          <div v-if="enc.error" class="mt-3 text-xs text-red-text bg-red-bg border border-red rounded-lg px-3 py-2">
            {{ enc.error }}
          </div>

          <div v-if="enc.output" class="mt-3">
            <div class="bg-bg-0 border border-border rounded-lg p-3 font-mono text-[10px] text-text-2 break-all leading-relaxed min-h-[60px]">{{ enc.output }}</div>
            <button class="btn w-full justify-center mt-2 text-xs" @click="copy(enc.output, 'enc')">
              <i class="ti ti-copy text-xs" /> {{ copied === 'enc' ? 'copiado!' : 'copiar resultado' }}
            </button>
          </div>
        </div>

        <!-- descriptografar -->
        <div class="card p-4">
          <div class="flex items-center gap-2.5 mb-4">
            <div class="w-7 h-7 rounded-lg bg-green-bg border border-green flex items-center justify-center">
              <i class="ti ti-lock-open text-green-text text-sm" />
            </div>
            <span class="text-sm font-semibold text-text-1">descriptografar</span>
          </div>

          <label class="text-[11px] text-text-2 block mb-1.5 font-medium">valor vault</label>
          <textarea v-model="dec.input" placeholder="$ANSIBLE_VAULT;1.1;AES256&#10;3836313631363364..." class="input font-mono text-[10px] resize-y min-h-[80px]" />

          <div class="mt-3">
            <label class="text-[11px] text-text-2 block mb-1.5 font-medium">vault password</label>
            <div class="relative">
              <input v-model="dec.password" :type="showDecPassword ? 'text' : 'password'" placeholder="••••••••" class="input text-xs h-8 pr-8" />
              <button type="button" class="absolute right-2 top-1/2 -translate-y-1/2 text-text-3 hover:text-text-2" @click="showDecPassword = !showDecPassword">
                <i :class="`ti ${showDecPassword ? 'ti-eye-off' : 'ti-eye'} text-xs`" />
              </button>
            </div>
          </div>

          <button class="btn btn-success w-full justify-center mt-3" :disabled="!dec.input.trim() || !dec.password.trim()" @click="decrypt">
            <i class="ti ti-lock-open" /> descriptografar
          </button>

          <div v-if="dec.error" class="mt-3 text-xs text-red-text bg-red-bg border border-red rounded-lg px-3 py-2">
            {{ dec.error }}
          </div>

          <div v-if="dec.output !== null" class="mt-3">
            <div class="bg-bg-0 border border-border rounded-lg p-3 font-mono text-xs text-green-text break-all leading-relaxed min-h-[60px]">{{ dec.output }}</div>
            <button class="btn w-full justify-center mt-2 text-xs" @click="copy(dec.output!, 'dec')">
              <i class="ti ti-copy text-xs" /> {{ copied === 'dec' ? 'copiado!' : 'copiar resultado' }}
            </button>
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
const copied = ref<'enc' | 'dec' | null>(null)

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
</script>
