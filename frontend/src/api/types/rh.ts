/**
 * Types RH – alignés sur l'OpenAPI Gesco.
 */

// --- Départements ---
export interface DepartementCreate {
  entreprise_id: number
  code: string
  libelle: string
  centre_cout?: string | null
  actif?: boolean
}

export interface DepartementUpdate {
  code?: string | null
  libelle?: string | null
  centre_cout?: string | null
  actif?: boolean | null
}

export interface DepartementResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  centre_cout?: string | null
  actif: boolean
  created_at: string
}

// --- Postes ---
export interface PosteCreate {
  entreprise_id: number
  departement_id?: number | null
  code: string
  libelle: string
  actif?: boolean
}

export interface PosteUpdate {
  departement_id?: number | null
  code?: string | null
  libelle?: string | null
  actif?: boolean | null
}

export interface PosteResponse {
  id: number
  entreprise_id: number
  departement_id?: number | null
  code: string
  libelle: string
  actif: boolean
  created_at: string
}

// --- Types de contrat ---
export interface TypeContratCreate {
  entreprise_id: number
  code: string
  libelle: string
  actif?: boolean
}

export interface TypeContratUpdate {
  code?: string | null
  libelle?: string | null
  actif?: boolean | null
}

export interface TypeContratResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  actif: boolean
  created_at: string
}

// --- Employés ---
export interface EmployeCreate {
  entreprise_id: number
  utilisateur_id?: number | null
  departement_id?: number | null
  poste_id?: number | null
  type_contrat_id?: number | null
  matricule: string
  nom: string
  prenom: string
  date_naissance?: string | null
  lieu_naissance?: string | null
  genre?: string | null
  nationalite?: string | null
  situation_familiale?: string | null
  niu?: string | null
  numero_cnps?: string | null
  email?: string | null
  telephone?: string | null
  adresse?: string | null
  date_embauche: string
  salaire_base?: number | string
  devise_id?: number | null
  compte_bancaire?: string | null
  banque?: string | null
  actif?: boolean
}

export interface EmployeUpdate {
  utilisateur_id?: number | null
  departement_id?: number | null
  poste_id?: number | null
  type_contrat_id?: number | null
  matricule?: string | null
  nom?: string | null
  prenom?: string | null
  date_naissance?: string | null
  lieu_naissance?: string | null
  genre?: string | null
  nationalite?: string | null
  situation_familiale?: string | null
  niu?: string | null
  numero_cnps?: string | null
  email?: string | null
  telephone?: string | null
  adresse?: string | null
  date_embauche?: string | null
  salaire_base?: number | string | null
  devise_id?: number | null
  compte_bancaire?: string | null
  banque?: string | null
  actif?: boolean | null
}

export interface EmployeResponse {
  id: number
  entreprise_id: number
  utilisateur_id?: number | null
  departement_id?: number | null
  poste_id?: number | null
  type_contrat_id?: number | null
  matricule: string
  nom: string
  prenom: string
  date_naissance?: string | null
  lieu_naissance?: string | null
  genre?: string | null
  nationalite?: string | null
  situation_familiale?: string | null
  niu?: string | null
  numero_cnps?: string | null
  email?: string | null
  telephone?: string | null
  adresse?: string | null
  date_embauche: string
  salaire_base: string
  devise_id?: number | null
  compte_bancaire?: string | null
  banque?: string | null
  actif: boolean
  created_at: string
}

// --- Types de congé ---
export interface TypeCongeCreate {
  entreprise_id: number
  code: string
  libelle: string
  paye?: boolean
  actif?: boolean
}

export interface TypeCongeUpdate {
  code?: string | null
  libelle?: string | null
  paye?: boolean | null
  actif?: boolean | null
}

export interface TypeCongeResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  paye: boolean
  actif: boolean
  created_at: string
}

// --- Demandes de congé ---
export interface DemandeCongeCreate {
  entreprise_id: number
  employe_id: number
  type_conge_id: number
  date_debut: string
  date_fin: string
  nombre_jours: number
  statut?: string
  motif?: string | null
}

export interface DemandeCongeUpdate {
  statut?: string | null
  commentaire_refus?: string | null
}

export interface DemandeCongeResponse {
  id: number
  entreprise_id: number
  employe_id: number
  type_conge_id: number
  date_debut: string
  date_fin: string
  nombre_jours: number
  statut: string
  motif?: string | null
  commentaire_refus?: string | null
  approuve_par_id?: number | null
  date_decision?: string | null
  created_by_id?: number | null
  created_at: string
}

// --- Soldes de congé ---
export interface SoldeCongeCreate {
  entreprise_id: number
  employe_id: number
  type_conge_id: number
  annee: number
  droits_acquis?: number
  jours_pris?: number
}

export interface SoldeCongeUpdate {
  droits_acquis?: number | null
  jours_pris?: number | null
}

export interface SoldeCongeResponse {
  id: number
  entreprise_id: number
  employe_id: number
  type_conge_id: number
  annee: number
  droits_acquis: number
  jours_pris: number
  created_at: string
}

// --- Objectifs ---
export interface ObjectifCreate {
  entreprise_id: number
  employe_id: number
  libelle: string
  date_debut: string
  date_fin: string
  montant_cible?: number | string
  atteint?: boolean
}

export interface ObjectifUpdate {
  libelle?: string | null
  date_fin?: string | null
  montant_cible?: number | string | null
  atteint?: boolean | null
}

export interface ObjectifResponse {
  id: number
  entreprise_id: number
  employe_id: number
  libelle: string
  date_debut: string
  date_fin: string
  montant_cible: string
  atteint: boolean
  created_at: string
}

// --- Taux de commission ---
export interface TauxCommissionCreate {
  entreprise_id: number
  code: string
  libelle: string
  taux_pct?: number | string
  actif?: boolean
}

export interface TauxCommissionUpdate {
  code?: string | null
  libelle?: string | null
  taux_pct?: number | string | null
  actif?: boolean | null
}

export interface TauxCommissionResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  taux_pct: string
  actif: boolean
  created_at: string
}

// --- Commissions ---
export interface CommissionCreate {
  entreprise_id: number
  employe_id: number
  taux_commission_id?: number | null
  date_debut: string
  date_fin: string
  montant?: number | string
  libelle?: string | null
  payee?: boolean
}

export interface CommissionUpdate {
  montant?: number | string | null
  libelle?: string | null
  payee?: boolean | null
}

export interface CommissionResponse {
  id: number
  entreprise_id: number
  employe_id: number
  taux_commission_id?: number | null
  date_debut: string
  date_fin: string
  montant: string
  libelle?: string | null
  payee: boolean
  created_at: string
}

// --- Avances ---
export interface AvanceCreate {
  entreprise_id: number
  employe_id: number
  date_avance: string
  montant: number | string
  motif?: string | null
  rembourse?: boolean
}

export interface AvanceUpdate {
  motif?: string | null
  rembourse?: boolean | null
}

export interface AvanceResponse {
  id: number
  entreprise_id: number
  employe_id: number
  date_avance: string
  montant: string
  motif?: string | null
  rembourse: boolean
  created_by_id?: number | null
  created_at: string
}
