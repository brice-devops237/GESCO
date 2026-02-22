/**
 * Types Partenaires – reflet du monde réel.
 * Types de tiers (client, fournisseur, etc.), Tiers (identification légale, adresse, commercial, paiement), Contacts.
 */

// --- Types de tiers (référentiel) ---
/** Création d'un type de tiers (ex. Client, Fournisseur, Prospect). */
export interface TypeTiersCreate {
  code: string
  libelle: string
}

/** Mise à jour partielle d'un type de tiers. */
export interface TypeTiersUpdate {
  code?: string | null
  libelle?: string | null
}

/** Type de tiers : catégorie du partenaire (client, fournisseur, etc.). */
export interface TypeTiersResponse {
  id: number
  code: string
  libelle: string
}

// --- Tiers (clients, fournisseurs) – identification légale, adresse, commercial, paiement ---
/** Création d'un tiers : entreprise partenaire (client ou fournisseur). */
export interface TiersCreate {
  entreprise_id: number
  type_tiers_id: number
  code: string
  raison_sociale: string
  sigle?: string | null
  nom_contact?: string | null
  niu?: string | null
  rccm?: string | null
  adresse?: string | null
  code_postal?: string | null
  boite_postale?: string | null
  ville?: string | null
  region?: string | null
  pays?: string
  telephone?: string | null
  telephone_secondaire?: string | null
  email?: string | null
  canal_vente_id?: number | null
  limite_credit?: number | string | null
  delai_paiement_jours?: number | null
  compte_bancaire?: string | null
  mobile_money_numero?: string | null
  mobile_money_operateur?: string | null
  segment?: string | null
  notes?: string | null
  actif?: boolean
}

/** Mise à jour partielle d'un tiers. */
export interface TiersUpdate {
  type_tiers_id?: number | null
  code?: string | null
  raison_sociale?: string | null
  sigle?: string | null
  nom_contact?: string | null
  niu?: string | null
  rccm?: string | null
  adresse?: string | null
  code_postal?: string | null
  boite_postale?: string | null
  ville?: string | null
  region?: string | null
  pays?: string | null
  telephone?: string | null
  telephone_secondaire?: string | null
  email?: string | null
  canal_vente_id?: number | null
  limite_credit?: number | string | null
  delai_paiement_jours?: number | null
  compte_bancaire?: string | null
  mobile_money_numero?: string | null
  mobile_money_operateur?: string | null
  segment?: string | null
  notes?: string | null
  actif?: boolean | null
}

/** Tiers : partenaire (client ou fournisseur) avec identification légale, adresse, conditions commerciales et moyens de paiement. */
export interface TiersResponse {
  id: number
  entreprise_id: number
  type_tiers_id: number
  code: string
  raison_sociale: string
  sigle?: string | null
  nom_contact?: string | null
  niu?: string | null
  rccm?: string | null
  adresse?: string | null
  code_postal?: string | null
  boite_postale?: string | null
  ville?: string | null
  region?: string | null
  pays: string
  telephone?: string | null
  telephone_secondaire?: string | null
  email?: string | null
  canal_vente_id?: number | null
  limite_credit?: string | null
  delai_paiement_jours?: number | null
  compte_bancaire?: string | null
  mobile_money_numero?: string | null
  mobile_money_operateur?: string | null
  segment?: string | null
  notes?: string | null
  actif: boolean
  created_at: string
  updated_at: string
}

// --- Contacts (personnes rattachées à un tiers) ---
/** Création d'un contact : interlocuteur d'un tiers (civilité pour courriers et factures). */
export interface ContactCreate {
  tiers_id: number
  civilite?: string | null
  nom: string
  prenom?: string | null
  fonction?: string | null
  telephone?: string | null
  email?: string | null
  est_principal?: boolean
  actif?: boolean
}

/** Mise à jour partielle d'un contact. */
export interface ContactUpdate {
  civilite?: string | null
  nom?: string | null
  prenom?: string | null
  fonction?: string | null
  telephone?: string | null
  email?: string | null
  est_principal?: boolean | null
  actif?: boolean | null
}

/** Contact : interlocuteur d'un tiers (nom, fonction, coordonnées, contact principal). */
export interface ContactResponse {
  id: number
  tiers_id: number
  civilite?: string | null
  nom: string
  prenom?: string | null
  fonction?: string | null
  telephone?: string | null
  email?: string | null
  est_principal: boolean
  actif: boolean
  created_at: string
  updated_at: string
}
