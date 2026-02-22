/**
 * API Immobilisations – alignée sur le backend (Bearer requis).
 * Catégories, Actifs, Lignes d'amortissement.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  CategorieImmobilisationCreate,
  CategorieImmobilisationUpdate,
  CategorieImmobilisationResponse,
  ImmobilisationCreate,
  ImmobilisationUpdate,
  ImmobilisationResponse,
  LigneAmortissementResponse,
} from './types/immobilisations'

const PREFIX = '/api/v1/immobilisations'

// --- Catégories ---
export interface ListCategoriesImmobilisationsParams {
  entreprise_id: number
  skip?: number
  limit?: number
}
export function listCategoriesImmobilisations(params: ListCategoriesImmobilisationsParams): Promise<CategorieImmobilisationResponse[]> {
  return authenticatedRequest<CategorieImmobilisationResponse[]>(`${PREFIX}/categories${toQuery(params)}`)
}
export function getCategorieImmobilisation(id: number): Promise<CategorieImmobilisationResponse> {
  return authenticatedRequest<CategorieImmobilisationResponse>(`${PREFIX}/categories/${id}`)
}
export function createCategorieImmobilisation(body: CategorieImmobilisationCreate): Promise<CategorieImmobilisationResponse> {
  return authenticatedRequest<CategorieImmobilisationResponse>(`${PREFIX}/categories`, { method: 'POST', body })
}
export function updateCategorieImmobilisation(id: number, body: CategorieImmobilisationUpdate): Promise<CategorieImmobilisationResponse> {
  return authenticatedRequest<CategorieImmobilisationResponse>(`${PREFIX}/categories/${id}`, { method: 'PATCH', body })
}

// --- Actifs (immobilisations) ---
export interface ListImmobilisationsParams {
  entreprise_id: number
  categorie_id?: number | null
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listImmobilisations(params: ListImmobilisationsParams): Promise<ImmobilisationResponse[]> {
  return authenticatedRequest<ImmobilisationResponse[]>(`${PREFIX}/actifs${toQuery(params)}`)
}
export function getImmobilisation(id: number): Promise<ImmobilisationResponse> {
  return authenticatedRequest<ImmobilisationResponse>(`${PREFIX}/actifs/${id}`)
}
export function createImmobilisation(body: ImmobilisationCreate): Promise<ImmobilisationResponse> {
  return authenticatedRequest<ImmobilisationResponse>(`${PREFIX}/actifs`, { method: 'POST', body })
}
export function updateImmobilisation(id: number, body: ImmobilisationUpdate): Promise<ImmobilisationResponse> {
  return authenticatedRequest<ImmobilisationResponse>(`${PREFIX}/actifs/${id}`, { method: 'PATCH', body })
}

// --- Lignes d'amortissement ---
export interface ListLignesAmortissementParams {
  skip?: number
  limit?: number
}
export function listLignesAmortissement(actifId: number, params: ListLignesAmortissementParams = {}): Promise<LigneAmortissementResponse[]> {
  return authenticatedRequest<LigneAmortissementResponse[]>(`${PREFIX}/actifs/${actifId}/lignes-amortissement${toQuery(params)}`)
}
