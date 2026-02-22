/**
 * Types alignés sur l'API OpenAPI Gesco (auth et réponses courantes).
 * @see OpenAPI 3.1.0 – Gesco API 1.0.0
 */

// --- Auth (OpenAPI: /api/v1/auth/login, /api/v1/auth/refresh) ---
export interface LoginRequest {
  /** ID de l'entreprise (contexte de connexion) */
  entreprise_id: number
  /** Identifiant de connexion */
  login: string
  /** Mot de passe en clair */
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type?: string
  refresh_token?: string | null
}

export interface RefreshRequest {
  refresh_token: string
}

/** Option entreprise pour le select de la page de connexion (GET /auth/entreprises) */
export interface EntrepriseOption {
  id: number
  raison_sociale: string
}

// --- Validation / erreurs API ---
export interface ValidationErrorDetail {
  loc: (string | number)[]
  msg: string
  type: string
}

export interface HTTPValidationError {
  detail?: ValidationErrorDetail[]
}

// --- Réponses génériques pour listes (pagination optionnelle) ---
export type ApiError = { detail?: string | HTTPValidationError }
