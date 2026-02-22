import type { App } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth)
  const unauthenticatedOnly = to.matched.some(r => r.meta?.unauthenticatedOnly)

  if (requiresAuth && !authStore.isAuthenticated) {
    if (authStore.refreshToken) {
      const ok = await authStore.refresh()
      if (ok) {
        next()
        return
      }
    }
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  if (unauthenticatedOnly && authStore.isAuthenticated) {
    const redirect = (to.query.redirect as string) || '/dashboard'
    next(redirect.startsWith('/') ? redirect : '/dashboard')
    return
  }
  next()
})

export default function (app: App) {
  app.use(router)
}

export { router }
