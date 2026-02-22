/**
 * Types Comptabilité – alignés sur l'OpenAPI Gesco.
 */

// --- Comptes comptables ---
export interface CompteComptableCreate {
  entreprise_id: number
  numero: string
  libelle: string
  type_compte?: string | null
  sens_normal?: string
  actif?: boolean
}

export interface CompteComptableUpdate {
  numero?: string | null
  libelle?: string | null
  type_compte?: string | null
  sens_normal?: string | null
  actif?: boolean | null
}

export interface CompteComptableResponse {
  id: number
  entreprise_id: number
  numero: string
  libelle: string
  type_compte?: string | null
  sens_normal: string
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Journaux comptables ---
export interface JournalComptableCreate {
  entreprise_id: number
  code: string
  libelle: string
  actif?: boolean
}

export interface JournalComptableUpdate {
  code?: string | null
  libelle?: string | null
  actif?: boolean | null
}

export interface JournalComptableResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Périodes comptables ---
export interface PeriodeComptableCreate {
  entreprise_id: number
  date_debut: string
  date_fin: string
  libelle: string
}

export interface PeriodeComptableUpdate {
  date_fin?: string | null
  libelle?: string | null
  cloturee?: boolean | null
}

export interface PeriodeComptableResponse {
  id: number
  entreprise_id: number
  date_debut: string
  date_fin: string
  libelle: string
  cloturee: boolean
  created_at: string
}

// --- Écritures comptables ---
export interface LigneEcritureCreate {
  compte_id: number
  libelle_ligne?: string | null
  debit?: number | string
  credit?: number | string
}

export interface LigneEcritureResponse {
  id: number
  ecriture_id: number
  compte_id: number
  libelle_ligne?: string | null
  debit: string
  credit: string
}

export interface EcritureComptableCreate {
  entreprise_id: number
  journal_id: number
  periode_id?: number | null
  date_ecriture: string
  numero_piece: string
  piece_jointe_ref?: string | null
  libelle?: string | null
  lignes: LigneEcritureCreate[]
}

export interface EcritureComptableResponse {
  id: number
  entreprise_id: number
  journal_id: number
  periode_id?: number | null
  date_ecriture: string
  numero_piece: string
  piece_jointe_ref?: string | null
  libelle?: string | null
  created_by_id?: number | null
  created_at: string
}

export interface EcritureComptableDetailResponse extends EcritureComptableResponse {
  lignes: LigneEcritureResponse[]
}
