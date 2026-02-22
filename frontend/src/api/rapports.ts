/**
 * API Rapports – alignée sur le backend (Bearer requis).
 * Chiffre d'affaires, Dashboard.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type { ChiffreAffairesPeriode, SyntheseDashboard } from './types/rapports'

const PREFIX = '/api/v1/rapports'

export interface ChiffreAffairesParams {
  entreprise_id: number
  date_debut: string
  date_fin: string
}

export function getChiffreAffaires(params: ChiffreAffairesParams): Promise<ChiffreAffairesPeriode> {
  return authenticatedRequest<ChiffreAffairesPeriode>(`${PREFIX}/chiffre-affaires${toQuery(params)}`)
}

export interface DashboardParams {
  entreprise_id: number
  date_debut?: string | null
  date_fin?: string | null
}

export function getDashboard(params: DashboardParams): Promise<SyntheseDashboard> {
  return authenticatedRequest<SyntheseDashboard>(`${PREFIX}/dashboard${toQuery(params)}`)
}
