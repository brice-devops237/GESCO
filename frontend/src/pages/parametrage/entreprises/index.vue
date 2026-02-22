<script setup lang="ts">
import { listEntreprises, deleteEntreprise, getEntrepriseStats } from '@/api/parametrage'
import type { EntrepriseResponse, EntrepriseStatsResponse } from '@/api/types/parametrage'
import EntrepriseFormModal from '@/components/parametrage/EntrepriseFormModal.vue'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const toastStore = useToastStore()
const entreprises = ref<EntrepriseResponse[]>([])
const stats = ref<EntrepriseStatsResponse | null>(null)
const loading = ref(false)
const loadingStats = ref(false)
const searchQuery = ref('')
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)

// Filtres (temps réel, client-side)
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')
const filterPays = ref('')
const filterRegimeFiscal = ref('')
const dateDebut = ref('')
const dateFin = ref('')

const regimeFiscalLabels: Record<string, string> = {
  informel: 'Informel',
  liberatoire: 'Libératoire',
  forfait: 'Forfait',
  reel_simplifie: 'Réel simplifié',
  reel_normal: 'Réel normal',
}

const headers = [
  { title: 'CODE', key: 'code', sortable: true, width: 'min(100px, 10%)' },
  { title: 'ENTREPRISE', key: 'raison_sociale', sortable: true },
  { title: 'FISCALITÉ', key: 'regime_fiscal', width: '120px' },
  { title: 'PAYS', key: 'pays', width: '90px' },
  { title: 'DEVISE', key: 'devise_principale', width: '80px' },
  { title: 'STATUT', key: 'actif', width: '90px' },
  { title: 'CRÉÉE LE', key: 'created_at', width: '110px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '100px', align: 'end' as const },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

// Données affichées = page courante renvoyée par l’API (pagination serveur)
const displayedItems = computed(() => Array.isArray(entreprises.value) ? entreprises.value : [])

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = String(iso).slice(0, 10)
  if (!d) return '—'
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}

const totalFiltered = computed(() => totalFromApi.value)

const pageRangeText = computed(() => {
  const total = totalFiltered.value
  if (total === 0) return '0 sur 0'
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, total)
  return `${start}-${end} sur ${total}`
})

const canPrev = computed(() => page.value > 1)
const canNext = computed(() => (page.value * itemsPerPage.value) < totalFiltered.value)

const totalFromApi = ref(0)

async function loadEntreprises() {
  loading.value = true
  try {
    const params: { skip?: number; limit?: number; actif_only?: boolean; inactif_only?: boolean; search?: string } = {
      skip: (page.value - 1) * itemsPerPage.value,
      limit: itemsPerPage.value,
    }
    if (filterStatut.value === 'actif') params.actif_only = true
    if (filterStatut.value === 'inactif') params.inactif_only = true
    if (searchQuery.value?.trim()) params.search = searchQuery.value.trim()
    const data = await listEntreprises(params)
    entreprises.value = Array.isArray(data.items) ? data.items : []
    totalFromApi.value = data.total ?? 0
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des entreprises.')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  loadingStats.value = true
  try {
    stats.value = await getEntrepriseStats()
  } catch {
    stats.value = null
  } finally {
    loadingStats.value = false
  }
}

function onFiltersChange() {
  page.value = 1
  loadEntreprises()
}

onMounted(() => {
  loadEntreprises()
  loadStats()
})
watch([searchQuery, filterStatut], onFiltersChange)
watch([page, itemsPerPage], () => loadEntreprises())

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: EntrepriseResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

async function openConfirmDelete(row: EntrepriseResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Voulez-vous vraiment supprimer <strong>« ${row.raison_sociale } »</strong> ?<br><span class="text-caption">Cette action est irréversible.</span>`,
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
    await deleteEntreprise(row.id)
    toastStore.success('Entreprise supprimée.')
    await loadEntreprises()
    await loadStats()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadEntreprises()
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
  <div class="entreprises-page">
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
              <div class="stats-icon total"><VIcon icon="ri-building-line" size="28" /></div>
              <div>
                <div class="text-body-2 text-medium-emphasis">Total entreprises</div>
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

    <VCard class="entreprises-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher "
            density="compact"
            hide-details
            clearable
            class="entreprises-search"
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
          />
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
                Aucune entreprise trouvée.
              </td>
            </tr>
            <tr v-else v-for="item in displayedItems" :key="item.id" class="entreprise-row">
              <td class="py-3 px-4 font-weight-medium">
                {{ item.code }}
              </td>
              <td class="py-3 px-4">{{ item.raison_sociale || '—' }}</td>
              <td class="py-3 px-4 text-body-2 text-medium-emphasis">{{ item.regime_fiscal || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.pays || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.devise_principale || '—' }}</td>
              <td class="py-3 px-4">
                {{ item.actif ? 'actif' : 'inactif' }}
              </td>
              <td class="py-3 px-4 text-body-2 text-medium-emphasis">{{ formatDate(item.created_at) }}</td>
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

    <EntrepriseFormModal
      v-model="formModalOpen"
      :entreprise-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
  </div>
</template>

<style scoped>
.entreprises-page {
  max-width: 100%;
}

.entreprises-card {
  border-radius: 12px;
  overflow: hidden;
}

.entreprises-table-wrap {
  overflow: hidden;
}

.entreprises-table {
  border-collapse: collapse;
}

.entreprises-table :deep(thead th) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.entreprises-table th {
  white-space: nowrap;
}

.list-item-danger :deep(.v-list-item-title),
.list-item-danger :deep(.v-icon) {
  color: rgb(var(--v-theme-error)) !important;
}

.entreprise-row:hover {
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
.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.stats-icon.total { background: rgba(var(--v-theme-primary), 0.15); color: rgb(var(--v-theme-primary)); }
.stats-icon.actives { background: rgba(var(--v-theme-success), 0.15); color: rgb(var(--v-theme-success)); }
.stats-icon.inactives { background: rgba(var(--v-theme-error), 0.12); color: rgb(var(--v-theme-error)); }
.stats-repartition { border-width: 1px; }
</style>
