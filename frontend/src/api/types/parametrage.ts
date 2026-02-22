/**
 * Types Paramétrage – alignés sur l'OpenAPI Gesco.
 */

// --- Entreprises ---
export type RegimeFiscal = 'informel' | 'liberatoire' | 'forfait' | 'reel_simplifie' | 'reel_normal'
export type ModeGestion = 'standard' | 'simplifie'
export type FormeJuridique = 'sarl' | 'sa' | 'sas' | 'snc' | 'scs' | 'eurl' | 'ei' | 'gie' | 'association' | 'cooperative' | 'autre'

export interface EntrepriseCreate {
  code: string
  raison_sociale: string
  sigle?: string | null
  niu?: string | null
  regime_fiscal: RegimeFiscal
  mode_gestion: ModeGestion
  forme_juridique?: FormeJuridique | null
  rccm?: string | null
  cnps?: string | null
  adresse?: string | null
  code_postal?: string | null
  boite_postale?: string | null
  ville?: string | null
  region?: string | null
  pays?: string
  fuseau_horaire?: string | null
  telephone?: string | null
  email?: string | null
  site_web?: string | null
  devise_principale?: string
  date_creation?: string | null
  capital_social?: number | string | null
  logo_url?: string | null
  actif?: boolean
}

export interface EntrepriseUpdate {
  raison_sociale?: string | null
  sigle?: string | null
  niu?: string | null
  regime_fiscal?: RegimeFiscal | null
  mode_gestion?: ModeGestion | null
  forme_juridique?: FormeJuridique | null
  rccm?: string | null
  cnps?: string | null
  adresse?: string | null
  code_postal?: string | null
  boite_postale?: string | null
  ville?: string | null
  region?: string | null
  pays?: string | null
  fuseau_horaire?: string | null
  telephone?: string | null
  email?: string | null
  site_web?: string | null
  devise_principale?: string | null
  date_creation?: string | null
  capital_social?: number | string | null
  logo_url?: string | null
  actif?: boolean | null
}

export interface EntrepriseResponse {
  id: number
  code: string
  raison_sociale: string
  sigle?: string | null
  niu?: string | null
  regime_fiscal: string
  mode_gestion: string
  forme_juridique?: string | null
  rccm?: string | null
  cnps?: string | null
  ville?: string | null
  region?: string | null
  pays: string
  fuseau_horaire?: string | null
  devise_principale: string
  date_creation?: string | null
  capital_social?: string | null
  actif: boolean
  created_at: string
  updated_at: string
}

/** Réponse paginée de la liste des entreprises. */
export interface ListEntreprisesResponse {
  items: EntrepriseResponse[]
  total: number
}

/** Statistiques globales entreprises (total, actives, inactives, répartition par régime et pays). */
export interface EntrepriseStatsResponse {
  total: number
  actives: number
  inactives: number
  par_regime_fiscal: Record<string, number>
  par_pays: Record<string, number>
}

// --- Devises ---
export interface DeviseCreate {
  code: string
  libelle: string
  symbole?: string | null
  decimales?: number
  actif?: boolean
}

export interface DeviseUpdate {
  libelle?: string | null
  symbole?: string | null
  decimales?: number | null
  actif?: boolean | null
}

export interface DeviseResponse {
  id: number
  code: string
  libelle: string
  symbole?: string | null
  decimales: number
  actif: boolean
}

export interface ListDevisesResponse {
  items: DeviseResponse[]
  total: number
}

export interface DeviseStatsResponse {
  total: number
  actives: number
  inactives: number
}

// --- Taux de change ---
export interface TauxChangeCreate {
  devise_from_id: number
  devise_to_id: number
  taux: number | string
  date_effet: string
  source?: string | null
}

export interface TauxChangeUpdate {
  taux?: number | string | null
  source?: string | null
}

export interface TauxChangeResponse {
  id: number
  devise_from_id: number
  devise_to_id: number
  taux: string
  date_effet: string
  source?: string | null
  created_at: string
}

export interface ListTauxChangeResponse {
  items: TauxChangeResponse[]
  total: number
}

export interface TauxChangeStatsResponse {
  total: number
}

// --- Points de vente ---
export type TypePointDeVente = 'principal' | 'secondaire' | 'depot'

export interface PointDeVenteCreate {
  entreprise_id: number
  code: string
  libelle: string
  type: TypePointDeVente
  adresse?: string | null
  code_postal?: string | null
  ville?: string | null
  telephone?: string | null
  latitude?: number | string | null
  longitude?: number | string | null
  fuseau_horaire?: string | null
  est_depot?: boolean
  actif?: boolean
}

export interface PointDeVenteUpdate {
  code?: string | null
  libelle?: string | null
  type?: TypePointDeVente | null
  adresse?: string | null
  code_postal?: string | null
  ville?: string | null
  telephone?: string | null
  latitude?: number | string | null
  longitude?: number | string | null
  fuseau_horaire?: string | null
  est_depot?: boolean | null
  actif?: boolean | null
}

export interface PointDeVenteResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  type: string
  adresse?: string | null
  ville?: string | null
  code_postal?: string | null
  telephone?: string | null
  latitude?: string | null
  longitude?: string | null
  fuseau_horaire?: string | null
  est_depot: boolean
  actif: boolean
  created_at: string
  updated_at: string
}

export interface ListPointsVenteResponse {
  items: PointDeVenteResponse[]
  total: number
}

export interface PointVenteStatsResponse {
  total: number
  actifs: number
  inactifs: number
  par_type: Record<string, number>
}

// --- Rôles ---
export interface RoleCreate {
  entreprise_id?: number | null
  code: string
  libelle: string
}

export interface RoleUpdate {
  code?: string | null
  libelle?: string | null
}

export interface RoleResponse {
  id: number
  entreprise_id?: number | null
  code: string
  libelle: string
  created_at: string
  updated_at: string
}

// --- Permissions ---
export interface PermissionCreate {
  module: string
  action: string
  libelle: string
}

export interface PermissionResponse {
  id: number
  module: string
  action: string
  libelle: string
}

export interface RoleMinimal {
  id: number
  code: string
  libelle?: string
}

export interface PermissionWithRolesResponse extends PermissionResponse {
  roles: RoleMinimal[]
}

export interface PermissionRoleCreate {
  role_id: number
  permission_id: number
}

export interface PermissionRoleResponse {
  id: number
  role_id: number
  permission_id: number
}

// --- Utilisateurs ---
export interface UtilisateurCreate {
  entreprise_id: number
  point_de_vente_id?: number | null
  role_id: number
  login: string
  mot_de_passe: string
  email?: string | null
  nom: string
  prenom?: string | null
  telephone?: string | null
  actif?: boolean
}

export interface UtilisateurUpdate {
  point_de_vente_id?: number | null
  role_id?: number | null
  email?: string | null
  nom?: string | null
  prenom?: string | null
  telephone?: string | null
  actif?: boolean | null
  mot_de_passe?: string | null
}

export interface UtilisateurResponse {
  id: number
  entreprise_id: number
  point_de_vente_id?: number | null
  role_id: number
  login: string
  email?: string | null
  nom: string
  prenom?: string | null
  telephone?: string | null
  actif: boolean
  derniere_connexion_at?: string | null
  created_at: string
  updated_at: string
}

/** Corps pour le changement de mot de passe (par soi-même ou par un admin). */
export interface UtilisateurChangePasswordBody {
  /** Requis si l'utilisateur change son propre mot de passe. */
  ancien_mot_de_passe?: string | null
  nouveau_mot_de_passe: string
}

// --- Affectations utilisateur-PDV ---
export interface AffectationUtilisateurPdvCreate {
  utilisateur_id: number
  point_de_vente_id: number
  est_principal?: boolean
}

export interface AffectationUtilisateurPdvUpdate {
  est_principal?: boolean | null
}

export interface AffectationUtilisateurPdvResponse {
  id: number
  utilisateur_id: number
  point_de_vente_id: number
  est_principal: boolean
}
