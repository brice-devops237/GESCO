/**
 * Client HTTP pour l'API Gesco.
 * - Base URL depuis VITE_API_URL
 * - En-tête Authorization Bearer si token fourni
 * - Gestion 401 : tentative de refresh puis retry (optionnel, utilisé par le store)
 */

const getBaseUrl = (): string => {
  const url = import.meta.env.VITE_API_URL
  if (typeof url === 'string' && url.length > 0)
    return url.replace(/\/$/, '')
  // En dev sans .env : défaut vers le backend local (évite 404 sur localhost:5173)
  if (import.meta.env.DEV)
    return 'http://localhost:9111'
  return ''
}

export function getApiBaseUrl(): string {
  return getBaseUrl()
}

export type RequestConfig = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
  /** Token à utiliser (sinon pas d'Authorization) */
  token?: string | null
}

async function doRequest<T>(
  path: string,
  config: RequestConfig = {},
): Promise<{ data: T; status: number }> {
  const base = getBaseUrl()
  const url = path.startsWith('http') ? path : `${base}${path.startsWith('/') ? path : `/${path}`}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...config.headers,
  }
  if (config.token)
    headers.Authorization = `Bearer ${config.token}`

  const init: RequestInit = {
    method: config.method ?? 'GET',
    headers,
  }
  if (config.body !== undefined && config.body !== null)
    init.body = JSON.stringify(config.body)

  const res = await fetch(url, init)
  let data: T
  const contentType = res.headers.get('content-type')
  if (contentType?.includes('application/json')) {
    const text = await res.text()
    data = (text ? JSON.parse(text) : null) as T
  } else {
    data = null as T
  }

  if (!res.ok) {
    const err = new Error((data as { detail?: string })?.detail ?? res.statusText) as Error & { status: number; data?: unknown }
    err.status = res.status
    err.data = data
    throw err
  }

  return { data, status: res.status }
}

/**
 * Effectue une requête vers l'API.
 * Pour les appels authentifiés, passer le token dans config.token (géré par le store).
 */
export async function apiRequest<T>(
  path: string,
  config: RequestConfig = {},
): Promise<T> {
  const { data } = await doRequest<T>(path, config)
  return data
}

export { doRequest }
