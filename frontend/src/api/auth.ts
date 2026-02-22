/**
 * Endpoints d'authentification (OpenAPI).
 * GET /api/v1/auth/entreprises, POST /api/v1/auth/login, POST /api/v1/auth/refresh
 */

import { apiRequest } from './client'
import type { LoginRequest, TokenResponse, RefreshRequest, EntrepriseOption } from './types'

const AUTH_PREFIX = '/api/v1/auth'

export async function getLoginEntreprises(): Promise<EntrepriseOption[]> {
  return apiRequest<EntrepriseOption[]>(`${AUTH_PREFIX}/entreprises`, { method: 'GET' })
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(`${AUTH_PREFIX}/login`, {
    method: 'POST',
    body: payload,
  })
}

export async function refresh(refreshToken: string): Promise<TokenResponse> {
  const body: RefreshRequest = { refresh_token: refreshToken }
  return apiRequest<TokenResponse>(`${AUTH_PREFIX}/refresh`, {
    method: 'POST',
    body,
  })
}
