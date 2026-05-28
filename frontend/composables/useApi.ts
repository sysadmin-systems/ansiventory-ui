export function useApi() {
  const config = useRuntimeConfig()

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    // No SSR usa URL absoluta do backend; no cliente usa o proxy /api do Nitro.
    const baseURL = import.meta.server ? config.public.apiBase : '/api'

    const extraHeaders: Record<string, string> = {}

    // Repassa o cookie do browser para o backend quando rodando server-side,
    // permitindo que o middleware de autenticação funcione no SSR.
    if (import.meta.server) {
      const { cookie } = useRequestHeaders(['cookie'])
      if (cookie) extraHeaders['Cookie'] = cookie
    }

    const res = await fetch(`${baseURL}${path}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...extraHeaders,
        ...(options.headers as Record<string, string>),
      },
    })

    if (res.status === 401) {
      if (import.meta.client) await navigateTo('/login')
      throw new Error('Não autenticado')
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    if (res.status === 204) return undefined as T
    return res.json()
  }

  return {
    get:   <T>(path: string)                => request<T>(path),
    post:  <T>(path: string, body: unknown) => request<T>(path, { method: 'POST',   body: JSON.stringify(body) }),
    patch: <T>(path: string, body: unknown) => request<T>(path, { method: 'PATCH',  body: JSON.stringify(body) }),
    del:   (path: string)                   => request<void>(path, { method: 'DELETE' }),
  }
}
