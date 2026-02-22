/**
 * API Achats – alignée sur le backend (Bearer requis).
 * Dépôts : entrepôts / lieux de stockage (multi-sites).
 * Commandes fournisseurs : commandes d'achat (fournisseur, dépôt, dates, montants, état).
 * Réceptions : bons de réception (livraison fournisseur, n° BL, dépôt).
 * Factures fournisseurs : factures d'achat (facture / avoir / proforma, échéance, restant dû).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  DepotCreate,
  DepotUpdate,
  DepotResponse,
  CommandeFournisseurCreate,
  CommandeFournisseurUpdate,
  CommandeFournisseurResponse,
  ReceptionCreate,
  ReceptionUpdate,
  ReceptionResponse,
  FactureFournisseurCreate,
  FactureFournisseurUpdate,
  FactureFournisseurResponse,
} from './types/achats'

const PREFIX = '/api/v1/achats'

// --- Dépôts ---
export interface ListDepotsParams {
  entreprise_id: number
  skip?: number
  limit?: number
}

export function listDepots(params: ListDepotsParams): Promise<DepotResponse[]> {
  return authenticatedRequest<DepotResponse[]>(`${PREFIX}/depots${toQuery(params)}`)
}

export function getDepot(id: number): Promise<DepotResponse> {
  return authenticatedRequest<DepotResponse>(`${PREFIX}/depots/${id}`)
}

export function createDepot(body: DepotCreate): Promise<DepotResponse> {
  return authenticatedRequest<DepotResponse>(`${PREFIX}/depots`, { method: 'POST', body })
}

export function updateDepot(id: number, body: DepotUpdate): Promise<DepotResponse> {
  return authenticatedRequest<DepotResponse>(`${PREFIX}/depots/${id}`, { method: 'PATCH', body })
}

export function deleteDepot(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/depots/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Commandes fournisseurs ---
export interface ListCommandesFournisseursParams {
  entreprise_id: number
  fournisseur_id?: number | null
  skip?: number
  limit?: number
}

export function listCommandesFournisseurs(params: ListCommandesFournisseursParams): Promise<CommandeFournisseurResponse[]> {
  return authenticatedRequest<CommandeFournisseurResponse[]>(`${PREFIX}/commandes-fournisseurs${toQuery(params)}`)
}

export function getCommandeFournisseur(id: number): Promise<CommandeFournisseurResponse> {
  return authenticatedRequest<CommandeFournisseurResponse>(`${PREFIX}/commandes-fournisseurs/${id}`)
}

export function createCommandeFournisseur(body: CommandeFournisseurCreate): Promise<CommandeFournisseurResponse> {
  return authenticatedRequest<CommandeFournisseurResponse>(`${PREFIX}/commandes-fournisseurs`, { method: 'POST', body })
}

export function updateCommandeFournisseur(id: number, body: CommandeFournisseurUpdate): Promise<CommandeFournisseurResponse> {
  return authenticatedRequest<CommandeFournisseurResponse>(`${PREFIX}/commandes-fournisseurs/${id}`, { method: 'PATCH', body })
}

// --- Réceptions (sous-route commande) ---
export interface ListReceptionsByCommandeParams {
  skip?: number
  limit?: number
}

export function listReceptionsByCommande(commandeId: number, params: ListReceptionsByCommandeParams = {}): Promise<ReceptionResponse[]> {
  return authenticatedRequest<ReceptionResponse[]>(`${PREFIX}/commandes-fournisseurs/${commandeId}/receptions${toQuery(params)}`)
}

// --- Réceptions (CRUD) ---
export function createReception(body: ReceptionCreate): Promise<ReceptionResponse> {
  return authenticatedRequest<ReceptionResponse>(`${PREFIX}/receptions`, { method: 'POST', body })
}

export function getReception(id: number): Promise<ReceptionResponse> {
  return authenticatedRequest<ReceptionResponse>(`${PREFIX}/receptions/${id}`)
}

export function updateReception(id: number, body: ReceptionUpdate): Promise<ReceptionResponse> {
  return authenticatedRequest<ReceptionResponse>(`${PREFIX}/receptions/${id}`, { method: 'PATCH', body })
}

// --- Factures fournisseurs ---
export interface ListFacturesFournisseursParams {
  entreprise_id: number
  fournisseur_id?: number | null
  skip?: number
  limit?: number
}

export function listFacturesFournisseurs(params: ListFacturesFournisseursParams): Promise<FactureFournisseurResponse[]> {
  return authenticatedRequest<FactureFournisseurResponse[]>(`${PREFIX}/factures-fournisseurs${toQuery(params)}`)
}

export function getFactureFournisseur(id: number): Promise<FactureFournisseurResponse> {
  return authenticatedRequest<FactureFournisseurResponse>(`${PREFIX}/factures-fournisseurs/${id}`)
}

export function createFactureFournisseur(body: FactureFournisseurCreate): Promise<FactureFournisseurResponse> {
  return authenticatedRequest<FactureFournisseurResponse>(`${PREFIX}/factures-fournisseurs`, { method: 'POST', body })
}

export function updateFactureFournisseur(id: number, body: FactureFournisseurUpdate): Promise<FactureFournisseurResponse> {
  return authenticatedRequest<FactureFournisseurResponse>(`${PREFIX}/factures-fournisseurs/${id}`, { method: 'PATCH', body })
}
