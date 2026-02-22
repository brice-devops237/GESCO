/**
 * Requête authentifiée : token du store + retry après refresh sur 401.
 * Utilisé par les modules API (parametrage, catalogue, etc.) pour éviter les imports circulaires.
 */

import { doRequest } from './client'
import type { RequestConfig } from './client'
import { useAuthStore } from '@/stores/auth'

export async function authenticatedRequest<T>(
  path: string,
  config: RequestConfig = {},
): Promise<T> {
  const store = useAuthStore()
  try {
    const { data } = await doRequest<T>(path, { ...config, token: store.bearerToken })
    return data
  } catch (e: unknown) {
    const err = e as { status?: number }
    if (err?.status === 401) {
      if (store.refreshToken) {
        const ok = await store.refresh()
        if (ok) {
          const { data } = await doRequest<T>(path, { ...config, token: store.bearerToken })
          return data
        }
        // refresh() a déjà appelé logout() en cas d'échec
      } else {
        store.logout()
      }
    }
    throw e
  }
}
