/**
 * Types Rapports – alignés sur le backend Gesco (schemas Pydantic).
 */

export interface ChiffreAffairesPeriode {
  entreprise_id: number
  date_debut: string
  date_fin: string
  montant_total_ttc?: string
  nombre_factures?: number
}

/** Indicateurs stock (valeur, alertes) – backend rapports/schemas.IndicateurStock */
export interface IndicateurStock {
  entreprise_id: number
  nombre_articles?: number
  valeur_totale?: string | null
  articles_en_rupture?: number
}

export interface SyntheseDashboard {
  entreprise_id: number
  periode_label?: string | null
  ca_periode?: string
  nb_factures?: number
  nb_commandes?: number
  nb_employes_actifs?: number
}
