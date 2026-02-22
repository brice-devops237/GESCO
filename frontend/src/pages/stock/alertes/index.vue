<script setup lang="ts">
import { listAlertes } from '@/api/stock'
import { listDepots } from '@/api/achats'
import type { AlerteStockResponse } from '@/api/types/stock'
import type { DepotResponse } from '@/api/types/achats'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<AlerteStockResponse[]>([])
const depots = ref<DepotResponse[]>([])
const loading = ref(false)
const selectedDepotId = ref<number | null>(null)

const headers = [
  { title: 'PRODUIT', key: 'produit_libelle', width: '200px' },
  { title: 'CODE', key: 'produit_code', width: '120px' },
  { title: 'DÉPÔT', key: 'depot_libelle', width: '160px' },
  { title: 'QUANTITÉ', key: 'quantite', width: '110px', align: 'end' as const },
  { title: 'SEUIL ALERTE MIN', key: 'seuil_alerte_min', width: '130px', align: 'end' as const },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const paginatedItems = computed(() => { const start = (page.value - 1) * itemsPerPage.value; return items.value.slice(start, start + itemsPerPage.value) })
const totalFiltered = computed(() => items.value.length)
const pageRangeText = computed(() => { const total = totalFiltered.value; if (total === 0) return '0 sur 0'; const start = (page.value - 1) * itemsPerPage.value + 1; const end = Math.min(page.value * itemsPerPage.value, total); return `${start}-${end} sur ${total}` })
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

const depotItems = computed(() => depots.value.map(d => ({ title: d.libelle || `Dépôt ${d.id}`, value: d.id })))

async function loadDepots() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) return
  try {
    depots.value = await listDepots({ entreprise_id: entrepriseId, limit: 100 })
    if (depots.value.length && !selectedDepotId.value) selectedDepotId.value = depots.value[0].id
  } catch {
    depots.value = []
  }
}

async function load() {
  if (selectedDepotId.value == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listAlertes({ depot_id: selectedDepotId.value, limit: 500 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadDepots() })
watch(selectedDepotId, (id) => { if (id) { page.value = 1; load() } else items.value = [] })
watch(() => authStore.isAuthenticated, (ok) => { if (ok) { loadDepots(); if (selectedDepotId.value) load() } })
</script>

<template>
  <div class="module-page">
    <VCard>
      <VCardText class="pa-0">
        <div class="d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VSelect
            v-model="selectedDepotId"
            :items="depotItems"
            item-title="title"
            item-value="value"
            label="Dépôt"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 200px;"
          />
          <VBtn variant="outlined" size="small" prepend-icon="ri-refresh-line" @click="load">Actualiser</VBtn>
        </div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!selectedDepotId"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Sélectionnez un dépôt.</td></tr>
            <tr v-else-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune alerte.</td></tr>
            <tr v-else v-for="(item, idx) in paginatedItems" :key="idx" class="data-row">
              <td class="py-3 px-4">{{ item.produit_libelle || '—' }}</td>
              <td class="py-3 px-4">{{ item.produit_code || '—' }}</td>
              <td class="py-3 px-4">{{ item.depot_libelle || '—' }}</td>
              <td class="py-3 px-4 text-right">{{ item.quantite ?? '—' }}</td>
              <td class="py-3 px-4 text-right">{{ item.seuil_alerte_min ?? '—' }}</td>
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
