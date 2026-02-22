/**
 * API Catalogue – alignée sur le backend (Bearer requis).
 * Unités de mesure, taux TVA, familles produits, conditionnements, produits,
 * produits-conditionnements, canaux de vente, prix produits, variantes.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  UniteMesureCreate,
  UniteMesureUpdate,
  UniteMesureResponse,
  TauxTvaCreate,
  TauxTvaUpdate,
  TauxTvaResponse,
  FamilleProduitCreate,
  FamilleProduitUpdate,
  FamilleProduitResponse,
  ConditionnementCreate,
  ConditionnementUpdate,
  ConditionnementResponse,
  ProduitCreate,
  ProduitUpdate,
  ProduitResponse,
  ProduitConditionnementCreate,
  ProduitConditionnementUpdate,
  ProduitConditionnementResponse,
  CanalVenteCreate,
  CanalVenteUpdate,
  CanalVenteResponse,
  PrixProduitCreate,
  PrixProduitUpdate,
  PrixProduitResponse,
  VarianteProduitCreate,
  VarianteProduitUpdate,
  VarianteProduitResponse,
} from './types/catalogue'

const PREFIX = '/api/v1/catalogue'

// --- Unités de mesure ---
export interface ListUnitesMesureParams {
  skip?: number
  limit?: number
  actif_only?: boolean
}

export function listUnitesMesure(params: ListUnitesMesureParams = {}): Promise<UniteMesureResponse[]> {
  return authenticatedRequest<UniteMesureResponse[]>(`${PREFIX}/unites-mesure${toQuery(params)}`)
}

export function getUniteMesure(id: number): Promise<UniteMesureResponse> {
  return authenticatedRequest<UniteMesureResponse>(`${PREFIX}/unites-mesure/${id}`)
}

export function createUniteMesure(body: UniteMesureCreate): Promise<UniteMesureResponse> {
  return authenticatedRequest<UniteMesureResponse>(`${PREFIX}/unites-mesure`, { method: 'POST', body })
}

export function updateUniteMesure(id: number, body: UniteMesureUpdate): Promise<UniteMesureResponse> {
  return authenticatedRequest<UniteMesureResponse>(`${PREFIX}/unites-mesure/${id}`, { method: 'PATCH', body })
}

export function deleteUniteMesure(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/unites-mesure/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Taux TVA ---
export interface ListTauxTvaParams {
  skip?: number
  limit?: number
  actif_only?: boolean
}

export function listTauxTva(params: ListTauxTvaParams = {}): Promise<TauxTvaResponse[]> {
  return authenticatedRequest<TauxTvaResponse[]>(`${PREFIX}/taux-tva${toQuery(params)}`)
}

export function getTauxTva(id: number): Promise<TauxTvaResponse> {
  return authenticatedRequest<TauxTvaResponse>(`${PREFIX}/taux-tva/${id}`)
}

export function createTauxTva(body: TauxTvaCreate): Promise<TauxTvaResponse> {
  return authenticatedRequest<TauxTvaResponse>(`${PREFIX}/taux-tva`, { method: 'POST', body })
}

export function updateTauxTva(id: number, body: TauxTvaUpdate): Promise<TauxTvaResponse> {
  return authenticatedRequest<TauxTvaResponse>(`${PREFIX}/taux-tva/${id}`, { method: 'PATCH', body })
}

export function deleteTauxTva(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/taux-tva/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Familles de produits ---
export interface ListFamillesProduitsParams {
  entreprise_id: number
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export function listFamillesProduits(params: ListFamillesProduitsParams): Promise<FamilleProduitResponse[]> {
  return authenticatedRequest<FamilleProduitResponse[]>(`${PREFIX}/familles-produits${toQuery(params)}`)
}

export function getFamilleProduit(id: number): Promise<FamilleProduitResponse> {
  return authenticatedRequest<FamilleProduitResponse>(`${PREFIX}/familles-produits/${id}`)
}

export function createFamilleProduit(body: FamilleProduitCreate): Promise<FamilleProduitResponse> {
  return authenticatedRequest<FamilleProduitResponse>(`${PREFIX}/familles-produits`, { method: 'POST', body })
}

export function updateFamilleProduit(id: number, body: FamilleProduitUpdate): Promise<FamilleProduitResponse> {
  return authenticatedRequest<FamilleProduitResponse>(`${PREFIX}/familles-produits/${id}`, { method: 'PATCH', body })
}

export function deleteFamilleProduit(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/familles-produits/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Conditionnements ---
export interface ListConditionnementsParams {
  entreprise_id: number
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export function listConditionnements(params: ListConditionnementsParams): Promise<ConditionnementResponse[]> {
  return authenticatedRequest<ConditionnementResponse[]>(`${PREFIX}/conditionnements${toQuery(params)}`)
}

export function getConditionnement(id: number): Promise<ConditionnementResponse> {
  return authenticatedRequest<ConditionnementResponse>(`${PREFIX}/conditionnements/${id}`)
}

export function createConditionnement(body: ConditionnementCreate): Promise<ConditionnementResponse> {
  return authenticatedRequest<ConditionnementResponse>(`${PREFIX}/conditionnements`, { method: 'POST', body })
}

export function updateConditionnement(id: number, body: ConditionnementUpdate): Promise<ConditionnementResponse> {
  return authenticatedRequest<ConditionnementResponse>(`${PREFIX}/conditionnements/${id}`, { method: 'PATCH', body })
}

export function deleteConditionnement(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/conditionnements/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Produits ---
export interface ListProduitsParams {
  entreprise_id: number
  famille_id?: number | null
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export function listProduits(params: ListProduitsParams): Promise<ProduitResponse[]> {
  return authenticatedRequest<ProduitResponse[]>(`${PREFIX}/produits${toQuery(params)}`)
}

export function getProduit(id: number): Promise<ProduitResponse> {
  return authenticatedRequest<ProduitResponse>(`${PREFIX}/produits/${id}`)
}

export function createProduit(body: ProduitCreate): Promise<ProduitResponse> {
  return authenticatedRequest<ProduitResponse>(`${PREFIX}/produits`, { method: 'POST', body })
}

export function updateProduit(id: number, body: ProduitUpdate): Promise<ProduitResponse> {
  return authenticatedRequest<ProduitResponse>(`${PREFIX}/produits/${id}`, { method: 'PATCH', body })
}

export function deleteProduit(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/produits/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Produits / conditionnements (sous-routes produit) ---
export interface ListProduitConditionnementsParams {
  skip?: number
  limit?: number
}

export function listProduitConditionnements(produitId: number, params: ListProduitConditionnementsParams = {}): Promise<ProduitConditionnementResponse[]> {
  return authenticatedRequest<ProduitConditionnementResponse[]>(`${PREFIX}/produits/${produitId}/conditionnements${toQuery(params)}`)
}

export interface ListPrixByProduitParams {
  skip?: number
  limit?: number
}

export function listPrixByProduit(produitId: number, params: ListPrixByProduitParams = {}): Promise<PrixProduitResponse[]> {
  return authenticatedRequest<PrixProduitResponse[]>(`${PREFIX}/produits/${produitId}/prix${toQuery(params)}`)
}

export interface ListVariantesByProduitParams {
  skip?: number
  limit?: number
  actif_only?: boolean
}

export function listVariantesByProduit(produitId: number, params: ListVariantesByProduitParams = {}): Promise<VarianteProduitResponse[]> {
  return authenticatedRequest<VarianteProduitResponse[]>(`${PREFIX}/produits/${produitId}/variantes${toQuery(params)}`)
}

// --- Produits-Conditionnements (CRUD direct) ---
export function getProduitConditionnement(id: number): Promise<ProduitConditionnementResponse> {
  return authenticatedRequest<ProduitConditionnementResponse>(`${PREFIX}/produits-conditionnements/${id}`)
}

export function createProduitConditionnement(body: ProduitConditionnementCreate): Promise<ProduitConditionnementResponse> {
  return authenticatedRequest<ProduitConditionnementResponse>(`${PREFIX}/produits-conditionnements`, { method: 'POST', body })
}

export function updateProduitConditionnement(id: number, body: ProduitConditionnementUpdate): Promise<ProduitConditionnementResponse> {
  return authenticatedRequest<ProduitConditionnementResponse>(`${PREFIX}/produits-conditionnements/${id}`, { method: 'PATCH', body })
}

export function deleteProduitConditionnement(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/produits-conditionnements/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Canaux de vente ---
export interface ListCanauxVenteParams {
  entreprise_id: number
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export function listCanauxVente(params: ListCanauxVenteParams): Promise<CanalVenteResponse[]> {
  return authenticatedRequest<CanalVenteResponse[]>(`${PREFIX}/canaux-vente${toQuery(params)}`)
}

export function getCanalVente(id: number): Promise<CanalVenteResponse> {
  return authenticatedRequest<CanalVenteResponse>(`${PREFIX}/canaux-vente/${id}`)
}

export function createCanalVente(body: CanalVenteCreate): Promise<CanalVenteResponse> {
  return authenticatedRequest<CanalVenteResponse>(`${PREFIX}/canaux-vente`, { method: 'POST', body })
}

export function updateCanalVente(id: number, body: CanalVenteUpdate): Promise<CanalVenteResponse> {
  return authenticatedRequest<CanalVenteResponse>(`${PREFIX}/canaux-vente/${id}`, { method: 'PATCH', body })
}

export function deleteCanalVente(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/canaux-vente/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Prix produits ---
export interface ListPrixProduitsParams {
  entreprise_id: number
  skip?: number
  limit?: number
}

export function listPrixProduits(params: ListPrixProduitsParams): Promise<PrixProduitResponse[]> {
  return authenticatedRequest<PrixProduitResponse[]>(`${PREFIX}/prix-produits${toQuery(params)}`)
}

export function getPrixProduit(id: number): Promise<PrixProduitResponse> {
  return authenticatedRequest<PrixProduitResponse>(`${PREFIX}/prix-produits/${id}`)
}

export function createPrixProduit(body: PrixProduitCreate): Promise<PrixProduitResponse> {
  return authenticatedRequest<PrixProduitResponse>(`${PREFIX}/prix-produits`, { method: 'POST', body })
}

export function updatePrixProduit(id: number, body: PrixProduitUpdate): Promise<PrixProduitResponse> {
  return authenticatedRequest<PrixProduitResponse>(`${PREFIX}/prix-produits/${id}`, { method: 'PATCH', body })
}

export function deletePrixProduit(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/prix-produits/${id}`, { method: 'DELETE' }) as Promise<void>
}

// --- Variantes produit ---
export function getVarianteProduit(id: number): Promise<VarianteProduitResponse> {
  return authenticatedRequest<VarianteProduitResponse>(`${PREFIX}/variantes-produits/${id}`)
}

export function createVarianteProduit(body: VarianteProduitCreate): Promise<VarianteProduitResponse> {
  return authenticatedRequest<VarianteProduitResponse>(`${PREFIX}/variantes-produits`, { method: 'POST', body })
}

export function updateVarianteProduit(id: number, body: VarianteProduitUpdate): Promise<VarianteProduitResponse> {
  return authenticatedRequest<VarianteProduitResponse>(`${PREFIX}/variantes-produits/${id}`, { method: 'PATCH', body })
}

export function deleteVarianteProduit(id: number): Promise<void> {
  return authenticatedRequest<unknown>(`${PREFIX}/variantes-produits/${id}`, { method: 'DELETE' }) as Promise<void>
}
