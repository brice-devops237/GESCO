/**
 * Types Achats – reflet du monde réel.
 * Dépôts (entrepôts), commandes fournisseurs, réceptions marchandises, factures fournisseurs.
 */

// --- Dépôt (entrepôt / lieu de stockage) ---
/** Création d'un dépôt : lieu de stockage (entrepôt, magasin, site). */
export interface DepotCreate {
  entreprise_id: number
  code: string
  libelle: string
  adresse?: string | null
  ville?: string | null
  code_postal?: string | null
  pays?: string | null
  point_de_vente_id?: number | null
}

/** Mise à jour partielle d'un dépôt. */
export interface DepotUpdate {
  code?: string | null
  libelle?: string | null
  adresse?: string | null
  ville?: string | null
  code_postal?: string | null
  pays?: string | null
  point_de_vente_id?: number | null
}

/** Dépôt : entrepôt ou lieu de stockage (multi-sites, logistique). */
export interface DepotResponse {
  id: number
  entreprise_id: number
  code: string
  libelle: string
  adresse?: string | null
  ville?: string | null
  code_postal?: string | null
  pays?: string | null
  point_de_vente_id?: number | null
}

// --- Commande fournisseur (commande d'achat) ---
/** Création d'une commande fournisseur : commande d'achat auprès d'un fournisseur. */
export interface CommandeFournisseurCreate {
  entreprise_id: number
  fournisseur_id: number
  depot_id?: number | null
  numero: string
  numero_fournisseur?: string | null
  date_commande: string
  date_livraison_prevue?: string | null
  delai_livraison_jours?: number | null
  etat_id: number
  montant_ht?: number | string
  montant_tva?: number | string
  montant_ttc?: number | string
  devise_id: number
  notes?: string | null
}

/** Mise à jour partielle d'une commande fournisseur. */
export interface CommandeFournisseurUpdate {
  depot_id?: number | null
  date_livraison_prevue?: string | null
  delai_livraison_jours?: number | null
  etat_id?: number | null
  notes?: string | null
}

/** Commande fournisseur : commande d'achat (n° interne, fournisseur, dates, montants, devise, état). */
export interface CommandeFournisseurResponse {
  id: number
  entreprise_id: number
  fournisseur_id: number
  depot_id?: number | null
  numero: string
  numero_fournisseur?: string | null
  date_commande: string
  date_livraison_prevue?: string | null
  delai_livraison_jours?: number | null
  etat_id: number
  montant_ht: string
  montant_tva: string
  montant_ttc: string
  devise_id: number
  notes?: string | null
  created_at: string
}

// --- Réception (livraison fournisseur / bon de réception) ---
/** Création d'une réception : entrée marchandise liée à une commande fournisseur. */
export interface ReceptionCreate {
  commande_fournisseur_id: number
  depot_id: number
  numero: string
  numero_bl_fournisseur?: string | null
  date_reception: string
  etat?: string
  notes?: string | null
}

/** Mise à jour partielle d'une réception. */
export interface ReceptionUpdate {
  numero_bl_fournisseur?: string | null
  etat?: string | null
  notes?: string | null
}

/** Réception : bon de réception (livraison fournisseur, dépôt de destination, n° BL fournisseur). */
export interface ReceptionResponse {
  id: number
  commande_fournisseur_id: number
  depot_id: number
  numero: string
  numero_bl_fournisseur?: string | null
  date_reception: string
  etat: string
  notes?: string | null
  created_at: string
}

// --- Facture fournisseur ---
/** Création d'une facture fournisseur : facture d'achat (facture, avoir, proforma). */
export interface FactureFournisseurCreate {
  entreprise_id: number
  fournisseur_id: number
  commande_fournisseur_id?: number | null
  numero_fournisseur: string
  type_facture?: string
  date_facture: string
  date_echeance?: string | null
  date_reception_facture?: string | null
  montant_ht?: number | string
  montant_tva?: number | string
  montant_ttc?: number | string
  montant_restant_du?: number | string
  devise_id: number
  statut_paiement?: string
  notes?: string | null
}

/** Mise à jour partielle d'une facture fournisseur. */
export interface FactureFournisseurUpdate {
  type_facture?: string | null
  date_echeance?: string | null
  date_reception_facture?: string | null
  montant_restant_du?: number | string | null
  statut_paiement?: string | null
  notes?: string | null
}

/** Facture fournisseur : facture d'achat (n° fournisseur, type facture/avoir/proforma, échéance, restant dû). */
export interface FactureFournisseurResponse {
  id: number
  entreprise_id: number
  fournisseur_id: number
  commande_fournisseur_id?: number | null
  numero_fournisseur: string
  type_facture: string
  date_facture: string
  date_echeance?: string | null
  date_reception_facture?: string | null
  montant_ttc: string
  montant_restant_du: string
  statut_paiement: string
  created_at: string
}
