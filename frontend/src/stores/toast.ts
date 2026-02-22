/**
 * Store Pinia pour les notifications toast (snackbar).
 * Utiliser useToastStore().toast.error(), .success(), etc. depuis n'importe quel composant.
 */

import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export const useToastStore = defineStore('toast', {
  state: () => ({
    visible: false,
    message: '',
    type: 'info' as ToastType,
    timeout: 5000,
  }),

  actions: {
    show(text: string, type: ToastType = 'info', timeout = 5000) {
      this.message = text
      this.type = type
      this.timeout = timeout
      this.visible = true
    },

    hide() {
      this.visible = false
    },

    success(message: string, timeout?: number) {
      this.show(message, 'success', timeout ?? 4000)
    },

    error(message: string, timeout?: number) {
      this.show(message, 'error', timeout ?? 6000)
    },

    info(message: string, timeout?: number) {
      this.show(message, 'info', timeout)
    },

    warning(message: string, timeout?: number) {
      this.show(message, 'warning', timeout)
    },
  },
})
