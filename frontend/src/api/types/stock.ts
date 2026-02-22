/**
 * Types Stock – alignés sur l'OpenAPI Gesco.
 */

export interface StockResponse {
  id: number
  depot_id: number
  produit_id: number
  variante_id?: number | null
  quantite: string
  unite_id: number
  updated_at: string
}

export interface QuantiteStockResponse {
  depot_id: number
  produit_id: number
  variante_id?: number | null
  quantite: string
}

export interface MouvementStockCreate {
  type_mouvement: string
  depot_id: number
  depot_dest_id?: number | null
  produit_id: number
  variante_id?: number | null
  quantite: number | string
  lot_serie?: string | null
  date_peremption?: string | null
  reference_type: string
  reference_id?: number | null
  notes?: string | null
}

export interface MouvementStockResponse {
  id: number
  type_mouvement: string
  depot_id: number
  depot_dest_id?: number | null
  produit_id: number
  variante_id?: number | null
  quantite: string
  lot_serie?: string | null
  date_peremption?: string | null
  date_mouvement: string
  reference_type: string
  reference_id?: number | null
  notes?: string | null
  created_by_id?: number | null
  created_at: string
}

export interface AlerteStockResponse {
  produit_id: number
  produit_code?: string | null
  produit_libelle?: string | null
  depot_id: number
  depot_libelle?: string | null
  variante_id?: number | null
  variante_libelle?: string | null
  quantite: string
  seuil_alerte_min: string
  seuil_alerte_max?: string | null
  type_alerte: string
}
