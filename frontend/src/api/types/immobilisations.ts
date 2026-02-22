/**
 * Types Immobilisations – alignés sur l'OpenAPI Gesco.
 */

// --- Catégories ---
export interface CategorieImmobilisationCreate {
  entreprise_id: number
  code: string
  libelle: string
  duree_amortissement_annees?: number
  taux_amortissement?: number | string | null
}

export interface CategorieImmobilisationUpdate {
  libelle?: string | null
  duree_amortissement_annees?: number | null
  taux_amortissement?: number | string | null
}

export interface CategorieImmobilisationResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  duree_amortissement_annees: number
  taux_amortissement?: string | null
  created_at: string
  updated_at: string
}

// --- Immobilisations (actifs) ---
export interface ImmobilisationCreate {
  entreprise_id: number
  categorie_id: number
  compte_comptable_id?: number | null
  compte_amortissement_id?: number | null
  code: string
  designation: string
  date_acquisition: string
  valeur_acquisition: number | string
  duree_amortissement_annees?: number
  date_mise_en_service?: string | null
  notes?: string | null
}

export interface ImmobilisationUpdate {
  designation?: string | null
  date_mise_en_service?: string | null
  notes?: string | null
  actif?: boolean | null
}

export interface ImmobilisationResponse {
  id: number
  entreprise_id: number
  categorie_id: number
  code: string
  designation: string
  date_acquisition: string
  valeur_acquisition: string
  duree_amortissement_annees: number
  date_mise_en_service?: string | null
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Lignes d'amortissement ---
export interface LigneAmortissementResponse {
  id: number
  immobilisation_id: number
  annee: number
  mois?: number | null
  montant_dotation: string
  cumul_amortissement: string
  valeur_nette: string
  created_at: string
}
