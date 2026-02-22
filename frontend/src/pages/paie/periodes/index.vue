<script setup lang="ts">
import { listPeriodesPaie } from '@/api/paie'
import type { PeriodePaieResponse } from '@/api/types/paie'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<PeriodePaieResponse[]>([])
const loading = ref(false)

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'DATE DÉBUT', key: 'date_debut', width: '120px' },
  { title: 'DATE FIN', key: 'date_fin', width: '120px' },
  { title: 'CLÔTURÉE', key: 'cloturee', width: '100px' },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const paginatedItems = computed(() => { const start = (page.value - 1) * itemsPerPage.value; return items.value.slice(start, start + itemsPerPage.value) })
const totalFiltered = computed(() => items.value.length)
const pageRangeText = computed(() => { const total = totalFiltered.value; if (total === 0) return '0 sur 0'; const start = (page.value - 1) * itemsPerPage.value + 1; const end = Math.min(page.value * itemsPerPage.value, total); return `${start}-${end} sur ${total}` })
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listPeriodesPaie({ entreprise_id: entrepriseId, limit: 200 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })
</script>

<template>
  <div class="module-page">
    <VCard>
      <VCardText class="pa-0">
        <div class="pa-5 pb-4"><h3 class="text-h6">Périodes de paie</h3></div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" class="text-left text-body-2 font-weight-bold py-4 px-4" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune période.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4">{{ item.id }}</td>
              <td class="py-3 px-4">{{ item.date_debut }}</td>
              <td class="py-3 px-4">{{ item.date_fin }}</td>
              <td class="py-3 px-4">{{ item.cloturee ? 'Oui' : 'Non' }}</td>
            </tr>
          </tbody>
        </VTable>
        <VDivider />
        <div class="d-flex flex-wrap align-center gap-4 pa-4">
          <VSelect :model-value="itemsPerPage" :items="itemsPerPageOptions" item-value="value" item-title="title" density="compact" hide-details variant="outlined" style="width: 72px;" @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }" />
          <VSpacer />
          <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
          <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="page--"><VIcon icon="ri-arrow-left-s-line" /></VBtn>
          <VBtn icon variant="text" size="small" :disabled="!canNext" @click="page++"><VIcon icon="ri-arrow-right-s-line" /></VBtn>
        </div>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.module-page { max-width: 100%; }
.data-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.02); }
</style>
