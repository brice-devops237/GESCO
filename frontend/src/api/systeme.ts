/**
 * API Système – alignée sur le backend (Bearer requis).
 * Paramètres, Journal d'audit, Notifications (marquer-lue), Licences (vérifier, activer, prolonger, info-prolongations).
 */

import { authenticatedRequest } from './authenticatedRequest'
import { toQuery } from './utils'
import type {
  ParametreSystemeCreate,
  ParametreSystemeUpdate,
  ParametreSystemeResponse,
  JournalAuditCreate,
  JournalAuditResponse,
  NotificationCreate,
  NotificationUpdate,
  NotificationResponse,
  LicenceLogicielleCreate,
  LicenceLogicielleUpdate,
  LicenceLogicielleResponse,
  LicenceValideResponse,
  LicenceProlongationsInfo,
} from './types/systeme'

const PREFIX = '/api/v1/systeme'

// --- Paramètres système ---
export interface ListParametresSystemeParams {
  entreprise_id: number
  categorie?: string | null
  skip?: number
  limit?: number
}
export function listParametresSysteme(params: ListParametresSystemeParams): Promise<ParametreSystemeResponse[]> {
  return authenticatedRequest<ParametreSystemeResponse[]>(`${PREFIX}/parametres${toQuery(params)}`)
}
export function getParametreSysteme(id: number): Promise<ParametreSystemeResponse> {
  return authenticatedRequest<ParametreSystemeResponse>(`${PREFIX}/parametres/${id}`)
}
export function createParametreSysteme(body: ParametreSystemeCreate): Promise<ParametreSystemeResponse> {
  return authenticatedRequest<ParametreSystemeResponse>(`${PREFIX}/parametres`, { method: 'POST', body })
}
export function updateParametreSysteme(id: number, body: ParametreSystemeUpdate): Promise<ParametreSystemeResponse> {
  return authenticatedRequest<ParametreSystemeResponse>(`${PREFIX}/parametres/${id}`, { method: 'PATCH', body })
}

// --- Journal d'audit ---
export interface ListJournalAuditParams {
  entreprise_id: number
  utilisateur_id?: number | null
  action?: string | null
  module?: string | null
  date_debut?: string | null
  date_fin?: string | null
  skip?: number
  limit?: number
}
export function listJournalAudit(params: ListJournalAuditParams): Promise<JournalAuditResponse[]> {
  return authenticatedRequest<JournalAuditResponse[]>(`${PREFIX}/audit${toQuery(params)}`)
}
export function getJournalAudit(id: number): Promise<JournalAuditResponse> {
  return authenticatedRequest<JournalAuditResponse>(`${PREFIX}/audit/${id}`)
}
export function createEntreeAudit(body: JournalAuditCreate): Promise<JournalAuditResponse> {
  return authenticatedRequest<JournalAuditResponse>(`${PREFIX}/audit`, { method: 'POST', body })
}

// --- Notifications ---
export interface ListNotificationsParams {
  lue?: boolean | null
  skip?: number
  limit?: number
}
export function listNotifications(params: ListNotificationsParams = {}): Promise<NotificationResponse[]> {
  return authenticatedRequest<NotificationResponse[]>(`${PREFIX}/notifications${toQuery(params)}`)
}
export function getNotification(id: number): Promise<NotificationResponse> {
  return authenticatedRequest<NotificationResponse>(`${PREFIX}/notifications/${id}`)
}
export function createNotification(body: NotificationCreate): Promise<NotificationResponse> {
  return authenticatedRequest<NotificationResponse>(`${PREFIX}/notifications`, { method: 'POST', body })
}
export function updateNotification(id: number, body: NotificationUpdate): Promise<NotificationResponse> {
  return authenticatedRequest<NotificationResponse>(`${PREFIX}/notifications/${id}`, { method: 'PATCH', body })
}
export function marquerNotificationLue(id: number): Promise<NotificationResponse> {
  return authenticatedRequest<NotificationResponse>(`${PREFIX}/notifications/${id}/marquer-lue`, { method: 'POST' })
}

// --- Licences logicielles ---
export interface ListLicencesParams {
  entreprise_id: number
  actif_only?: boolean
  valide_only?: boolean
  skip?: number
  limit?: number
}
export function listLicences(params: ListLicencesParams): Promise<LicenceLogicielleResponse[]> {
  return authenticatedRequest<LicenceLogicielleResponse[]>(`${PREFIX}/licences${toQuery(params)}`)
}
export function verifierLicence(entreprise_id: number): Promise<LicenceValideResponse> {
  return authenticatedRequest<LicenceValideResponse>(`${PREFIX}/licences/verifier${toQuery({ entreprise_id })}`)
}
export function getLicence(id: number): Promise<LicenceLogicielleResponse> {
  return authenticatedRequest<LicenceLogicielleResponse>(`${PREFIX}/licences/${id}`)
}
export function createLicence(body: LicenceLogicielleCreate): Promise<LicenceLogicielleResponse> {
  return authenticatedRequest<LicenceLogicielleResponse>(`${PREFIX}/licences`, { method: 'POST', body })
}
export function updateLicence(id: number, body: LicenceLogicielleUpdate): Promise<LicenceLogicielleResponse> {
  return authenticatedRequest<LicenceLogicielleResponse>(`${PREFIX}/licences/${id}`, { method: 'PATCH', body })
}
export function activerLicence(id: number): Promise<LicenceLogicielleResponse> {
  return authenticatedRequest<LicenceLogicielleResponse>(`${PREFIX}/licences/${id}/activer`, { method: 'POST' })
}
export function prolongerLicence(id: number): Promise<LicenceLogicielleResponse> {
  return authenticatedRequest<LicenceLogicielleResponse>(`${PREFIX}/licences/${id}/prolonger`, { method: 'POST' })
}
export function infoProlongationsLicence(id: number): Promise<LicenceProlongationsInfo> {
  return authenticatedRequest<LicenceProlongationsInfo>(`${PREFIX}/licences/${id}/info-prolongations`)
}
