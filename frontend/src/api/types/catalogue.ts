/**
 * Types Catalogue – alignés sur l'OpenAPI Gesco.
 */

// --- Unités de mesure ---
export type TypeUniteMesure = 'unite' | 'poids' | 'volume' | 'longueur' | 'surface'

export interface UniteMesureCreate {
  code: string
  libelle: string
  symbole?: string | null
  type: TypeUniteMesure
  code_cefact?: string | null
  actif?: boolean
}

export interface UniteMesureUpdate {
  libelle?: string | null
  symbole?: string | null
  type?: TypeUniteMesure | null
  code_cefact?: string | null
  actif?: boolean | null
}

export interface UniteMesureResponse {
  id: number
  code: string
  libelle: string
  symbole?: string | null
  type: string
  code_cefact?: string | null
  actif: boolean
}

// --- Taux TVA ---
export type NatureTva = 'normal' | 'reduit' | 'exonere'

export interface TauxTvaCreate {
  code: string
  taux: number | string
  libelle: string
  nature?: NatureTva | null
  actif?: boolean
}

export interface TauxTvaUpdate {
  taux?: number | string | null
  libelle?: string | null
  nature?: NatureTva | null
  actif?: boolean | null
}

export interface TauxTvaResponse {
  id: number
  code: string
  taux: string
  libelle: string
  nature?: string | null
  actif: boolean
}

// --- Familles de produits ---
export interface FamilleProduitCreate {
  entreprise_id: number
  parent_id?: number | null
  code: string
  libelle: string
  description?: string | null
  niveau?: number
  ordre_affichage?: number
  actif?: boolean
}

export interface FamilleProduitUpdate {
  parent_id?: number | null
  code?: string | null
  libelle?: string | null
  description?: string | null
  niveau?: number | null
  ordre_affichage?: number | null
  actif?: boolean | null
}

export interface FamilleProduitResponse {
  id: number
  entreprise_id: number
  parent_id?: number | null
  code: string
  libelle: string
  description?: string | null
  niveau: number
  ordre_affichage: number
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Conditionnements ---
export type TypeEmballage = 'caisse' | 'carton' | 'palette' | 'sachet' | 'bidon' | 'fut' | 'bouteille' | 'autre'

export interface ConditionnementCreate {
  entreprise_id: number
  code: string
  libelle: string
  quantite_unites: number | string
  unite_id: number
  type_emballage?: TypeEmballage | null
  poids_net_kg?: number | string | null
  actif?: boolean
}

export interface ConditionnementUpdate {
  code?: string | null
  libelle?: string | null
  quantite_unites?: number | string | null
  unite_id?: number | null
  type_emballage?: TypeEmballage | null
  poids_net_kg?: number | string | null
  actif?: boolean | null
}

export interface ConditionnementResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  quantite_unites: string
  unite_id: number
  type_emballage?: string | null
  poids_net_kg?: string | null
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Produits ---
export type TypeProduit = 'produit' | 'service' | 'composant'

export interface ProduitCreate {
  entreprise_id: number
  famille_id?: number | null
  code: string
  code_barre?: string | null
  libelle: string
  description?: string | null
  type?: TypeProduit
  marque?: string | null
  reference_fournisseur?: string | null
  code_douanier?: string | null
  pays_origine?: string | null
  poids_net_kg?: number | string | null
  unite_vente_id: number
  unite_achat_id?: number | null
  coefficient_achat_vente?: number | string
  prix_achat_ht?: number | string | null
  prix_vente_ttc: number | string
  taux_tva_id?: number | null
  seuil_alerte_min?: number | string
  seuil_alerte_max?: number | string | null
  gerer_stock?: boolean
  actif?: boolean
}

export interface ProduitUpdate {
  famille_id?: number | null
  code?: string | null
  code_barre?: string | null
  libelle?: string | null
  description?: string | null
  type?: TypeProduit | null
  marque?: string | null
  reference_fournisseur?: string | null
  code_douanier?: string | null
  pays_origine?: string | null
  poids_net_kg?: number | string | null
  unite_vente_id?: number | null
  unite_achat_id?: number | null
  coefficient_achat_vente?: number | string | null
  prix_achat_ht?: number | string | null
  prix_vente_ttc?: number | string | null
  taux_tva_id?: number | null
  seuil_alerte_min?: number | string | null
  seuil_alerte_max?: number | string | null
  gerer_stock?: boolean | null
  actif?: boolean | null
}

export interface ProduitResponse {
  id: number
  entreprise_id: number
  famille_id?: number | null
  code: string
  code_barre?: string | null
  libelle: string
  description?: string | null
  type: string
  marque?: string | null
  reference_fournisseur?: string | null
  code_douanier?: string | null
  pays_origine?: string | null
  poids_net_kg?: string | null
  unite_vente_id: number
  unite_achat_id?: number | null
  coefficient_achat_vente: string
  prix_achat_ht?: string | null
  prix_vente_ttc: string
  taux_tva_id?: number | null
  seuil_alerte_min: string
  seuil_alerte_max?: string | null
  gerer_stock: boolean
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Produits-Conditionnements ---
export interface ProduitConditionnementCreate {
  produit_id: number
  conditionnement_id: number
  quantite_unites: number | string
  prix_vente_ttc?: number | string | null
}

export interface ProduitConditionnementUpdate {
  quantite_unites?: number | string | null
  prix_vente_ttc?: number | string | null
}

export interface ProduitConditionnementResponse {
  id: number
  produit_id: number
  conditionnement_id: number
  quantite_unites: string
  prix_vente_ttc?: string | null
}

// --- Canaux de vente ---
export interface CanalVenteCreate {
  entreprise_id: number
  code: string
  libelle: string
  ordre?: number
  actif?: boolean
}

export interface CanalVenteUpdate {
  code?: string | null
  libelle?: string | null
  ordre?: number | null
  actif?: boolean | null
}

export interface CanalVenteResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  ordre: number
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Prix produits ---
export interface PrixProduitCreate {
  produit_id: number
  canal_vente_id?: number | null
  point_de_vente_id?: number | null
  prix_ttc: number | string
  prix_ht?: number | string | null
  date_debut: string
  date_fin?: string | null
}

export interface PrixProduitUpdate {
  canal_vente_id?: number | null
  point_de_vente_id?: number | null
  prix_ttc?: number | string | null
  prix_ht?: number | string | null
  date_debut?: string | null
  date_fin?: string | null
}

export interface PrixProduitResponse {
  id: number
  produit_id: number
  canal_vente_id?: number | null
  point_de_vente_id?: number | null
  prix_ttc: string
  prix_ht?: string | null
  date_debut: string
  date_fin?: string | null
  created_at: string
  updated_at: string
}

// --- Variantes produit ---
export interface VarianteProduitCreate {
  produit_id: number
  code: string
  libelle: string
  prix_ttc_supplement?: number | string
  stock_separe?: boolean
  actif?: boolean
}

export interface VarianteProduitUpdate {
  code?: string | null
  libelle?: string | null
  prix_ttc_supplement?: number | string | null
  stock_separe?: boolean | null
  actif?: boolean | null
}

export interface VarianteProduitResponse {
  id: number
  produit_id: number
  code: string
  libelle: string
  prix_ttc_supplement: string
  stock_separe: boolean
  actif: boolean
  created_at: string
  updated_at: string
}
