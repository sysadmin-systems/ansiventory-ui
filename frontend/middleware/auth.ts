export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (to.path === '/login') {
    auth.checking = false
    return
  }

  await auth.fetchMe()

  if (!auth.isAuthenticated) {
    if (import.meta.client) {
      // Hard redirect: garante recarga completa e SSR limpo do login.
      // navigateTo() client-side trocaria o layout mid-hydration e quebraria a tela.
      window.location.replace('/login')
      return abortNavigation()
    }
    // No servidor: redirect HTTP normal; o browser nunca vê o conteúdo protegido.
    return navigateTo('/login')
  }
})