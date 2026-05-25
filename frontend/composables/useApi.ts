export function useApi() {
  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`/api${path}`, {
      ...options,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...options.headers },
    })
    if (res.status === 401) {
      await navigateTo('/login')
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
