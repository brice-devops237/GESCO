/**
 * API Partenaires – alignée sur le backend (Bearer requis).
 * Référentiel : Types de tiers (Client, Fournisseur, etc.).
 * Tiers : partenaires avec identification légale (NIU, RCCM), adresse, conditions commerciales, moyens de paiement.
 * Contacts : interlocuteurs rattachés à un tiers (civilité, fonction, contact principal).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  TypeTiersCreate,
  TypeTiersUpdate,
  TypeTiersResponse,
  TiersCreate,
  TiersUpdate,
  TiersResponse,
  ContactCreate,
  ContactUpdate,
  ContactResponse,
} from './types/partenaires'

const PREFIX = '/api/v1/partenaires'

// --- Types de tiers ---
export interface ListTypesTiersParams {
  skip?: number
  limit?: number
}

export function listTypesTiers(params: ListTypesTiersParams = {}): Promise<TypeTiersResponse[]> {
  return authenticatedRequest<TypeTiersResponse[]>(`${PREFIX}/types-tiers${toQuery(params)}`)
}

export function getTypeTiers(id: number): Promise<TypeTiersResponse> {
  return authenticatedRequest<TypeTiersResponse>(`${PREFIX}/types-tiers/${id}`)
}

export function createTypeTiers(body: TypeTiersCreate): Promise<TypeTiersResponse> {
  return authenticatedRequest<TypeTiersResponse>(`${PREFIX}/types-tiers`, { method: 'POST', body })
}

export function updateTypeTiers(id: number, body: TypeTiersUpdate): Promise<TypeTiersResponse> {
  return authenticatedRequest<TypeTiersResponse>(`${PREFIX}/types-tiers/${id}`, { method: 'PATCH', body })
}

export function deleteTypeTiers(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/types-tiers/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Tiers ---
export interface ListTiersParams {
  entreprise_id: number
  type_tiers_id?: number | null
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export function listTiers(params: ListTiersParams): Promise<TiersResponse[]> {
  return authenticatedRequest<TiersResponse[]>(`${PREFIX}/tiers${toQuery(params)}`)
}

export function getTiers(id: number): Promise<TiersResponse> {
  return authenticatedRequest<TiersResponse>(`${PREFIX}/tiers/${id}`)
}

export function createTiers(body: TiersCreate): Promise<TiersResponse> {
  return authenticatedRequest<TiersResponse>(`${PREFIX}/tiers`, { method: 'POST', body })
}

export function updateTiers(id: number, body: TiersUpdate): Promise<TiersResponse> {
  return authenticatedRequest<TiersResponse>(`${PREFIX}/tiers/${id}`, { method: 'PATCH', body })
}

export function deleteTiers(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/tiers/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Contacts (sous-routes tiers) ---
export interface ListContactsByTiersParams {
  skip?: number
  limit?: number
  actif_only?: boolean
}

export function listContactsByTiers(tiersId: number, params: ListContactsByTiersParams = {}): Promise<ContactResponse[]> {
  return authenticatedRequest<ContactResponse[]>(`${PREFIX}/tiers/${tiersId}/contacts${toQuery(params)}`)
}

// --- Contacts (CRUD direct) ---
export function createContact(body: ContactCreate): Promise<ContactResponse> {
  return authenticatedRequest<ContactResponse>(`${PREFIX}/contacts`, { method: 'POST', body })
}

export function getContact(id: number): Promise<ContactResponse> {
  return authenticatedRequest<ContactResponse>(`${PREFIX}/contacts/${id}`)
}

export function updateContact(id: number, body: ContactUpdate): Promise<ContactResponse> {
  return authenticatedRequest<ContactResponse>(`${PREFIX}/contacts/${id}`, { method: 'PATCH', body })
}

export function deleteContact(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/contacts/${id}`, { method: 'DELETE' }) as Promise<void>
}
