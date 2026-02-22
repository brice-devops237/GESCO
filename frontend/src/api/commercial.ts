/**
 * API Commercial – alignée sur le backend (Bearer requis).
 * États document, Devis, Commandes, Factures, Bons de livraison.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  EtatDocumentCreate,
  EtatDocumentUpdate,
  EtatDocumentResponse,
  DevisCreate,
  DevisUpdate,
  DevisResponse,
  CommandeCreate,
  CommandeUpdate,
  CommandeResponse,
  FactureCreate,
  FactureUpdate,
  FactureResponse,
  BonLivraisonCreate,
  BonLivraisonUpdate,
  BonLivraisonResponse,
} from './types/commercial'

const PREFIX = '/api/v1/commercial'

// --- États document ---
export interface ListEtatsDocumentParams {
  type_document?: string | null
  skip?: number
  limit?: number
}

export function listEtatsDocument(params: ListEtatsDocumentParams = {}): Promise<EtatDocumentResponse[]> {
  return authenticatedRequest<EtatDocumentResponse[]>(`${PREFIX}/etats-document${toQuery(params)}`)
}

export function getEtatDocument(id: number): Promise<EtatDocumentResponse> {
  return authenticatedRequest<EtatDocumentResponse>(`${PREFIX}/etats-document/${id}`)
}

export function createEtatDocument(body: EtatDocumentCreate): Promise<EtatDocumentResponse> {
  return authenticatedRequest<EtatDocumentResponse>(`${PREFIX}/etats-document`, { method: 'POST', body })
}

export function updateEtatDocument(id: number, body: EtatDocumentUpdate): Promise<EtatDocumentResponse> {
  return authenticatedRequest<EtatDocumentResponse>(`${PREFIX}/etats-document/${id}`, { method: 'PATCH', body })
}

// --- Devis ---
export interface ListDevisParams {
  entreprise_id: number
  client_id?: number | null
  skip?: number
  limit?: number
}

export function listDevis(params: ListDevisParams): Promise<DevisResponse[]> {
  return authenticatedRequest<DevisResponse[]>(`${PREFIX}/devis${toQuery(params)}`)
}

export function getDevis(id: number): Promise<DevisResponse> {
  return authenticatedRequest<DevisResponse>(`${PREFIX}/devis/${id}`)
}

export function createDevis(body: DevisCreate): Promise<DevisResponse> {
  return authenticatedRequest<DevisResponse>(`${PREFIX}/devis`, { method: 'POST', body })
}

export function updateDevis(id: number, body: DevisUpdate): Promise<DevisResponse> {
  return authenticatedRequest<DevisResponse>(`${PREFIX}/devis/${id}`, { method: 'PATCH', body })
}

// --- Commandes ---
export interface ListCommandesParams {
  entreprise_id: number
  client_id?: number | null
  skip?: number
  limit?: number
}

export function listCommandes(params: ListCommandesParams): Promise<CommandeResponse[]> {
  return authenticatedRequest<CommandeResponse[]>(`${PREFIX}/commandes${toQuery(params)}`)
}

export function getCommande(id: number): Promise<CommandeResponse> {
  return authenticatedRequest<CommandeResponse>(`${PREFIX}/commandes/${id}`)
}

export function createCommande(body: CommandeCreate): Promise<CommandeResponse> {
  return authenticatedRequest<CommandeResponse>(`${PREFIX}/commandes`, { method: 'POST', body })
}

export function updateCommande(id: number, body: CommandeUpdate): Promise<CommandeResponse> {
  return authenticatedRequest<CommandeResponse>(`${PREFIX}/commandes/${id}`, { method: 'PATCH', body })
}

// --- Factures ---
export interface ListFacturesParams {
  entreprise_id: number
  client_id?: number | null
  skip?: number
  limit?: number
}

export function listFactures(params: ListFacturesParams): Promise<FactureResponse[]> {
  return authenticatedRequest<FactureResponse[]>(`${PREFIX}/factures${toQuery(params)}`)
}

export function getFacture(id: number): Promise<FactureResponse> {
  return authenticatedRequest<FactureResponse>(`${PREFIX}/factures/${id}`)
}

export function createFacture(body: FactureCreate): Promise<FactureResponse> {
  return authenticatedRequest<FactureResponse>(`${PREFIX}/factures`, { method: 'POST', body })
}

export function updateFacture(id: number, body: FactureUpdate): Promise<FactureResponse> {
  return authenticatedRequest<FactureResponse>(`${PREFIX}/factures/${id}`, { method: 'PATCH', body })
}

// --- Bons de livraison ---
export interface ListBonsLivraisonParams {
  entreprise_id: number
  client_id?: number | null
  skip?: number
  limit?: number
}

export function listBonsLivraison(params: ListBonsLivraisonParams): Promise<BonLivraisonResponse[]> {
  return authenticatedRequest<BonLivraisonResponse[]>(`${PREFIX}/bons-livraison${toQuery(params)}`)
}

export function getBonLivraison(id: number): Promise<BonLivraisonResponse> {
  return authenticatedRequest<BonLivraisonResponse>(`${PREFIX}/bons-livraison/${id}`)
}

export function createBonLivraison(body: BonLivraisonCreate): Promise<BonLivraisonResponse> {
  return authenticatedRequest<BonLivraisonResponse>(`${PREFIX}/bons-livraison`, { method: 'POST', body })
}

export function updateBonLivraison(id: number, body: BonLivraisonUpdate): Promise<BonLivraisonResponse> {
  return authenticatedRequest<BonLivraisonResponse>(`${PREFIX}/bons-livraison/${id}`, { method: 'PATCH', body })
}
