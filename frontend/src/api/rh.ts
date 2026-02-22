/**
 * API RH – alignée sur le backend (Bearer requis).
 * Départements, Postes, Types contrat, Employés, Types congé, Demandes congé,
 * Soldes congé, Objectifs, Taux commission, Commissions, Avances.
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  DepartementCreate,
  DepartementUpdate,
  DepartementResponse,
  PosteCreate,
  PosteUpdate,
  PosteResponse,
  TypeContratCreate,
  TypeContratUpdate,
  TypeContratResponse,
  EmployeCreate,
  EmployeUpdate,
  EmployeResponse,
  TypeCongeCreate,
  TypeCongeUpdate,
  TypeCongeResponse,
  DemandeCongeCreate,
  DemandeCongeUpdate,
  DemandeCongeResponse,
  SoldeCongeCreate,
  SoldeCongeUpdate,
  SoldeCongeResponse,
  ObjectifCreate,
  ObjectifUpdate,
  ObjectifResponse,
  TauxCommissionCreate,
  TauxCommissionUpdate,
  TauxCommissionResponse,
  CommissionCreate,
  CommissionUpdate,
  CommissionResponse,
  AvanceCreate,
  AvanceUpdate,
  AvanceResponse,
} from './types/rh'

const PREFIX = '/api/v1/rh'

// --- Départements ---
export interface ListDepartementsParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listDepartements(params: ListDepartementsParams): Promise<DepartementResponse[]> {
  return authenticatedRequest<DepartementResponse[]>(`${PREFIX}/departements${toQuery(params)}`)
}
export function getDepartement(id: number): Promise<DepartementResponse> {
  return authenticatedRequest<DepartementResponse>(`${PREFIX}/departements/${id}`)
}
export function createDepartement(body: DepartementCreate): Promise<DepartementResponse> {
  return authenticatedRequest<DepartementResponse>(`${PREFIX}/departements`, { method: 'POST', body })
}
export function updateDepartement(id: number, body: DepartementUpdate): Promise<DepartementResponse> {
  return authenticatedRequest<DepartementResponse>(`${PREFIX}/departements/${id}`, { method: 'PATCH', body })
}

// --- Postes ---
export interface ListPostesParams {
  entreprise_id: number
  departement_id?: number | null
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listPostes(params: ListPostesParams): Promise<PosteResponse[]> {
  return authenticatedRequest<PosteResponse[]>(`${PREFIX}/postes${toQuery(params)}`)
}
export function getPoste(id: number): Promise<PosteResponse> {
  return authenticatedRequest<PosteResponse>(`${PREFIX}/postes/${id}`)
}
export function createPoste(body: PosteCreate): Promise<PosteResponse> {
  return authenticatedRequest<PosteResponse>(`${PREFIX}/postes`, { method: 'POST', body })
}
export function updatePoste(id: number, body: PosteUpdate): Promise<PosteResponse> {
  return authenticatedRequest<PosteResponse>(`${PREFIX}/postes/${id}`, { method: 'PATCH', body })
}

// --- Types de contrat ---
export interface ListTypesContratParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listTypesContrat(params: ListTypesContratParams): Promise<TypeContratResponse[]> {
  return authenticatedRequest<TypeContratResponse[]>(`${PREFIX}/types-contrat${toQuery(params)}`)
}
export function getTypeContrat(id: number): Promise<TypeContratResponse> {
  return authenticatedRequest<TypeContratResponse>(`${PREFIX}/types-contrat/${id}`)
}
export function createTypeContrat(body: TypeContratCreate): Promise<TypeContratResponse> {
  return authenticatedRequest<TypeContratResponse>(`${PREFIX}/types-contrat`, { method: 'POST', body })
}
export function updateTypeContrat(id: number, body: TypeContratUpdate): Promise<TypeContratResponse> {
  return authenticatedRequest<TypeContratResponse>(`${PREFIX}/types-contrat/${id}`, { method: 'PATCH', body })
}

// --- Employés ---
export interface ListEmployesParams {
  entreprise_id: number
  actif_only?: boolean
  departement_id?: number | null
  poste_id?: number | null
  skip?: number
  limit?: number
}
export function listEmployes(params: ListEmployesParams): Promise<EmployeResponse[]> {
  return authenticatedRequest<EmployeResponse[]>(`${PREFIX}/employes${toQuery(params)}`)
}
export function getEmploye(id: number): Promise<EmployeResponse> {
  return authenticatedRequest<EmployeResponse>(`${PREFIX}/employes/${id}`)
}
export function createEmploye(body: EmployeCreate): Promise<EmployeResponse> {
  return authenticatedRequest<EmployeResponse>(`${PREFIX}/employes`, { method: 'POST', body })
}
export function updateEmploye(id: number, body: EmployeUpdate): Promise<EmployeResponse> {
  return authenticatedRequest<EmployeResponse>(`${PREFIX}/employes/${id}`, { method: 'PATCH', body })
}

// --- Types de congé ---
export interface ListTypesCongeParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listTypesConge(params: ListTypesCongeParams): Promise<TypeCongeResponse[]> {
  return authenticatedRequest<TypeCongeResponse[]>(`${PREFIX}/types-conge${toQuery(params)}`)
}
export function getTypeConge(id: number): Promise<TypeCongeResponse> {
  return authenticatedRequest<TypeCongeResponse>(`${PREFIX}/types-conge/${id}`)
}
export function createTypeConge(body: TypeCongeCreate): Promise<TypeCongeResponse> {
  return authenticatedRequest<TypeCongeResponse>(`${PREFIX}/types-conge`, { method: 'POST', body })
}
export function updateTypeConge(id: number, body: TypeCongeUpdate): Promise<TypeCongeResponse> {
  return authenticatedRequest<TypeCongeResponse>(`${PREFIX}/types-conge/${id}`, { method: 'PATCH', body })
}

// --- Demandes de congé ---
export interface ListDemandesCongeParams {
  entreprise_id: number
  employe_id?: number | null
  statut?: string | null
  skip?: number
  limit?: number
}
export function listDemandesConge(params: ListDemandesCongeParams): Promise<DemandeCongeResponse[]> {
  return authenticatedRequest<DemandeCongeResponse[]>(`${PREFIX}/demandes-conge${toQuery(params)}`)
}
export function getDemandeConge(id: number): Promise<DemandeCongeResponse> {
  return authenticatedRequest<DemandeCongeResponse>(`${PREFIX}/demandes-conge/${id}`)
}
export function createDemandeConge(body: DemandeCongeCreate): Promise<DemandeCongeResponse> {
  return authenticatedRequest<DemandeCongeResponse>(`${PREFIX}/demandes-conge`, { method: 'POST', body })
}
export function updateDemandeConge(id: number, body: DemandeCongeUpdate): Promise<DemandeCongeResponse> {
  return authenticatedRequest<DemandeCongeResponse>(`${PREFIX}/demandes-conge/${id}`, { method: 'PATCH', body })
}

// --- Soldes de congé ---
export interface ListSoldesCongeParams {
  entreprise_id: number
  employe_id?: number | null
  annee?: number | null
  skip?: number
  limit?: number
}
export function listSoldesConge(params: ListSoldesCongeParams): Promise<SoldeCongeResponse[]> {
  return authenticatedRequest<SoldeCongeResponse[]>(`${PREFIX}/soldes-conge${toQuery(params)}`)
}
export function getSoldeConge(id: number): Promise<SoldeCongeResponse> {
  return authenticatedRequest<SoldeCongeResponse>(`${PREFIX}/soldes-conge/${id}`)
}
export function createSoldeConge(body: SoldeCongeCreate): Promise<SoldeCongeResponse> {
  return authenticatedRequest<SoldeCongeResponse>(`${PREFIX}/soldes-conge`, { method: 'POST', body })
}
export function updateSoldeConge(id: number, body: SoldeCongeUpdate): Promise<SoldeCongeResponse> {
  return authenticatedRequest<SoldeCongeResponse>(`${PREFIX}/soldes-conge/${id}`, { method: 'PATCH', body })
}

// --- Objectifs ---
export interface ListObjectifsParams {
  entreprise_id: number
  employe_id?: number | null
  skip?: number
  limit?: number
}
export function listObjectifs(params: ListObjectifsParams): Promise<ObjectifResponse[]> {
  return authenticatedRequest<ObjectifResponse[]>(`${PREFIX}/objectifs${toQuery(params)}`)
}
export function getObjectif(id: number): Promise<ObjectifResponse> {
  return authenticatedRequest<ObjectifResponse>(`${PREFIX}/objectifs/${id}`)
}
export function createObjectif(body: ObjectifCreate): Promise<ObjectifResponse> {
  return authenticatedRequest<ObjectifResponse>(`${PREFIX}/objectifs`, { method: 'POST', body })
}
export function updateObjectif(id: number, body: ObjectifUpdate): Promise<ObjectifResponse> {
  return authenticatedRequest<ObjectifResponse>(`${PREFIX}/objectifs/${id}`, { method: 'PATCH', body })
}

// --- Taux de commission ---
export interface ListTauxCommissionsParams {
  entreprise_id: number
  actif_only?: boolean
  skip?: number
  limit?: number
}
export function listTauxCommissions(params: ListTauxCommissionsParams): Promise<TauxCommissionResponse[]> {
  return authenticatedRequest<TauxCommissionResponse[]>(`${PREFIX}/taux-commissions${toQuery(params)}`)
}
export function getTauxCommission(id: number): Promise<TauxCommissionResponse> {
  return authenticatedRequest<TauxCommissionResponse>(`${PREFIX}/taux-commissions/${id}`)
}
export function createTauxCommission(body: TauxCommissionCreate): Promise<TauxCommissionResponse> {
  return authenticatedRequest<TauxCommissionResponse>(`${PREFIX}/taux-commissions`, { method: 'POST', body })
}
export function updateTauxCommission(id: number, body: TauxCommissionUpdate): Promise<TauxCommissionResponse> {
  return authenticatedRequest<TauxCommissionResponse>(`${PREFIX}/taux-commissions/${id}`, { method: 'PATCH', body })
}

// --- Commissions ---
export interface ListCommissionsParams {
  entreprise_id: number
  employe_id?: number | null
  payee?: boolean | null
  skip?: number
  limit?: number
}
export function listCommissions(params: ListCommissionsParams): Promise<CommissionResponse[]> {
  return authenticatedRequest<CommissionResponse[]>(`${PREFIX}/commissions${toQuery(params)}`)
}
export function getCommission(id: number): Promise<CommissionResponse> {
  return authenticatedRequest<CommissionResponse>(`${PREFIX}/commissions/${id}`)
}
export function createCommission(body: CommissionCreate): Promise<CommissionResponse> {
  return authenticatedRequest<CommissionResponse>(`${PREFIX}/commissions`, { method: 'POST', body })
}
export function updateCommission(id: number, body: CommissionUpdate): Promise<CommissionResponse> {
  return authenticatedRequest<CommissionResponse>(`${PREFIX}/commissions/${id}`, { method: 'PATCH', body })
}

// --- Avances ---
export interface ListAvancesParams {
  entreprise_id: number
  employe_id?: number | null
  rembourse?: boolean | null
  skip?: number
  limit?: number
}
export function listAvances(params: ListAvancesParams): Promise<AvanceResponse[]> {
  return authenticatedRequest<AvanceResponse[]>(`${PREFIX}/avances${toQuery(params)}`)
}
export function getAvance(id: number): Promise<AvanceResponse> {
  return authenticatedRequest<AvanceResponse>(`${PREFIX}/avances/${id}`)
}
export function createAvance(body: AvanceCreate): Promise<AvanceResponse> {
  return authenticatedRequest<AvanceResponse>(`${PREFIX}/avances`, { method: 'POST', body })
}
export function updateAvance(id: number, body: AvanceUpdate): Promise<AvanceResponse> {
  return authenticatedRequest<AvanceResponse>(`${PREFIX}/avances/${id}`, { method: 'PATCH', body })
}
