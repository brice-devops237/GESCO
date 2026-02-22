<script setup lang="ts">
import {
  listTauxChange,
  listDevises,
  deleteTauxChange,
  getTauxChangeStats,
} from '@/api/parametrage'
import type { TauxChangeResponse, DeviseResponse, TauxChangeStatsResponse } from '@/api/types/parametrage'
import TauxChangeFormModal from '@/components/parametrage/TauxChangeFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const taux = ref<TauxChangeResponse[]>([])
const devises = ref<DeviseResponse[]>([])
const stats = ref<TauxChangeStatsResponse | null>(null)
const loading = ref(false)
const loadingStats = ref(false)
const totalFromApi = ref(0)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)

const filterDeviseFromId = ref<number | null>(null)
const filterDeviseToId = ref<number | null>(null)
const filterDateMin = ref('')
const filterDateMax = ref('')

const headers = [
  { title: 'DEVISE SOURCE', key: 'devise_from_id', sortable: true, width: 'min(140px, 18%)' },
  { title: 'DEVISE CIBLE', key: 'devise_to_id', sortable: true, width: 'min(140px, 18%)' },
  { title: 'TAUX', key: 'taux', sortable: true, width: '120px', align: 'end' as const },
  { title: 'DATE EFFET', key: 'date_effet', sortable: true, width: '130px' },
  { title: 'SOURCE', key: 'source', width: '120px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '100px', align: 'end' as const },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

const deviseCode = (id: number) => devises.value.find(d => d.id === id)?.code ?? String(id)
const deviseLabel = (id: number) => {
  const d = devises.value.find(x => x.id === id)
  return d ? `${d.code} - ${d.libelle}` : String(id)
}

const displayedItems = computed(() => (Array.isArray(taux.value) ? taux.value : []))
const totalFiltered = computed(() => totalFromApi.value)
const pageRangeText = computed(() => {
  const total = totalFiltered.value
  if (total === 0) return '0 sur 0'
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, total)
  return `${start}-${end} sur ${total}`
})
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

const deviseOptions = computed(() =>
  devises.value.map(d => ({ title: `${d.code} - ${d.libelle}`, value: d.id })),
)

async function loadDevises() {
  try {
    const data = await listDevises({ limit: 100 })
    devises.value = data.items ?? []
  } catch {
    devises.value = []
  }
}

async function loadTaux() {
  if (!authStore.isAuthenticated) return
  loading.value = true
  try {
    const data = await listTauxChange({
      skip: (page.value - 1) * itemsPerPage.value,
      limit: itemsPerPage.value,
      devise_from_id: filterDeviseFromId.value ?? undefined,
      devise_to_id: filterDeviseToId.value ?? undefined,
      date_effet_min: filterDateMin.value?.trim() || undefined,
      date_effet_max: filterDateMax.value?.trim() || undefined,
    })
    taux.value = data.items ?? []
    totalFromApi.value = data.total ?? 0
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des taux.')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  if (!authStore.isAuthenticated) return
  loadingStats.value = true
  try {
    stats.value = await getTauxChangeStats()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des statistiques.')
  } finally {
    loadingStats.value = false
  }
}

function onFiltersChange() {
  page.value = 1
  loadTaux()
}

function resetFilters() {
  filterDeviseFromId.value = null
  filterDeviseToId.value = null
  filterDateMin.value = ''
  filterDateMax.value = ''
  page.value = 1
}

const hasActiveFilters = computed(
  () =>
    filterDeviseFromId.value != null
    || filterDeviseToId.value != null
    || (filterDateMin.value?.trim() ?? '') !== ''
    || (filterDateMax.value?.trim() ?? '') !== '',
)

onMounted(() => {
  loadDevises()
  loadTaux()
  loadStats()
})
watch(
  [filterDeviseFromId, filterDeviseToId, filterDateMin, filterDateMax],
  onFiltersChange,
)
watch([page, itemsPerPage], () => loadTaux())
watch(() => authStore.isAuthenticated, ok => {
  if (ok) loadTaux()
})

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: TauxChangeResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

async function openConfirmDelete(row: TauxChangeResponse) {
  const fromLabel = deviseLabel(row.devise_from_id)
  const toLabel = deviseLabel(row.devise_to_id)
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Supprimer le taux de change<br><strong>${fromLabel} → ${toLabel}</strong><br>au ${row.date_effet} (taux ${row.taux}) ?`,
    showCancelButton: true,
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  try {
    await deleteTauxChange(row.id)
    toastStore.success('Taux de change supprimé.')
    await loadTaux()
    await loadStats()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadTaux()
  loadStats()
}

function onFormCancel() {
  formModalOpen.value = false
  editingId.value = null
}

function prevPage() {
  if (canPrev.value) page.value--
}

function nextPage() {
  if (canNext.value) page.value++
}
</script>

<template>
  <div class="taux-change-page">
    <VCard class="taux-change-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VSelect
            v-model="filterDeviseFromId"
            :items="[{ title: 'Toutes', value: null }, ...deviseOptions]"
            item-title="title"
            item-value="value"
            label="Devise source"
            density="compact"
            hide-details
            clearable
            variant="outlined"
            style="min-width: 180px; max-width: 220px;"
            class="filter-select"
            prepend-inner-icon="ri-arrow-right-down-line"
          />
          <VSelect
            v-model="filterDeviseToId"
            :items="[{ title: 'Toutes', value: null }, ...deviseOptions]"
            item-title="title"
            item-value="value"
            label="Devise cible"
            density="compact"
            hide-details
            clearable
            variant="outlined"
            style="min-width: 180px; max-width: 220px;"
            class="filter-select"
            prepend-inner-icon="ri-arrow-right-up-line"
          />
          <VTextField
            v-model="filterDateMin"
            label="Date min"
            type="date"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 150px;"
            class="filter-date"
            prepend-inner-icon="ri-calendar-line"
          />
          <VTextField
            v-model="filterDateMax"
            label="Date max"
            type="date"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 150px;"
            class="filter-date"
            prepend-inner-icon="ri-calendar-line"
          />
          <VBtn
            v-if="hasActiveFilters"
            variant="outlined"
            color="secondary"
            size="small"
            prepend-icon="ri-refresh-line"
            @click="resetFilters"
          >
            Réinitialiser
          </VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">
            Ajouter
          </VBtn>
        </div>

        <VDivider />

          <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th
                v-for="h in headers"
                :key="h.key"
                :class="[
                  'text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4',
                  h.align === 'end' && 'text-right',
                ]"
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
            <tr v-else-if="displayedItems.length === 0">
              <td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">
                Aucun taux de change trouvé.
              </td>
            </tr>
            <tr v-else v-for="item in displayedItems" :key="item.id" class="taux-row">
              <td class="py-3 px-4">
                {{ deviseCode(item.devise_from_id) }}
              </td>
              <td class="py-3 px-4">
                {{ deviseCode(item.devise_to_id) }}
              </td>
              <td class="py-3 px-4 text-right font-weight-medium">
                {{ item.taux }}
              </td>
              <td class="py-3 px-4 text-body-2">{{ item.date_effet }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.source || '—' }}</td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props }">
                    <VBtn v-bind="props" size="small">
                      Options
                      <VIcon icon="ri-settings-4-line" class="ml-1" size="22" />
                    </VBtn>
                  </template>
                  <VList density="compact" min-width="200">
                    <VListItem prepend-icon="ri-pencil-line" title="Modifier" @click="openEdit(item)" />
                    <VDivider class="my-1" />
                    <VListItem prepend-icon="ri-delete-bin-line" title="Supprimer" class="list-item-danger" @click="openConfirmDelete(item)" />
                  </VList>
                </VMenu>
              </td>
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
              class="rows-select"
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

    <TauxChangeFormModal
      v-model="formModalOpen"
      :taux-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
  </div>
</template>

<style scoped>
.taux-change-page {
  max-width: 100%;
}

.taux-change-card {
  border-radius: 12px;
  overflow: hidden;
}

.taux-change-table-wrap {
  overflow: hidden;
}

.taux-change-table {
  border-collapse: collapse;
}

.taux-change-table :deep(thead th) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.taux-change-table th {
  white-space: nowrap;
}

.list-item-danger :deep(.v-list-item-title),
.list-item-danger :deep(.v-icon) {
  color: rgb(var(--v-theme-error)) !important;
}

.taux-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.devise-chip {
  font-size: 0.75rem;
  font-weight: 600;
}

.rows-select :deep(.v-field) {
  font-size: 0.875rem;
}

.stats-card { transition: transform 0.15s ease; }
.stats-card:hover { transform: translateY(-2px); }
.stats-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stats-icon.total { background: rgba(var(--v-theme-primary), 0.15); color: rgb(var(--v-theme-primary)); }
</style>
