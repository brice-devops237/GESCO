/**
 * API Comptabilité – alignée sur le backend (Bearer requis).
 * Comptes comptables, Journaux, Périodes, Écritures (détail avec lignes).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  CompteComptableCreate,
  CompteComptableUpdate,
  CompteComptableResponse,
  JournalComptableCreate,
  JournalComptableUpdate,
  JournalComptableResponse,
  PeriodeComptableCreate,
  PeriodeComptableUpdate,
  PeriodeComptableResponse,
  EcritureComptableCreate,
  EcritureComptableResponse,
  EcritureComptableDetailResponse,
} from './types/comptabilite'

const PREFIX = '/api/v1/comptabilite'

// --- Comptes comptables ---
export interface ListComptesComptablesParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}

export function listComptesComptables(params: ListComptesComptablesParams): Promise<CompteComptableResponse[]> {
  return authenticatedRequest<CompteComptableResponse[]>(`${PREFIX}/comptes${toQuery(params)}`)
}

export function getCompteComptable(id: number): Promise<CompteComptableResponse> {
  return authenticatedRequest<CompteComptableResponse>(`${PREFIX}/comptes/${id}`)
}

export function createCompteComptable(body: CompteComptableCreate): Promise<CompteComptableResponse> {
  return authenticatedRequest<CompteComptableResponse>(`${PREFIX}/comptes`, { method: 'POST', body })
}

export function updateCompteComptable(id: number, body: CompteComptableUpdate): Promise<CompteComptableResponse> {
  return authenticatedRequest<CompteComptableResponse>(`${PREFIX}/comptes/${id}`, { method: 'PATCH', body })
}

// --- Journaux comptables ---
export interface ListJournauxComptablesParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}

export function listJournauxComptables(params: ListJournauxComptablesParams): Promise<JournalComptableResponse[]> {
  return authenticatedRequest<JournalComptableResponse[]>(`${PREFIX}/journaux${toQuery(params)}`)
}

export function getJournalComptable(id: number): Promise<JournalComptableResponse> {
  return authenticatedRequest<JournalComptableResponse>(`${PREFIX}/journaux/${id}`)
}

export function createJournalComptable(body: JournalComptableCreate): Promise<JournalComptableResponse> {
  return authenticatedRequest<JournalComptableResponse>(`${PREFIX}/journaux`, { method: 'POST', body })
}

export function updateJournalComptable(id: number, body: JournalComptableUpdate): Promise<JournalComptableResponse> {
  return authenticatedRequest<JournalComptableResponse>(`${PREFIX}/journaux/${id}`, { method: 'PATCH', body })
}

// --- Périodes comptables ---
export interface ListPeriodesComptablesParams {
  entreprise_id: number
  skip?: number
  limit?: number
}

export function listPeriodesComptables(params: ListPeriodesComptablesParams): Promise<PeriodeComptableResponse[]> {
  return authenticatedRequest<PeriodeComptableResponse[]>(`${PREFIX}/periodes${toQuery(params)}`)
}

export function getPeriodeComptable(id: number): Promise<PeriodeComptableResponse> {
  return authenticatedRequest<PeriodeComptableResponse>(`${PREFIX}/periodes/${id}`)
}

export function createPeriodeComptable(body: PeriodeComptableCreate): Promise<PeriodeComptableResponse> {
  return authenticatedRequest<PeriodeComptableResponse>(`${PREFIX}/periodes`, { method: 'POST', body })
}

export function updatePeriodeComptable(id: number, body: PeriodeComptableUpdate): Promise<PeriodeComptableResponse> {
  return authenticatedRequest<PeriodeComptableResponse>(`${PREFIX}/periodes/${id}`, { method: 'PATCH', body })
}

// --- Écritures comptables ---
export interface ListEcrituresComptablesParams {
  entreprise_id: number
  journal_id?: number | null
  periode_id?: number | null
  date_from?: string | null
  date_to?: string | null
  skip?: number
  limit?: number
}

export function listEcrituresComptables(params: ListEcrituresComptablesParams): Promise<EcritureComptableResponse[]> {
  return authenticatedRequest<EcritureComptableResponse[]>(`${PREFIX}/ecritures${toQuery(params)}`)
}

export function getEcritureComptable(id: number): Promise<EcritureComptableDetailResponse> {
  return authenticatedRequest<EcritureComptableDetailResponse>(`${PREFIX}/ecritures/${id}`)
}

export function createEcritureComptable(body: EcritureComptableCreate): Promise<EcritureComptableResponse> {
  return authenticatedRequest<EcritureComptableResponse>(`${PREFIX}/ecritures`, { method: 'POST', body })
}
