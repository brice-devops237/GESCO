<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => (route.meta?.moduleTitle as string) ?? 'Module')
const description = computed(() => (route.meta?.moduleDescription as string) ?? 'Ce module sera intégré prochainement.')
</script>

<template>
  <div class="module-en-cours">
    <VCard class="rounded-lg">
      <VCardText class="text-center pa-8">
        <VIcon icon="ri-tools-line" size="64" color="primary" class="mb-4" />
        <h3 class="text-h5 font-weight-medium mb-2">{{ title }}</h3>
        <p class="text-body-2 text-medium-emphasis mb-4">
          {{ description }}
        </p>
        <VBtn to="/dashboard" color="primary" variant="tonal">Retour au tableau de bord</VBtn>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.module-en-cours { max-width: 600px; margin: 0 auto; }
</style>
