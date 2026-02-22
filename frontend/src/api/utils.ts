/**
 * Utilitaires API (query string, etc.). Sans dépendance sur index pour éviter les imports circulaires.
 */

export function toQuery(params: object): string {
  const search = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === null || v === undefined || v === '') continue
    search.set(k, String(v))
  }
  const q = search.toString()
  return q ? `?${q}` : ''
}
