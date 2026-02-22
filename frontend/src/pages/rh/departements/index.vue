<script setup lang="ts">
import { listDepartements } from '@/api/rh'
import type { DepartementResponse } from '@/api/types/rh'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<DepartementResponse[]>([])
const loading = ref(false)
const searchQuery = ref('')
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')

const headers = [
  { title: 'CODE', key: 'code', width: '120px' },
  { title: 'LIBELLÉ', key: 'libelle' },
  { title: 'STATUT', key: 'actif', width: '90px' },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(d => (d.code?.toLowerCase().includes(q)) || (d.libelle?.toLowerCase().includes(q)))
  if (filterStatut.value === 'actif') list = list.filter(d => d.actif)
  if (filterStatut.value === 'inactif') list = list.filter(d => !d.actif)
  return list
})
const paginatedItems = computed(() => { const start = (page.value - 1) * itemsPerPage.value; return filteredItems.value.slice(start, start + itemsPerPage.value) })
const totalFiltered = computed(() => filteredItems.value.length)
const pageRangeText = computed(() => { const total = totalFiltered.value; if (total === 0) return '0 sur 0'; const start = (page.value - 1) * itemsPerPage.value + 1; const end = Math.min(page.value * itemsPerPage.value, total); return `${start}-${end} sur ${total}` })
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listDepartements({ entreprise_id: entrepriseId, limit: 300, actif_only: filterStatut.value === 'actif' ? true : undefined })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch([searchQuery, filterStatut], () => { page.value = 1; load() })
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })
</script>

<template>
  <div class="module-page">
    <VCard>
      <VCardText class="pa-0">
        <div class="d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="searchQuery" placeholder="Rechercher…" density="compact" hide-details clearable style="min-width: 200px;" prepend-inner-icon="ri-search-line" variant="outlined" />
          <VSelect v-model="filterStatut" :items="[{ title: 'Tous', value: 'all' }, { title: 'Actifs', value: 'actif' }, { title: 'Inactifs', value: 'inactif' }]" label="Statut" item-title="title" item-value="value" density="compact" hide-details variant="outlined" style="width: 120px;" />
        </div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" class="text-left text-body-2 font-weight-bold py-4 px-4" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun département.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4 font-weight-medium">{{ item.code }}</td>
              <td class="py-3 px-4">{{ item.libelle || '—' }}</td>
              <td class="py-3 px-4">{{ item.actif ? 'Actif' : 'Inactif' }}</td>
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
