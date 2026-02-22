<script setup lang="ts">
import { listMouvements } from '@/api/stock'
import { listDepots } from '@/api/achats'
import type { MouvementStockResponse } from '@/api/types/stock'
import type { DepotResponse } from '@/api/types/achats'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<MouvementStockResponse[]>([])
const depots = ref<DepotResponse[]>([])
const loading = ref(false)
const selectedDepotId = ref<number | null>(null)
const filterDateFrom = ref('')
const filterDateTo = ref('')

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'TYPE', key: 'type_mouvement', width: '110px' },
  { title: 'PRODUIT ID', key: 'produit_id', width: '100px' },
  { title: 'QUANTITÉ', key: 'quantite', width: '100px', align: 'end' as const },
  { title: 'DATE', key: 'date_mouvement', width: '120px' },
  { title: 'RÉF. TYPE', key: 'reference_type' },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  if (filterDateFrom.value) list = list.filter(m => m.date_mouvement >= filterDateFrom.value)
  if (filterDateTo.value) list = list.filter(m => m.date_mouvement <= filterDateTo.value)
  return list
})
const paginatedItems = computed(() => { const start = (page.value - 1) * itemsPerPage.value; return filteredItems.value.slice(start, start + itemsPerPage.value) })
const totalFiltered = computed(() => filteredItems.value.length)
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
    items.value = await listMouvements({
      depot_id: selectedDepotId.value,
      limit: 500,
      date_from: filterDateFrom.value || undefined,
      date_to: filterDateTo.value || undefined,
    })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadDepots() })
watch(selectedDepotId, (id) => { if (id) { page.value = 1; load() } else items.value = [] })
watch([filterDateFrom, filterDateTo], () => { page.value = 1; load() })
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
          <VTextField v-model="filterDateFrom" label="Du" type="date" density="compact" hide-details variant="outlined" style="width: 140px;" />
          <VTextField v-model="filterDateTo" label="Au" type="date" density="compact" hide-details variant="outlined" style="width: 140px;" />
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
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun mouvement.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4">{{ item.id }}</td>
              <td class="py-3 px-4">{{ item.type_mouvement }}</td>
              <td class="py-3 px-4">{{ item.produit_id }}</td>
              <td class="py-3 px-4 text-right">{{ item.quantite }}</td>
              <td class="py-3 px-4">{{ item.date_mouvement }}</td>
              <td class="py-3 px-4">{{ item.reference_type || '—' }}</td>
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
