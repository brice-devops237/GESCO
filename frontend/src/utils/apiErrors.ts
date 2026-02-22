/**
 * Extrait un message d'erreur lisible depuis une réponse API (detail string ou liste de validation).
 */
export function getApiErrorMessage(err: unknown): string {
  if (err && typeof err === 'object' && 'data' in err) {
    const data = (err as { data?: unknown }).data
    if (data && typeof data === 'object' && 'detail' in data) {
      const d = (data as { detail?: unknown }).detail
      if (typeof d === 'string')
        return d
      if (Array.isArray(d) && d.length > 0)
        return d.map((x: { msg?: string }) => x?.msg).filter(Boolean).join(', ')
    }
  }
  return err instanceof Error ? err.message : 'Échec de la connexion.'
}
