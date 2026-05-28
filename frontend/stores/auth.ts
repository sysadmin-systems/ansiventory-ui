import { defineStore } from 'pinia'

interface Session {
  workspace: string
  workspace_id: number
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    session: null as Session | null,
    loading: false,
    checking: true,
    initialized: false,
    error: null as string | null,
  }),

  getters: {
    isAuthenticated: (s) => !!s.session,
    workspaceId: (s) => s.session?.workspace_id,
    workspace: (s) => s.session?.workspace,
  },

  actions: {
    async login(workspace: string, token: string) {
      const { post } = useApi()
      this.loading = true
      this.error = null
      try {
        this.session = await post<Session>('/auth/login', { workspace, token })
        await navigateTo('/hosts')
      } catch (e: any) {
        this.error = e.message || 'Erro ao autenticar'
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      // Pula se já foi verificado — o estado SSR é hidratado no cliente,
      // evitando uma chamada desnecessária em cada navegação SPA.
      if (this.initialized) return

      const { get } = useApi()
      this.checking = true
      try {
        this.session = await get<Session>('/auth/me')
      } catch {
        this.session = null
      } finally {
        this.checking = false
        this.initialized = true
      }
    },

    async logout() {
      const { post } = useApi()
      await post('/auth/logout', {}).catch(() => {})
      this.session = null
      await navigateTo('/login')
    },
  },
})
