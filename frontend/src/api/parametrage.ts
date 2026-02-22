/**
 * API Paramétrage – alignée sur l'OpenAPI Gesco (Bearer requis).
 * Entreprises, devises, taux de change, points de vente, rôles, permissions, utilisateurs, affectations PDV.
 *
 * Pour la liste des entreprises en contexte authentifié : importer listEntreprises depuis ce module
 * (import { listEntreprises } from '@/api/parametrage'). La page de connexion utilise
 * getLoginEntreprises() depuis @/api/auth (endpoint public sans Bearer).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  EntrepriseCreate,
  EntrepriseUpdate,
  EntrepriseResponse,
  ListEntreprisesResponse,
  EntrepriseStatsResponse,
  DeviseCreate,
  DeviseUpdate,
  DeviseResponse,
  ListDevisesResponse,
  DeviseStatsResponse,
  TauxChangeCreate,
  TauxChangeUpdate,
  TauxChangeResponse,
  ListTauxChangeResponse,
  TauxChangeStatsResponse,
  PointDeVenteCreate,
  PointDeVenteUpdate,
  PointDeVenteResponse,
  RoleCreate,
  RoleUpdate,
  RoleResponse,
  PermissionCreate,
  PermissionResponse,
  PermissionWithRolesResponse,
  PermissionRoleCreate,
  PermissionRoleResponse,
  UtilisateurCreate,
  UtilisateurUpdate,
  UtilisateurResponse,
  UtilisateurChangePasswordBody,
  AffectationUtilisateurPdvCreate,
  AffectationUtilisateurPdvUpdate,
  AffectationUtilisateurPdvResponse,
} from './types/parametrage'

const PREFIX = '/api/v1/parametrage'

// --- Entreprises ---
export interface ListEntreprisesParams {
  skip?: number
  limit?: number
  actif_only?: boolean
  inactif_only?: boolean
  search?: string | null
}

export async function listEntreprises(params: ListEntreprisesParams = {}): Promise<ListEntreprisesResponse> {
  return authenticatedRequest<ListEntreprisesResponse>(`${PREFIX}/entreprises${toQuery(params)}`)
}

export async function getEntreprise(entrepriseId: number): Promise<EntrepriseResponse> {
  return authenticatedRequest<EntrepriseResponse>(`${PREFIX}/entreprises/${entrepriseId}`)
}

export async function getEntrepriseStats(): Promise<EntrepriseStatsResponse> {
  return authenticatedRequest<EntrepriseStatsResponse>(`${PREFIX}/entreprises/stats`)
}

export async function createEntreprise(body: EntrepriseCreate): Promise<EntrepriseResponse> {
  return authenticatedRequest<EntrepriseResponse>(`${PREFIX}/entreprises`, { method: 'POST', body })
}

export async function updateEntreprise(entrepriseId: number, body: EntrepriseUpdate): Promise<EntrepriseResponse> {
  return authenticatedRequest<EntrepriseResponse>(`${PREFIX}/entreprises/${entrepriseId}`, { method: 'PATCH', body })
}

export async function deleteEntreprise(entrepriseId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/entreprises/${entrepriseId}`, { method: 'DELETE' })
}

// --- Devises ---
export interface ListDevisesParams {
  skip?: number
  limit?: number
  actif_only?: boolean
  inactif_only?: boolean
  /** Recherche sur code, libellé, symbole (côté backend) */
  search?: string | null
  /** Filtrer par nombre de décimales (0–6, côté backend) */
  decimales?: number | null
}

export async function listDevises(params: ListDevisesParams = {}): Promise<ListDevisesResponse> {
  return authenticatedRequest<ListDevisesResponse>(`${PREFIX}/devises${toQuery(params)}`)
}

export async function getDeviseStats(): Promise<DeviseStatsResponse> {
  return authenticatedRequest<DeviseStatsResponse>(`${PREFIX}/devises/stats`)
}

export async function getDevise(deviseId: number): Promise<DeviseResponse> {
  return authenticatedRequest<DeviseResponse>(`${PREFIX}/devises/${deviseId}`)
}

export async function createDevise(body: DeviseCreate): Promise<DeviseResponse> {
  return authenticatedRequest<DeviseResponse>(`${PREFIX}/devises`, { method: 'POST', body })
}

export async function updateDevise(deviseId: number, body: DeviseUpdate): Promise<DeviseResponse> {
  return authenticatedRequest<DeviseResponse>(`${PREFIX}/devises/${deviseId}`, { method: 'PATCH', body })
}

/** Suppression d'une devise (refusée si la devise est utilisée dans des taux de change). */
export async function deleteDevise(deviseId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/devises/${deviseId}`, { method: 'DELETE' })
}

// --- Taux de change ---
export interface ListTauxChangeParams {
  skip?: number
  limit?: number
  devise_from_id?: number | null
  devise_to_id?: number | null
  date_effet_min?: string | null
  date_effet_max?: string | null
}

export async function listTauxChange(params: ListTauxChangeParams = {}): Promise<ListTauxChangeResponse> {
  return authenticatedRequest<ListTauxChangeResponse>(`${PREFIX}/taux-change${toQuery(params)}`)
}

export async function getTauxChangeStats(): Promise<TauxChangeStatsResponse> {
  return authenticatedRequest<TauxChangeStatsResponse>(`${PREFIX}/taux-change/stats/summary`)
}

export async function getTauxChange(tauxId: number): Promise<TauxChangeResponse> {
  return authenticatedRequest<TauxChangeResponse>(`${PREFIX}/taux-change/${tauxId}`)
}

export async function createTauxChange(body: TauxChangeCreate): Promise<TauxChangeResponse> {
  return authenticatedRequest<TauxChangeResponse>(`${PREFIX}/taux-change`, { method: 'POST', body })
}

export async function updateTauxChange(tauxId: number, body: TauxChangeUpdate): Promise<TauxChangeResponse> {
  return authenticatedRequest<TauxChangeResponse>(`${PREFIX}/taux-change/${tauxId}`, { method: 'PATCH', body })
}

export async function deleteTauxChange(tauxId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/taux-change/${tauxId}`, { method: 'DELETE' })
}

// --- Points de vente ---
export interface ListPointsVenteParams {
  skip?: number
  limit?: number
  actif_only?: boolean
  inactif_only?: boolean
  search?: string | null
  /** Filtrer par type : principal, secondaire, depot */
  type?: string | null
}

export async function listPointsVente(
  entrepriseId: number,
  params: ListPointsVenteParams = {},
): Promise<ListPointsVenteResponse> {
  return authenticatedRequest<ListPointsVenteResponse>(
    `${PREFIX}/entreprises/${entrepriseId}/points-vente${toQuery(params)}`,
  )
}

export async function getPointsVenteStats(entrepriseId: number): Promise<PointVenteStatsResponse> {
  return authenticatedRequest<PointVenteStatsResponse>(
    `${PREFIX}/entreprises/${entrepriseId}/points-vente/stats`,
  )
}

export async function getPointVente(pointVenteId: number): Promise<PointDeVenteResponse> {
  return authenticatedRequest<PointDeVenteResponse>(`${PREFIX}/points-vente/${pointVenteId}`)
}

export async function createPointVente(body: PointDeVenteCreate): Promise<PointDeVenteResponse> {
  return authenticatedRequest<PointDeVenteResponse>(`${PREFIX}/points-vente`, { method: 'POST', body })
}

export async function updatePointVente(
  pointVenteId: number,
  body: PointDeVenteUpdate,
): Promise<PointDeVenteResponse> {
  return authenticatedRequest<PointDeVenteResponse>(`${PREFIX}/points-vente/${pointVenteId}`, {
    method: 'PATCH',
    body,
  })
}

export async function deletePointVente(pointVenteId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/points-vente/${pointVenteId}`, { method: 'DELETE' })
}

// --- Rôles ---
export interface ListRolesParams {
  skip?: number
  limit?: number
  entreprise_id?: number | null
}

export async function listRoles(params: ListRolesParams = {}): Promise<RoleResponse[]> {
  return authenticatedRequest<RoleResponse[]>(`${PREFIX}/roles${toQuery(params)}`)
}

export async function getRole(roleId: number): Promise<RoleResponse> {
  return authenticatedRequest<RoleResponse>(`${PREFIX}/roles/${roleId}`)
}

export async function createRole(body: RoleCreate): Promise<RoleResponse> {
  return authenticatedRequest<RoleResponse>(`${PREFIX}/roles`, { method: 'POST', body })
}

export async function updateRole(roleId: number, body: RoleUpdate): Promise<RoleResponse> {
  return authenticatedRequest<RoleResponse>(`${PREFIX}/roles/${roleId}`, { method: 'PATCH', body })
}

// --- Permissions ---
export interface ListPermissionsParams {
  skip?: number
  limit?: number
  module?: string | null
  include_roles?: boolean
}

export async function listPermissions(params: ListPermissionsParams = {}): Promise<PermissionWithRolesResponse[]> {
  return authenticatedRequest<PermissionWithRolesResponse[]>(`${PREFIX}/permissions${toQuery(params)}`)
}

export async function getPermission(permissionId: number): Promise<PermissionResponse> {
  return authenticatedRequest<PermissionResponse>(`${PREFIX}/permissions/${permissionId}`)
}

export async function createPermission(body: PermissionCreate): Promise<PermissionResponse> {
  return authenticatedRequest<PermissionResponse>(`${PREFIX}/permissions`, { method: 'POST', body })
}

export async function addPermissionToRole(body: PermissionRoleCreate): Promise<PermissionRoleResponse> {
  return authenticatedRequest<PermissionRoleResponse>(`${PREFIX}/permissions-roles`, { method: 'POST', body })
}

export async function removePermissionFromRole(roleId: number, permissionId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/permissions-roles/${roleId}/${permissionId}`, {
    method: 'DELETE',
  })
}

// --- Utilisateurs ---
export interface ListUtilisateursParams {
  skip?: number
  limit?: number
  actif_only?: boolean
  search?: string | null
}

export async function listUtilisateurs(
  entrepriseId: number,
  params: ListUtilisateursParams = {},
): Promise<UtilisateurResponse[]> {
  return authenticatedRequest<UtilisateurResponse[]>(
    `${PREFIX}/entreprises/${entrepriseId}/utilisateurs${toQuery(params)}`,
  )
}

export async function getUtilisateur(utilisateurId: number): Promise<UtilisateurResponse> {
  return authenticatedRequest<UtilisateurResponse>(`${PREFIX}/utilisateurs/${utilisateurId}`)
}

export async function createUtilisateur(body: UtilisateurCreate): Promise<UtilisateurResponse> {
  return authenticatedRequest<UtilisateurResponse>(`${PREFIX}/utilisateurs`, { method: 'POST', body })
}

export async function updateUtilisateur(
  utilisateurId: number,
  body: UtilisateurUpdate,
): Promise<UtilisateurResponse> {
  return authenticatedRequest<UtilisateurResponse>(`${PREFIX}/utilisateurs/${utilisateurId}`, {
    method: 'PATCH',
    body,
  })
}

export async function changePasswordUtilisateur(
  utilisateurId: number,
  body: UtilisateurChangePasswordBody,
): Promise<void> {
  await authenticatedRequest<unknown>(
    `${PREFIX}/utilisateurs/${utilisateurId}/changer-mot-de-passe`,
    { method: 'PATCH', body },
  )
}

export async function deleteUtilisateur(utilisateurId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/utilisateurs/${utilisateurId}`, {
    method: 'DELETE',
  })
}

// --- Affectations utilisateur-PDV ---
export async function listAffectationsByUtilisateur(
  utilisateurId: number,
): Promise<AffectationUtilisateurPdvResponse[]> {
  return authenticatedRequest<AffectationUtilisateurPdvResponse[]>(
    `${PREFIX}/utilisateurs/${utilisateurId}/affectations-pdv`,
  )
}

export async function listAffectationsByPointVente(
  pointVenteId: number,
): Promise<AffectationUtilisateurPdvResponse[]> {
  return authenticatedRequest<AffectationUtilisateurPdvResponse[]>(
    `${PREFIX}/points-vente/${pointVenteId}/affectations`,
  )
}

export async function createAffectationPdv(
  body: AffectationUtilisateurPdvCreate,
): Promise<AffectationUtilisateurPdvResponse> {
  return authenticatedRequest<AffectationUtilisateurPdvResponse>(
    `${PREFIX}/affectations-utilisateur-pdv`,
    { method: 'POST', body },
  )
}

export async function updateAffectationPdv(
  affectationId: number,
  body: AffectationUtilisateurPdvUpdate,
): Promise<AffectationUtilisateurPdvResponse> {
  return authenticatedRequest<AffectationUtilisateurPdvResponse>(
    `${PREFIX}/affectations-utilisateur-pdv/${affectationId}`,
    { method: 'PATCH', body },
  )
}

export async function deleteAffectationPdv(affectationId: number): Promise<void> {
  await authenticatedRequest<unknown>(`${PREFIX}/affectations-utilisateur-pdv/${affectationId}`, {
    method: 'DELETE',
  })
}
