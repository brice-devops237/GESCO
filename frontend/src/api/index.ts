/**
 * Point d'entrée API Gesco.
 * - apiRequest / authenticatedRequest
 * - auth (login, refresh), getLoginEntreprises
 * - parametrage, catalogue, partenaires, commercial, achats, stock, tresorerie,
 *   comptabilite, rh, paie, systeme, rapports, immobilisations
 */

export { apiRequest, getApiBaseUrl, doRequest } from './client'
export type { RequestConfig } from './client'
export { authenticatedRequest } from './authenticatedRequest'
export { login as apiLogin, refresh as apiRefresh, getLoginEntreprises } from './auth'
export type { LoginRequest, TokenResponse, RefreshRequest, EntrepriseOption, HTTPValidationError, ApiError } from './types'
export { toQuery } from './utils'
export * from './parametrage'
export * from './catalogue'
export * from './partenaires'
export * from './commercial'
export * from './achats'
export * from './stock'
export * from './tresorerie'
export * from './comptabilite'
export * from './rh'
export * from './paie'
export * from './systeme'
export * from './rapports'
export * from './immobilisations'
