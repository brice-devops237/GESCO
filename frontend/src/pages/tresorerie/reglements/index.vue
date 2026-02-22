<script setup lang="ts">
import { listReglements } from '@/api/tresorerie'
import type { ReglementResponse } from '@/api/types/tresorerie'
import ReglementFormModal from '@/components/tresorerie/ReglementFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<ReglementResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const searchQuery = ref('')
const filterType = ref<string>('all')
const filterDateFrom = ref('')
const filterDateTo = ref('')

const headers = [
  { title: 'TYPE', key: 'type_reglement', width: '110px' },
  { title: 'TIERS ID', key: 'tiers_id', width: '90px' },
  { title: 'MONTANT', key: 'montant', width: '120px', align: 'end' as const },
  { title: 'DATE RÈGLEMENT', key: 'date_reglement', width: '130px' },
  { title: 'MODE PAIEMENT ID', key: 'mode_paiement_id', width: '120px' },
  { title: 'COMPTE TRÉS. ID', key: 'compte_tresorerie_id', width: '120px' },
  { title: 'RÉFÉRENCE', key: 'reference' },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]
const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(r => String(r.reference || '').toLowerCase().includes(q) || String(r.montant).includes(q))
  if (filterType.value !== 'all') list = list.filter(r => r.type_reglement === filterType.value)
  if (filterDateFrom.value) list = list.filter(r => r.date_reglement >= filterDateFrom.value)
  if (filterDateTo.value) list = list.filter(r => r.date_reglement <= filterDateTo.value)
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
const hasActiveFilters = computed(() =>
  (searchQuery.value?.trim() ?? '') !== '' || filterType.value !== 'all' || !!filterDateFrom.value || !!filterDateTo.value,
)

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listReglements({
      entreprise_id: entrepriseId,
      limit: 500,
      type_reglement: filterType.value === 'all' ? undefined : filterType.value,
      date_from: filterDateFrom.value || undefined,
      date_to: filterDateTo.value || undefined,
    })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}

function onFiltersChange() {
  page.value = 1
  load()
}

function resetFilters() {
  searchQuery.value = ''
  filterType.value = 'all'
  filterDateFrom.value = ''
  filterDateTo.value = ''
  page.value = 1
}

onMounted(load)
watch([searchQuery, filterType, filterDateFrom, filterDateTo], onFiltersChange)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })

function openCreate() {
  formModalOpen.value = true
}

function onFormSaved() {
  formModalOpen.value = false
  load()
}

function onFormCancel() {
  formModalOpen.value = false
}

function prevPage() {
  if (canPrev.value) page.value--
}

function nextPage() {
  if (canNext.value) page.value++
}
</script>

<template>
  <div class="tresorerie-page">
    <VCard class="tresorerie-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (référence, montant…)"
            density="compact"
            hide-details
            clearable
            style="min-width: 200px; max-width: 260px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VSelect
            v-model="filterType"
            :items="[
              { title: 'Tous', value: 'all' },
              { title: 'Encaissement', value: 'encaissement' },
              { title: 'Décaissement', value: 'decaissement' },
            ]"
            label="Type"
            item-title="title"
            item-value="value"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 140px;"
          />
          <VTextField
            v-model="filterDateFrom"
            label="Du"
            type="date"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 140px;"
          />
          <VTextField
            v-model="filterDateTo"
            label="Au"
            type="date"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 140px;"
          />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">
            Réinitialiser
          </VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">
            Nouveau règlement
          </VBtn>
        </div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th
                v-for="h in headers"
                :key="h.key"
                :class="['text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4', h.align === 'end' && 'text-right']"
                :style="h.width ? { width: h.width } : undefined"
              >
                {{ h.title }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="headers.length" class="text-center py-8">
                <VProgressCircular indeterminate color="primary" size="32" />
              </td>
            </tr>
            <tr v-else-if="paginatedItems.length === 0">
              <td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">
                Aucun règlement trouvé.
              </td>
            </tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4 text-body-2">{{ item.type_reglement || '—' }}</td>
              <td class="py-3 px-4">{{ item.tiers_id }}</td>
              <td class="py-3 px-4 text-right font-weight-medium">{{ item.montant }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_reglement }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.mode_paiement_id }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.compte_tresorerie_id }}</td>
              <td class="py-3 px-4">{{ item.reference || '—' }}</td>
            </tr>
          </tbody>
        </VTable>
        <VDivider />
        <div class="d-flex flex-wrap align-center gap-4 pa-4">
          <div class="d-flex align-center gap-2">
            <span class="text-body-2 text-medium-emphasis">Lignes par page :</span>
            <VSelect
              :model-value="itemsPerPage"
              :items="itemsPerPageOptions"
              item-value="value"
              item-title="title"
              density="compact"
              hide-details
              variant="outlined"
              style="width: 72px;"
              @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }"
            />
          </div>
          <VSpacer />
          <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
          <div class="d-flex gap-1">
            <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="prevPage">
              <VIcon icon="ri-arrow-left-s-line" />
            </VBtn>
            <VBtn icon variant="text" size="small" :disabled="!canNext" @click="nextPage">
              <VIcon icon="ri-arrow-right-s-line" />
            </VBtn>
          </div>
        </div>
      </VCardText>
    </VCard>
    <ReglementFormModal v-model="formModalOpen" @saved="onFormSaved" @cancel="onFormCancel" />
  </div>
</template>

<style scoped>
.tresorerie-page { max-width: 100%; }
.tresorerie-card { border-radius: 12px; overflow: hidden; }
.data-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.02); }
</style>
