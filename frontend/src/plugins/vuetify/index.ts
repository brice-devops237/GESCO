import type { App } from 'vue'

import { createVuetify } from 'vuetify'
import { VBtn } from 'vuetify/components/VBtn'
import defaults from './defaults'
import { icons } from './icons'
import { themes } from './theme'

// Styles

import '@core/scss/template/libs/vuetify/index.scss'
import 'vuetify/styles'

const THEME_STORAGE_KEY = 'gesco_theme'

function getInitialTheme(): string {
  if (typeof window === 'undefined')
    return 'light'
  const stored = localStorage.getItem(THEME_STORAGE_KEY)
  if (stored === 'light' || stored === 'dark')
    return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default function (app: App) {
  const vuetify = createVuetify({
    aliases: {
      IconBtn: VBtn,
    },
    defaults,
    icons,
    theme: {
      defaultTheme: getInitialTheme(),
      themes,
    },
  })

  app.use(vuetify)
}
