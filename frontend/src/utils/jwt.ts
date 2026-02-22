/**
 * Décodage du payload JWT (côté client, affichage uniquement).
 * Le backend signe et valide les tokens ; ici on lit seulement sub / entreprise_id pour l'UI.
 */

export interface JwtPayload {
  sub?: string
  entreprise_id?: number
  exp?: number
  [key: string]: unknown
}

/**
 * Décode le payload (partie centrale) d'un JWT sans vérification.
 * Retourne null si le token est invalide ou mal formé.
 */
export function decodeJwtPayload(token: string | null | undefined): JwtPayload | null {
  if (!token || typeof token !== 'string')
    return null
  const parts = token.trim().split('.')
  if (parts.length !== 3)
    return null
  try {
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = atob(base64)
    return JSON.parse(json) as JwtPayload
  } catch {
    return null
  }
}

/**
 * Retourne true si le token est expiré (exp en secondes).
 */
export function isJwtExpired(token: string | null | undefined): boolean {
  const payload = decodeJwtPayload(token)
  if (!payload?.exp)
    return true
  const now = Math.floor(Date.now() / 1000)
  return payload.exp < now
}
