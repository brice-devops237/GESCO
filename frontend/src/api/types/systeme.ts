/**
 * Types Système – alignés sur l'OpenAPI Gesco.
 */

// --- Paramètres système ---
export interface ParametreSystemeCreate {
  entreprise_id: number
  categorie: string
  cle: string
  valeur?: string | null
  description?: string | null
}

export interface ParametreSystemeUpdate {
  valeur?: string | null
  description?: string | null
}

export interface ParametreSystemeResponse {
  id: number
  entreprise_id: number
  categorie: string
  cle: string
  valeur?: string | null
  description?: string | null
  created_at: string
  updated_at: string
}

// --- Journal d'audit ---
export interface JournalAuditCreate {
  entreprise_id?: number | null
  utilisateur_id?: number | null
  action: string
  module?: string | null
  entite_type?: string | null
  entite_id?: number | null
  details?: Record<string, unknown> | null
  ip_address?: string | null
  user_agent?: string | null
}

export interface JournalAuditResponse {
  id: number
  entreprise_id?: number | null
  utilisateur_id?: number | null
  action: string
  module?: string | null
  entite_type?: string | null
  entite_id?: number | null
  details?: Record<string, unknown> | null
  ip_address?: string | null
  user_agent?: string | null
  created_at: string
}

// --- Notifications ---
export interface NotificationCreate {
  utilisateur_id: number
  titre: string
  message?: string | null
  entite_type?: string | null
  entite_id?: number | null
}

export interface NotificationUpdate {
  lue?: boolean | null
}

export interface NotificationResponse {
  id: number
  utilisateur_id: number
  titre: string
  message?: string | null
  lue: boolean
  entite_type?: string | null
  entite_id?: number | null
  created_at: string
}

// --- Licences logicielles ---
export interface LicenceLogicielleCreate {
  entreprise_id: number
  cle_licence: string
  type_licence?: string
  date_debut: string
}

export interface LicenceLogicielleUpdate {
  type_licence?: string | null
  date_fin?: string | null
  actif?: boolean | null
}

export interface LicenceLogicielleResponse {
  id: number
  entreprise_id: number
  cle_licence: string
  type_licence: string
  date_debut: string
  date_fin: string
  actif: boolean
  nombre_prolongations?: number
  date_activation?: string | null
  created_at: string
  updated_at: string
}

export interface LicenceValideResponse {
  valide: boolean
  message: string
  date_fin?: string | null
}

export interface LicenceProlongationsInfo {
  type_licence: string
  nombre_prolongations: number
  prolongations_restantes?: number | null
  duree_ajoutee_mois: number
}
