/**
 * Types Commercial – alignés sur l'OpenAPI Gesco.
 */

// --- États document ---
export interface EtatDocumentCreate {
  type_document: string
  code: string
  libelle: string
  ordre?: number
}

export interface EtatDocumentUpdate {
  code?: string | null
  libelle?: string | null
  ordre?: number | null
}

export interface EtatDocumentResponse {
  id: number
  type_document: string
  code: string
  libelle: string
  ordre: number
}

// --- Devis ---
export interface DevisCreate {
  entreprise_id: number
  point_de_vente_id?: number | null
  client_id: number
  reference_client?: string | null
  numero: string
  date_devis: string
  date_validite?: string | null
  etat_id: number
  montant_ht?: number | string
  montant_tva?: number | string
  montant_ttc?: number | string
  remise_globale_pct?: number | string
  remise_globale_montant?: number | string
  devise_id: number
  taux_change?: number | string
  notes?: string | null
  conditions_generales?: string | null
}

export interface DevisUpdate {
  reference_client?: string | null
  point_de_vente_id?: number | null
  date_validite?: string | null
  etat_id?: number | null
  montant_ht?: number | string | null
  montant_tva?: number | string | null
  montant_ttc?: number | string | null
  notes?: string | null
}

export interface DevisResponse {
  id: number
  entreprise_id: number
  client_id: number
  reference_client?: string | null
  numero: string
  date_devis: string
  etat_id: number
  montant_ttc: string
  created_at: string
}

// --- Commandes ---
export interface CommandeCreate {
  entreprise_id: number
  point_de_vente_id: number
  client_id: number
  devis_id?: number | null
  numero: string
  reference_client?: string | null
  date_commande: string
  date_livraison_prevue?: string | null
  etat_id: number
  montant_ht?: number | string
  montant_tva?: number | string
  montant_ttc?: number | string
  devise_id: number
  adresse_livraison?: string | null
  notes?: string | null
}

export interface CommandeUpdate {
  reference_client?: string | null
  date_livraison_prevue?: string | null
  etat_id?: number | null
  adresse_livraison?: string | null
  notes?: string | null
}

export interface CommandeResponse {
  id: number
  entreprise_id: number
  point_de_vente_id: number
  client_id: number
  numero: string
  reference_client?: string | null
  date_commande: string
  etat_id: number
  montant_ttc: string
  created_at: string
}

// --- Factures ---
/** Type facture (CGI) : facture, avoir, proforma, duplicata */
export type TypeFacture = 'facture' | 'avoir' | 'proforma' | 'duplicata'

export interface FactureCreate {
  entreprise_id: number
  point_de_vente_id: number
  client_id: number
  commande_id?: number | null
  numero: string
  date_facture: string
  date_echeance?: string | null
  etat_id: number
  /** facture | avoir | proforma | duplicata (défaut: facture) */
  type_facture?: TypeFacture
  montant_ht?: number | string
  montant_tva?: number | string
  montant_ttc?: number | string
  montant_restant_du?: number | string
  devise_id: number
  mention_legale?: string | null
  notes?: string | null
}

export interface FactureUpdate {
  date_echeance?: string | null
  etat_id?: number | null
  montant_restant_du?: number | string | null
  mention_legale?: string | null
  notes?: string | null
}

export interface FactureResponse {
  id: number
  entreprise_id: number
  client_id: number
  numero: string
  date_facture: string
  etat_id: number
  type_facture: string
  montant_ttc: string
  montant_restant_du: string
  mention_legale?: string | null
  created_at: string
}

// --- Bons de livraison ---
export interface BonLivraisonCreate {
  entreprise_id: number
  point_de_vente_id: number
  client_id: number
  commande_id?: number | null
  facture_id?: number | null
  numero: string
  date_livraison: string
  contact_livraison?: string | null
  adresse_livraison?: string | null
  etat_id: number
  notes?: string | null
}

export interface BonLivraisonUpdate {
  contact_livraison?: string | null
  adresse_livraison?: string | null
  etat_id?: number | null
  notes?: string | null
}

export interface BonLivraisonResponse {
  id: number
  entreprise_id: number
  client_id: number
  numero: string
  date_livraison: string
  contact_livraison?: string | null
  etat_id: number
  created_at: string
}
