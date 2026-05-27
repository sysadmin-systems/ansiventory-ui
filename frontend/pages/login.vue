<template>
  <div class="min-h-screen relative flex items-center justify-center p-4 overflow-hidden">

    <!-- atmospheric background -->
    <div class="absolute inset-0 bg-bg-0" />
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[500px] rounded-full"
           style="background: radial-gradient(ellipse, rgba(124,92,252,0.12) 0%, transparent 70%)" />
      <div class="absolute bottom-0 left-0 w-[600px] h-[400px] rounded-full"
           style="background: radial-gradient(ellipse, rgba(61,184,122,0.06) 0%, transparent 70%)" />
      <div class="absolute top-1/2 right-0 w-[500px] h-[500px] rounded-full"
           style="background: radial-gradient(ellipse, rgba(124,92,252,0.07) 0%, transparent 70%)" />
    </div>

    <!-- card -->
    <div class="relative w-full max-w-sm glass-card shadow-glow overflow-hidden">

      <!-- header -->
      <div class="px-8 pt-10 pb-7 text-center">
        <div class="w-16 h-16 rounded-2xl bg-blue/15 border border-blue/40 flex items-center justify-center mx-auto mb-5 shadow-glow-sm">
          <img v-if="logoUrl" :src="logoUrl" alt="logo" class="w-12 h-12 object-contain rounded-xl" />
          <i v-else class="ti ti-server-2 text-blue-text text-[28px]" />
        </div>
        <h1 class="text-2xl font-bold text-text-1 tracking-tight">Ansiventory</h1>
        <p class="text-sm text-text-2 mt-1.5">inventário dinâmico Ansible</p>
      </div>

      <!-- divider -->
      <div class="h-px mx-6 bg-gradient-to-r from-transparent via-border to-transparent" />

      <!-- form -->
      <div class="px-8 py-8">
        <form class="flex flex-col gap-5" @submit.prevent="handleLogin">

          <div>
            <label class="text-xs font-semibold text-text-2 block mb-2 tracking-wide uppercase">Workspace</label>
            <input
              v-model="form.workspace"
              type="text"
              placeholder="tecnologica"
              class="input font-mono text-sm"
              autocomplete="off"
              required
            />
          </div>

          <div>
            <label class="text-xs font-semibold text-text-2 block mb-2 tracking-wide uppercase">Token de acesso</label>
            <div class="relative">
              <input
                v-model="form.token"
                :type="showToken ? 'text' : 'password'"
                placeholder="••••••••••••••••••••••"
                class="input pr-10 font-mono text-sm"
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

          <div v-if="auth.error" class="flex items-center gap-2.5 text-xs text-red-text bg-red/10 border border-red/30 rounded-lg px-4 py-3">
            <i class="ti ti-alert-circle text-base flex-shrink-0" />
            {{ auth.error }}
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full justify-center h-11 text-sm mt-1 font-semibold"
            :disabled="auth.loading"
          >
            <i v-if="auth.loading" class="ti ti-loader-2 animate-spin text-base" />
            <span>{{ auth.loading ? 'Entrando...' : 'Entrar' }}</span>
            <i v-if="!auth.loading" class="ti ti-arrow-right text-base" />
          </button>

        </form>
      </div>

      <!-- footer features -->
      <div class="h-px mx-6 bg-gradient-to-r from-transparent via-border to-transparent" />
      <div class="px-8 py-6 flex flex-col gap-2.5">
        <div class="flex items-center gap-2.5 text-xs text-text-3">
          <i class="ti ti-shield-check text-blue-text text-sm flex-shrink-0" />
          <span>Autenticação por token seguro</span>
        </div>
        <div class="flex items-center gap-2.5 text-xs text-text-3">
          <i class="ti ti-server text-blue-text text-sm flex-shrink-0" />
          <span>Inventário dinâmico para Ansible</span>
        </div>
        <div class="flex items-center gap-2.5 text-xs text-text-3">
          <i class="ti ti-cloud text-blue-text text-sm flex-shrink-0" />
          <span>Multi-cloud: Azure, onprem e mais</span>
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

</script>
