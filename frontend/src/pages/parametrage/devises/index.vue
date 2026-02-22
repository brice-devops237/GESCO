<script setup lang="ts">
import { listDevises, deleteDevise, getDeviseStats } from '@/api/parametrage'
import type { DeviseResponse, DeviseStatsResponse } from '@/api/types/parametrage'
import DeviseFormModal from '@/components/parametrage/DeviseFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const devises = ref<DeviseResponse[]>([])
const stats = ref<DeviseStatsResponse | null>(null)
const loading = ref(false)
const loadingStats = ref(false)
const totalFromApi = ref(0)
const searchQuery = ref('')
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)

const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')
const filterDecimales = ref<string>('all')

const decimalesOptions = [
  { title: 'Toutes', value: 'all' },
  { title: '0', value: '0' },
  { title: '2', value: '2' },
  { title: '3', value: '3' },
  { title: '4', value: '4' },
  { title: '5', value: '5' },
  { title: '6', value: '6' },
]

const headers = [
  { title: 'CODE', key: 'code', sortable: true, width: 'min(90px, 12%)' },
  { title: 'LIBELLÉ', key: 'libelle', sortable: true },
  { title: 'SYMBOLE', key: 'symbole', width: '90px' },
  { title: 'DÉCIMALES', key: 'decimales', width: '100px' },
  { title: 'STATUT', key: 'actif', width: '90px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '100px', align: 'end' as const },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

const displayedItems = computed(() => Array.isArray(devises.value) ? devises.value : [])
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

async function loadDevises() {
  if (!authStore.isAuthenticated) return
  loading.value = true
  try {
    const search = searchQuery.value?.trim() || undefined
    const decimalesVal = filterDecimales.value === 'all' ? undefined : Number(filterDecimales.value)
    const data = await listDevises({
      limit: itemsPerPage.value,
      skip: (page.value - 1) * itemsPerPage.value,
      actif_only: filterStatut.value === 'actif',
      inactif_only: filterStatut.value === 'inactif',
      search: search || undefined,
      decimales: decimalesVal != null && !Number.isNaN(decimalesVal) ? decimalesVal : undefined,
    })
    devises.value = data.items ?? []
    totalFromApi.value = data.total ?? 0
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des devises.')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  if (!authStore.isAuthenticated) return
  loadingStats.value = true
  try {
    stats.value = await getDeviseStats()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des statistiques.')
  } finally {
    loadingStats.value = false
  }
}

function onFiltersChange() {
  page.value = 1
  loadDevises()
}

function resetFilters() {
  searchQuery.value = ''
  filterStatut.value = 'all'
  filterDecimales.value = 'all'
  page.value = 1
}

const hasActiveFilters = computed(() =>
  (searchQuery.value?.trim() ?? '') !== ''
  || filterStatut.value !== 'all'
  || filterDecimales.value !== 'all',
)

onMounted(() => {
  loadDevises()
  loadStats()
})
watch([searchQuery, filterStatut, filterDecimales], onFiltersChange)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) loadDevises() })

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: DeviseResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

async function openConfirmDelete(row: DeviseResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Voulez-vous vraiment supprimer la devise<br> <strong>« ${row.code } - ${row.libelle } »</strong> ?<br><span class="text-caption">Impossible si la devise est utilisée dans des taux de change.</span>`,
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
    await deleteDevise(row.id)
    toastStore.success('Devise supprimée.')
    await loadDevises()
    await loadStats()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadDevises()
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
  <div class="devises-page">
    <!-- Statistiques -->
    <VRow class="mb-2" dense>
      <VCol v-if="loadingStats" cols="12">
        <VCard class="pa-4">
          <div class="d-flex align-center gap-3">
            <VProgressCircular indeterminate size="24" width="2" />
            <span class="text-body-2">Chargement des statistiques…</span>
          </div>
        </VCard>
      </VCol>
      <template v-else-if="stats">
        <VCol cols="12" sm="6" md="4">
          <VCard class="stats-card stats-total" rounded="lg">
            <VCardText class="d-flex align-center gap-3 pa-4">
              <div class="stats-icon total"><VIcon icon="ri-money-dollar-circle-line" size="28" /></div>
              <div>
                <div class="text-body-2 text-medium-emphasis">Total devises</div>
                <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="6" md="4">
          <VCard class="stats-card stats-actives" rounded="lg">
            <VCardText class="d-flex align-center gap-3 pa-4">
              <div class="stats-icon actives"><VIcon icon="ri-checkbox-circle-line" size="28" /></div>
              <div>
                <div class="text-body-2 text-medium-emphasis">Actives</div>
                <div class="text-h5 font-weight-bold">{{ stats.actives }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="6" md="4">
          <VCard class="stats-card stats-inactives" rounded="lg">
            <VCardText class="d-flex align-center gap-3 pa-4">
              <div class="stats-icon inactives"><VIcon icon="ri-close-circle-line" size="28" /></div>
              <div>
                <div class="text-body-2 text-medium-emphasis">Inactives</div>
                <div class="text-h5 font-weight-bold">{{ stats.inactives }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
      </template>
    </VRow>

    <VCard class="devises-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (code, libellé, symbole…)"
            density="compact"
            hide-details
            clearable
            label="Rechercher"
            class="devises-search"
            style="min-width: 220px; max-width: 280px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VSelect
            v-model="filterStatut"
            :items="[
              { title: 'Tous', value: 'all' },
              { title: 'Actifs', value: 'actif' },
              { title: 'Inactifs', value: 'inactif' },
            ]"
            label="Statut"
            item-title="title"
            item-value="value"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 120px;"
            class="filter-select"
            prepend-inner-icon="ri-toggle-line"
            clearable
          />
          <VSelect
            v-model="filterDecimales"
            :items="decimalesOptions"
            label="Décimales"
            item-title="title"
            item-value="value"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 110px;"
            class="filter-select"
            prepend-inner-icon="ri-number-0"
            clearable
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
                Aucune devise trouvée.
              </td>
            </tr>
            <tr v-else v-for="item in displayedItems" :key="item.id" class="devise-row">
              <td class="py-3 px-4 font-weight-medium">
                {{ item.code }}
              </td>
              <td class="py-3 px-4">{{ item.libelle || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.symbole || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.decimales ?? '—' }}</td>
              <td class="py-3 px-4">
                {{ item.actif ? 'actif' : 'inactif' }}
              </td>
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

    <DeviseFormModal
      v-model="formModalOpen"
      :devise-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
  </div>
</template>

<style scoped>
.devises-page {
  max-width: 100%;
}

.devises-card {
  border-radius: 12px;
  overflow: hidden;
}

.devises-table-wrap {
  overflow: hidden;
}

.devises-table {
  border-collapse: collapse;
}

.devises-table :deep(thead th) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.devises-table th {
  white-space: nowrap;
}

.list-item-danger :deep(.v-list-item-title),
.list-item-danger :deep(.v-icon) {
  color: rgb(var(--v-theme-error)) !important;
}

.devise-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.code-chip {
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
.stats-icon.actives { background: rgba(var(--v-theme-success), 0.15); color: rgb(var(--v-theme-success)); }
.stats-icon.inactives { background: rgba(var(--v-theme-error), 0.12); color: rgb(var(--v-theme-error)); }
</style>
