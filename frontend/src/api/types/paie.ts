/**
 * Types Paie – alignés sur l'OpenAPI Gesco.
 */

// --- Périodes de paie ---
export interface PeriodePaieCreate {
  entreprise_id: number
  annee: number
  mois: number
  date_debut: string
  date_fin: string
  cloturee?: boolean
}

export interface PeriodePaieUpdate {
  date_debut?: string | null
  date_fin?: string | null
  cloturee?: boolean | null
}

export interface PeriodePaieResponse {
  id: number
  entreprise_id: number
  annee: number
  mois: number
  date_debut: string
  date_fin: string
  cloturee: boolean
  created_at: string
}

// --- Types d'éléments de paie ---
export interface TypeElementPaieCreate {
  entreprise_id: number
  code: string
  libelle: string
  type: 'gain' | 'retenue'
  ordre_affichage?: number
  actif?: boolean
}

export interface TypeElementPaieUpdate {
  libelle?: string | null
  type?: 'gain' | 'retenue' | null
  ordre_affichage?: number | null
  actif?: boolean | null
}

export interface TypeElementPaieResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  type: string
  ordre_affichage: number
  actif: boolean
  created_at: string
}

// --- Bulletins de paie ---
export interface LigneBulletinPaieCreate {
  type_element_paie_id?: number | null
  libelle: string
  type: 'gain' | 'retenue'
  montant: number | string
  ordre?: number
}

export interface LigneBulletinPaieResponse {
  id: number
  bulletin_paie_id: number
  type_element_paie_id?: number | null
  libelle: string
  type: string
  montant: string
  ordre: number
  created_at: string
}

export interface BulletinPaieCreate {
  entreprise_id: number
  employe_id: number
  periode_paie_id: number
  salaire_brut?: number | string
  total_gains?: number | string
  total_retenues?: number | string
  net_a_payer?: number | string
  statut?: 'brouillon' | 'valide' | 'paye'
  lignes?: LigneBulletinPaieCreate[]
}

export interface BulletinPaieUpdate {
  salaire_brut?: number | string | null
  total_gains?: number | string | null
  total_retenues?: number | string | null
  net_a_payer?: number | string | null
  statut?: 'brouillon' | 'valide' | 'paye' | null
  date_paiement?: string | null
}

export interface BulletinPaieResponse {
  id: number
  entreprise_id: number
  employe_id: number
  periode_paie_id: number
  salaire_brut: string
  total_gains: string
  total_retenues: string
  net_a_payer: string
  statut: string
  date_paiement?: string | null
  created_at: string
}

export interface BulletinPaieDetailResponse extends BulletinPaieResponse {
  lignes: LigneBulletinPaieResponse[]
}
