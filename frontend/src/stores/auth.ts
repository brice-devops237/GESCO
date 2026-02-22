/**
 * Store Pinia d'authentification.
 * Gère access_token, refresh_token, login, logout, refresh et persistance
 * (localStorage = "se souvenir de moi", sessionStorage sinon).
 */

import { defineStore } from 'pinia'
import * as authApi from '@/api/auth'
import type { LoginRequest } from '@/api/types'
import { decodeJwtPayload } from '@/utils/jwt'

const STORAGE_ACCESS = 'gesco_access_token'
const STORAGE_REFRESH = 'gesco_refresh_token'

function loadFromStorage(key: string): string | null {
  if (typeof window === 'undefined')
    return null
  return localStorage.getItem(key) ?? sessionStorage.getItem(key)
}

export interface UserInfo {
  user_id: number | null
  entreprise_id: number | null
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: loadFromStorage(STORAGE_ACCESS),
    refreshToken: loadFromStorage(STORAGE_REFRESH),
    /** true = persister en localStorage (se souvenir de moi) */
    _remember: true,
    _refreshing: false,
  }),

  getters: {
    isAuthenticated(state): boolean {
      return !!state.accessToken
    },

    bearerToken(state): string | null {
      return state.accessToken
    },

    /** Infos lues depuis le JWT (affichage uniquement). */
    userInfo(state): UserInfo {
      const payload = decodeJwtPayload(state.accessToken)
      if (!payload) {
        return { user_id: null, entreprise_id: null }
      }
      const sub = payload.sub
      const user_id = sub != null ? Number(sub) : null
      const entreprise_id = payload.entreprise_id != null ? Number(payload.entreprise_id) : null
      return {
        user_id: Number.isNaN(user_id) ? null : user_id,
        entreprise_id: Number.isNaN(entreprise_id) ? null : entreprise_id,
      }
    },
  },

  actions: {
    _persist() {
      if (typeof window === 'undefined')
        return
      const storage = this._remember ? localStorage : sessionStorage
      const other = this._remember ? sessionStorage : localStorage
      if (this.accessToken) {
        storage.setItem(STORAGE_ACCESS, this.accessToken)
      }
      else {
        other.removeItem(STORAGE_ACCESS)
        storage.removeItem(STORAGE_ACCESS)
      }
      if (this.refreshToken) {
        storage.setItem(STORAGE_REFRESH, this.refreshToken)
      }
      else {
        other.removeItem(STORAGE_REFRESH)
        storage.removeItem(STORAGE_REFRESH)
      }
    },

    async login(payload: LoginRequest & { remember?: boolean }): Promise<void> {
      this._remember = payload.remember !== false
      const res = await authApi.login({
        entreprise_id: payload.entreprise_id,
        login: payload.login,
        password: payload.password,
      })
      this.accessToken = res.access_token ?? null
      this.refreshToken = res.refresh_token ?? null
      this._persist()
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_ACCESS)
        localStorage.removeItem(STORAGE_REFRESH)
        sessionStorage.removeItem(STORAGE_ACCESS)
        sessionStorage.removeItem(STORAGE_REFRESH)
      }
    },

    /**
     * Rafraîchit l'access token avec le refresh token.
     * @returns true si le refresh a réussi, false sinon
     */
    async refresh(): Promise<boolean> {
      if (this._refreshing || !this.refreshToken)
        return false
      this._refreshing = true
      try {
        const res = await authApi.refresh(this.refreshToken)
        this.accessToken = res.access_token ?? null
        this.refreshToken = res.refresh_token ?? this.refreshToken
        this._persist()
        return !!this.accessToken
      }
      catch {
        this.logout()
        return false
      }
      finally {
        this._refreshing = false
      }
    },
  },
})
