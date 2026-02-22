/**
 * Types Trésorerie – alignés sur l'OpenAPI Gesco.
 */

// --- Modes de paiement ---
export interface ModePaiementCreate {
  entreprise_id: number
  code: string
  libelle: string
  code_operateur?: string | null
  actif?: boolean
}

export interface ModePaiementUpdate {
  code?: string | null
  libelle?: string | null
  code_operateur?: string | null
  actif?: boolean | null
}

export interface ModePaiementResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  code_operateur?: string | null
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Comptes trésorerie ---
export interface CompteTresorerieCreate {
  entreprise_id: number
  type_compte: string
  libelle: string
  numero_compte?: string | null
  iban?: string | null
  devise_id: number
  actif?: boolean
}

export interface CompteTresorerieUpdate {
  type_compte?: string | null
  libelle?: string | null
  numero_compte?: string | null
  iban?: string | null
  devise_id?: number | null
  actif?: boolean | null
}

export interface CompteTresorerieResponse {
  id: number
  entreprise_id: number
  type_compte: string
  libelle: string
  numero_compte?: string | null
  iban?: string | null
  devise_id: number
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Règlements ---
export interface ReglementCreate {
  entreprise_id: number
  type_reglement: string
  facture_id?: number | null
  facture_fournisseur_id?: number | null
  tiers_id: number
  montant: number | string
  date_reglement: string
  date_valeur?: string | null
  mode_paiement_id: number
  compte_tresorerie_id: number
  reference?: string | null
  notes?: string | null
}

export interface ReglementResponse {
  id: number
  entreprise_id: number
  type_reglement: string
  facture_id?: number | null
  facture_fournisseur_id?: number | null
  tiers_id: number
  montant: string
  date_reglement: string
  date_valeur?: string | null
  mode_paiement_id: number
  compte_tresorerie_id: number
  reference?: string | null
  notes?: string | null
  created_by_id?: number | null
  created_at: string
}
