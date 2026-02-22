/**
 * API Trésorerie – alignée sur le backend (Bearer requis).
 * Modes de paiement, Comptes trésorerie, Règlements.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  ModePaiementCreate,
  ModePaiementUpdate,
  ModePaiementResponse,
  CompteTresorerieCreate,
  CompteTresorerieUpdate,
  CompteTresorerieResponse,
  ReglementCreate,
  ReglementResponse,
} from './types/tresorerie'

const PREFIX = '/api/v1/tresorerie'

// --- Modes de paiement ---
export interface ListModesPaiementParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}

export function listModesPaiement(params: ListModesPaiementParams): Promise<ModePaiementResponse[]> {
  return authenticatedRequest<ModePaiementResponse[]>(`${PREFIX}/modes-paiement${toQuery(params)}`)
}

export function getModePaiement(id: number): Promise<ModePaiementResponse> {
  return authenticatedRequest<ModePaiementResponse>(`${PREFIX}/modes-paiement/${id}`)
}

export function createModePaiement(body: ModePaiementCreate): Promise<ModePaiementResponse> {
  return authenticatedRequest<ModePaiementResponse>(`${PREFIX}/modes-paiement`, { method: 'POST', body })
}

export function updateModePaiement(id: number, body: ModePaiementUpdate): Promise<ModePaiementResponse> {
  return authenticatedRequest<ModePaiementResponse>(`${PREFIX}/modes-paiement/${id}`, { method: 'PATCH', body })
}

// --- Comptes trésorerie ---
export interface ListComptesTresorerieParams {
  entreprise_id: number
  actif_only?: boolean
  type_compte?: string | null
  skip?: number
  limit?: number
}

export function listComptesTresorerie(params: ListComptesTresorerieParams): Promise<CompteTresorerieResponse[]> {
  return authenticatedRequest<CompteTresorerieResponse[]>(`${PREFIX}/comptes${toQuery(params)}`)
}

export function getCompteTresorerie(id: number): Promise<CompteTresorerieResponse> {
  return authenticatedRequest<CompteTresorerieResponse>(`${PREFIX}/comptes/${id}`)
}

export function createCompteTresorerie(body: CompteTresorerieCreate): Promise<CompteTresorerieResponse> {
  return authenticatedRequest<CompteTresorerieResponse>(`${PREFIX}/comptes`, { method: 'POST', body })
}

export function updateCompteTresorerie(id: number, body: CompteTresorerieUpdate): Promise<CompteTresorerieResponse> {
  return authenticatedRequest<CompteTresorerieResponse>(`${PREFIX}/comptes/${id}`, { method: 'PATCH', body })
}

// --- Règlements ---
export interface ListReglementsParams {
  entreprise_id: number
  type_reglement?: string | null
  tiers_id?: number | null
  date_from?: string | null
  date_to?: string | null
  skip?: number
  limit?: number
}

export function listReglements(params: ListReglementsParams): Promise<ReglementResponse[]> {
  return authenticatedRequest<ReglementResponse[]>(`${PREFIX}/reglements${toQuery(params)}`)
}

export function getReglement(id: number): Promise<ReglementResponse> {
  return authenticatedRequest<ReglementResponse>(`${PREFIX}/reglements/${id}`)
}

export function createReglement(body: ReglementCreate): Promise<ReglementResponse> {
  return authenticatedRequest<ReglementResponse>(`${PREFIX}/reglements`, { method: 'POST', body })
}
