/**
 * API Paie – alignée sur le backend (Bearer requis).
 * Périodes de paie, Types d'éléments de paie, Bulletins (dont détail avec lignes).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  PeriodePaieCreate,
  PeriodePaieUpdate,
  PeriodePaieResponse,
  TypeElementPaieCreate,
  TypeElementPaieUpdate,
  TypeElementPaieResponse,
  BulletinPaieCreate,
  BulletinPaieUpdate,
  BulletinPaieResponse,
  BulletinPaieDetailResponse,
} from './types/paie'

const PREFIX = '/api/v1/paie'

// --- Périodes de paie ---
export interface ListPeriodesPaieParams {
  entreprise_id: number
  cloturee?: boolean | null
  skip?: number
  limit?: number
}
export function listPeriodesPaie(params: ListPeriodesPaieParams): Promise<PeriodePaieResponse[]> {
  return authenticatedRequest<PeriodePaieResponse[]>(`${PREFIX}/periodes${toQuery(params)}`)
}
export function getPeriodePaie(id: number): Promise<PeriodePaieResponse> {
  return authenticatedRequest<PeriodePaieResponse>(`${PREFIX}/periodes/${id}`)
}
export function createPeriodePaie(body: PeriodePaieCreate): Promise<PeriodePaieResponse> {
  return authenticatedRequest<PeriodePaieResponse>(`${PREFIX}/periodes`, { method: 'POST', body })
}
export function updatePeriodePaie(id: number, body: PeriodePaieUpdate): Promise<PeriodePaieResponse> {
  return authenticatedRequest<PeriodePaieResponse>(`${PREFIX}/periodes/${id}`, { method: 'PATCH', body })
}

// --- Types d'éléments de paie ---
export interface ListTypesElementPaieParams {
  entreprise_id: number
  actif_only?: boolean
  type_filter?: string | null
  skip?: number
  limit?: number
}
export function listTypesElementPaie(params: ListTypesElementPaieParams): Promise<TypeElementPaieResponse[]> {
  return authenticatedRequest<TypeElementPaieResponse[]>(`${PREFIX}/types-element${toQuery(params)}`)
}
export function getTypeElementPaie(id: number): Promise<TypeElementPaieResponse> {
  return authenticatedRequest<TypeElementPaieResponse>(`${PREFIX}/types-element/${id}`)
}
export function createTypeElementPaie(body: TypeElementPaieCreate): Promise<TypeElementPaieResponse> {
  return authenticatedRequest<TypeElementPaieResponse>(`${PREFIX}/types-element`, { method: 'POST', body })
}
export function updateTypeElementPaie(id: number, body: TypeElementPaieUpdate): Promise<TypeElementPaieResponse> {
  return authenticatedRequest<TypeElementPaieResponse>(`${PREFIX}/types-element/${id}`, { method: 'PATCH', body })
}

// --- Bulletins de paie ---
export interface ListBulletinsPaieParams {
  entreprise_id: number
  employe_id?: number | null
  periode_paie_id?: number | null
  statut?: string | null
  skip?: number
  limit?: number
}
export function listBulletinsPaie(params: ListBulletinsPaieParams): Promise<BulletinPaieResponse[]> {
  return authenticatedRequest<BulletinPaieResponse[]>(`${PREFIX}/bulletins${toQuery(params)}`)
}
export function getBulletinPaie(id: number): Promise<BulletinPaieResponse> {
  return authenticatedRequest<BulletinPaieResponse>(`${PREFIX}/bulletins/${id}`)
}
export function getBulletinPaieDetail(id: number): Promise<BulletinPaieDetailResponse> {
  return authenticatedRequest<BulletinPaieDetailResponse>(`${PREFIX}/bulletins/${id}/detail`)
}
export function createBulletinPaie(body: BulletinPaieCreate): Promise<BulletinPaieResponse> {
  return authenticatedRequest<BulletinPaieResponse>(`${PREFIX}/bulletins`, { method: 'POST', body })
}
export function updateBulletinPaie(id: number, body: BulletinPaieUpdate): Promise<BulletinPaieResponse> {
  return authenticatedRequest<BulletinPaieResponse>(`${PREFIX}/bulletins/${id}`, { method: 'PATCH', body })
}
