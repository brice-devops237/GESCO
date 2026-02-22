<script setup lang="ts">
import { useTheme } from 'vuetify'
import { useAuthStore } from '@/stores/auth'
import misc404 from '@images/pages/404.png'
import miscMaskDark from '@images/pages/misc-mask-dark.png'
import miscMaskLight from '@images/pages/misc-mask-light.png'
import tree from '@images/pages/tree.png'

const vuetifyTheme = useTheme()
const authStore = useAuthStore()

const authThemeMask = computed(() => {
  return vuetifyTheme.global.name.value === 'light'
    ? miscMaskLight
    : miscMaskDark
})

const backToLabel = computed(() => (authStore.isAuthenticated ? "Retour à l'accueil" : 'Retour à la connexion'))
const backToRoute = computed(() => (authStore.isAuthenticated ? '/dashboard' : '/login'))
</script>

<template>
  <div class="misc-wrapper">
    <ErrorHeader
      status-code="404"
      title="Page introuvable"
      description="La page que vous recherchez n'existe pas."
    />

    <!-- 👉 Image -->
    <div class="misc-avatar w-100 text-center">
      <VImg
        :src="misc404"
        alt="Coming Soon"
        :max-width="800"
        class="mx-auto"
      />
      <VBtn
        :to="backToRoute"
        color="primary"
        class="mt-10"
      >
        {{ backToLabel }}
      </VBtn>
    </div>

    <!-- 👉 Footer -->
    <VImg
      :src="tree"
      class="misc-footer-tree d-none d-md-block"
    />

    <VImg
      :src="authThemeMask"
      class="misc-footer-img d-none d-md-block"
    />
  </div>
</template>

<style lang="scss">
@use "@core/scss/template/pages/misc.scss";

.misc-footer-tree {
  inline-size: 15.625rem;
  inset-block-end: 3.5rem;
  inset-inline-start: 0.375rem;
}
</style>
