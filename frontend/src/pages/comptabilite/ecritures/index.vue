<script setup lang="ts">
import { listEcrituresComptables } from '@/api/comptabilite'
import type { EcritureComptableResponse } from '@/api/types/comptabilite'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<EcritureComptableResponse[]>([])
const loading = ref(false)
const filterJournalId = ref<number | null>(null)
const filterPeriodeId = ref<number | null>(null)
const filterDateFrom = ref('')
const filterDateTo = ref('')

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'JOURNAL ID', key: 'journal_id', width: '100px' },
  { title: 'PÉRIODE ID', key: 'periode_id', width: '100px' },
  { title: 'DATE', key: 'date_ecriture', width: '120px' },
  { title: 'N° PIÈCE', key: 'numero_piece' },
  { title: 'LIBELLÉ', key: 'libelle' },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  if (filterJournalId.value != null) list = list.filter(e => e.journal_id === filterJournalId.value)
  if (filterPeriodeId.value != null) list = list.filter(e => e.periode_id === filterPeriodeId.value)
  if (filterDateFrom.value) list = list.filter(e => e.date_ecriture >= filterDateFrom.value)
  if (filterDateTo.value) list = list.filter(e => e.date_ecriture <= filterDateTo.value)
  return list
})
const paginatedItems = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  return filteredItems.value.slice(start, start + itemsPerPage.value)
})
const totalFiltered = computed(() => filteredItems.value.length)
const pageRangeText = computed(() => {
  const total = totalFiltered.value
  if (total === 0) return '0 sur 0'
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, total)
  return `${start}-${end} sur ${total}`
})
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listEcrituresComptables({
      entreprise_id: entrepriseId,
      limit: 500,
      journal_id: filterJournalId.value ?? undefined,
      periode_id: filterPeriodeId.value ?? undefined,
      date_from: filterDateFrom.value || undefined,
      date_to: filterDateTo.value || undefined,
    })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

function onFiltersChange() { page.value = 1; load() }
onMounted(load)
watch([filterJournalId, filterPeriodeId, filterDateFrom, filterDateTo], onFiltersChange)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })

function prevPage() { if (canPrev.value) page.value-- }
function nextPage() { if (canNext.value) page.value++ }
</script>

<template>
  <div class="module-page">
    <VCard>
      <VCardText class="pa-0">
        <div class="d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="filterDateFrom" label="Du" type="date" density="compact" hide-details variant="outlined" style="width: 140px;" />
          <VTextField v-model="filterDateTo" label="Au" type="date" density="compact" hide-details variant="outlined" style="width: 140px;" />
          <VBtn color="primary" variant="outlined" size="small" prepend-icon="ri-refresh-line" @click="load">Actualiser</VBtn>
        </div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold py-4 px-4']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune écriture trouvée.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4">{{ item.id }}</td>
              <td class="py-3 px-4">{{ item.journal_id }}</td>
              <td class="py-3 px-4">{{ item.periode_id ?? '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_ecriture }}</td>
              <td class="py-3 px-4 font-weight-medium">{{ item.numero_piece || '—' }}</td>
              <td class="py-3 px-4">{{ item.libelle || '—' }}</td>
            </tr>
          </tbody>
        </VTable>
        <VDivider />
        <div class="d-flex flex-wrap align-center gap-4 pa-4">
          <div class="d-flex align-center gap-2">
            <span class="text-body-2 text-medium-emphasis">Lignes par page :</span>
            <VSelect :model-value="itemsPerPage" :items="itemsPerPageOptions" item-value="value" item-title="title" density="compact" hide-details variant="outlined" style="width: 72px;" @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }" />
          </div>
          <VSpacer />
          <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
          <div class="d-flex gap-1">
            <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="prevPage"><VIcon icon="ri-arrow-left-s-line" /></VBtn>
            <VBtn icon variant="text" size="small" :disabled="!canNext" @click="nextPage"><VIcon icon="ri-arrow-right-s-line" /></VBtn>
          </div>
        </div>
      </VCardText>
    </VCard>
  </div>
</template>

<style scoped>
.module-page { max-width: 100%; }
.data-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.02); }
</style>
