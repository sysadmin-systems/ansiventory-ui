<template>
  <div class="min-h-screen bg-bg-0 flex items-center justify-center p-4">
    <div class="w-full max-w-3xl bg-bg-1 border border-border rounded-xl overflow-hidden flex" style="min-height:480px">

      <!-- esquerda: branding -->
      <div class="w-5/12 bg-bg-2 border-r border-border flex flex-col items-center justify-center gap-6 p-8">
        <div class="flex flex-col items-center gap-4">
          <div class="w-16 h-16 rounded-xl bg-blue-bg border border-blue flex items-center justify-center">
            <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-12 h-12 object-contain rounded-lg" />
            <i v-else class="ti ti-server-2 text-blue text-3xl" />
          </div>
          <div class="text-center">
            <h1 class="text-xl font-semibold text-text-1">Ansiventory</h1>
            <p class="text-xs text-text-2 mt-1">inventário dinâmico Ansible</p>
          </div>
        </div>

        <div class="w-full border-t border-border pt-5 flex flex-col items-center gap-3">
          <label
            class="w-20 h-20 rounded-xl bg-bg-1 border-2 border-dashed border-border-2 flex flex-col items-center justify-center gap-1.5 cursor-pointer hover:border-blue transition-colors group"
            title="Upload de logo"
          >
            <i class="ti ti-photo-up text-2xl text-text-3 group-hover:text-blue transition-colors" />
            <span class="text-[10px] text-text-3 group-hover:text-blue transition-colors">upload logo</span>
            <input type="file" accept="image/png,image/svg+xml" class="hidden" @change="onLogoUpload" />
          </label>
          <p class="text-[10px] text-text-3 text-center leading-relaxed">
            PNG ou SVG · 128×128px recomendado<br>máximo 200kb
          </p>
          <button v-if="logoUrl" class="text-[10px] text-red-text hover:underline" @click="removeLogo">
            remover logo
          </button>
        </div>
      </div>

      <!-- direita: form -->
      <div class="flex-1 flex items-center justify-center p-8">
        <div class="w-full max-w-xs">
          <h2 class="text-lg font-semibold text-text-1 mb-1">entrar</h2>
          <p class="text-xs text-text-2 mb-6">insira seu workspace e token de acesso</p>

          <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
            <div>
              <label class="text-[11px] text-text-2 block mb-1.5 font-medium tracking-wide">workspace</label>
              <input
                v-model="form.workspace"
                type="text"
                placeholder="tecnologica"
                class="input font-mono text-xs"
                autocomplete="off"
                required
              />
            </div>

            <div>
              <label class="text-[11px] text-text-2 block mb-1.5 font-medium tracking-wide">token de acesso</label>
              <div class="relative">
                <input
                  v-model="form.token"
                  :type="showToken ? 'text' : 'password'"
                  placeholder="••••••••••••••••••••••••••••••••"
                  class="input pr-10"
                  required
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-text-3 hover:text-text-2 transition-colors"
                  @click="showToken = !showToken"
                >
                  <i :class="`ti ${showToken ? 'ti-eye-off' : 'ti-eye'} text-sm`" />
                </button>
              </div>
            </div>

            <div v-if="auth.error" class="text-xs text-red-text bg-red-bg border border-red rounded px-3 py-2 flex items-center gap-2">
              <i class="ti ti-alert-circle text-sm" />
              {{ auth.error }}
            </div>

            <button
              type="submit"
              class="btn btn-primary w-full justify-center h-10 text-sm mt-1"
              :disabled="auth.loading"
            >
              <i v-if="auth.loading" class="ti ti-loader-2 animate-spin" />
              <span>{{ auth.loading ? 'entrando...' : 'entrar' }}</span>
              <i v-if="!auth.loading" class="ti ti-arrow-right" />
            </button>
          </form>

          <p class="text-[11px] text-text-3 text-center mt-5 leading-relaxed">
            token gerado com<br>
            <code class="font-mono text-text-2 text-[10px]">openssl rand -hex 32</code>
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const auth = useAuthStore()
const form = reactive({ workspace: '', token: '' })
const showToken = ref(false)
const logoUrl = ref<string | null>(null)

onMounted(() => {
  logoUrl.value = localStorage.getItem('ansiventory_logo')
})

async function handleLogin() {
  await auth.login(form.workspace, form.token)
}

function onLogoUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 200 * 1024) {
    alert('Arquivo muito grande. Máximo 200kb.')
    return
  }
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
