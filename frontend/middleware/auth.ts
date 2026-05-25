export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/login') return

  // só executa no cliente — evita SSR sem cookie
  if (import.meta.server) return

  const auth = useAuthStore()

  if (!auth.isAuthenticated) {
    await auth.fetchMe()
    if (!auth.isAuthenticated) {
      return navigateTo('/login')
    }
  }
})
