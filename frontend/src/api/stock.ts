/**
 * API Stock – alignée sur le backend (Bearer requis).
 * Stocks par dépôt/produit, quantité, mouvements, alertes.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  StockResponse,
  QuantiteStockResponse,
  MouvementStockCreate,
  MouvementStockResponse,
  AlerteStockResponse,
} from './types/stock'

const PREFIX = '/api/v1/stock'

// --- Stocks par dépôt ---
export interface ListStocksByDepotParams {
  skip?: number
  limit?: number
}

export function listStocksByDepot(depotId: number, params: ListStocksByDepotParams = {}): Promise<StockResponse[]> {
  return authenticatedRequest<StockResponse[]>(`${PREFIX}/depots/${depotId}/stocks${toQuery(params)}`)
}

export function getStock(depotId: number, stockId: number): Promise<StockResponse> {
  return authenticatedRequest<StockResponse>(`${PREFIX}/depots/${depotId}/stocks/${stockId}`)
}

// --- Quantité (dépôt × produit × variante optionnelle) ---
export interface GetQuantiteStockParams {
  variante_id?: number | null
}

export function getQuantiteStock(depotId: number, produitId: number, params: GetQuantiteStockParams = {}): Promise<QuantiteStockResponse> {
  return authenticatedRequest<QuantiteStockResponse>(`${PREFIX}/depots/${depotId}/produits/${produitId}/quantite${toQuery(params)}`)
}

// --- Stocks par produit ---
export interface ListStocksByProduitParams {
  skip?: number
  limit?: number
}

export function listStocksByProduit(produitId: number, params: ListStocksByProduitParams = {}): Promise<StockResponse[]> {
  return authenticatedRequest<StockResponse[]>(`${PREFIX}/produits/${produitId}/stocks${toQuery(params)}`)
}

// --- Mouvements ---
export interface ListMouvementsParams {
  depot_id: number
  produit_id?: number | null
  type_mouvement?: string | null
  date_from?: string | null
  date_to?: string | null
  skip?: number
  limit?: number
}

export function listMouvements(params: ListMouvementsParams): Promise<MouvementStockResponse[]> {
  return authenticatedRequest<MouvementStockResponse[]>(`${PREFIX}/mouvements${toQuery(params)}`)
}

export function getMouvement(id: number): Promise<MouvementStockResponse> {
  return authenticatedRequest<MouvementStockResponse>(`${PREFIX}/mouvements/${id}`)
}

export function createMouvement(body: MouvementStockCreate): Promise<MouvementStockResponse> {
  return authenticatedRequest<MouvementStockResponse>(`${PREFIX}/mouvements`, { method: 'POST', body })
}

// --- Alertes ---
export interface ListAlertesParams {
  depot_id: number
  skip?: number
  limit?: number
}

export function listAlertes(params: ListAlertesParams): Promise<AlerteStockResponse[]> {
  return authenticatedRequest<AlerteStockResponse[]>(`${PREFIX}/alertes${toQuery(params)}`)
}
