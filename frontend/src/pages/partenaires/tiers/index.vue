<script setup lang="ts">
import { listTiers, listTypesTiers, deleteTiers } from '@/api/partenaires'
import type { TiersResponse, TypeTiersResponse } from '@/api/types/partenaires'
import TiersFormModal from '@/components/partenaires/TiersFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const items = ref<TiersResponse[]>([])
const typesTiers = ref<TypeTiersResponse[]>([])
const typeMap = computed(() => {
  const m: Record<number, string> = {}
  for (const t of typesTiers.value) m[t.id] = t.libelle
  return m
})
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')
const filterType = ref<number | null>(null)
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')

const headers = [
  { title: 'CODE', key: 'code', width: 'min(100px, 10%)' },
  { title: 'RAISON SOCIALE', key: 'raison_sociale', minWidth: '180px' },
  { title: 'TYPE', key: 'type_tiers_id', width: '110px' },
  { title: 'VILLE', key: 'ville', width: '120px' },
  { title: 'TÉLÉPHONE', key: 'telephone', width: '130px' },
  { title: 'EMAIL', key: 'email', width: '180px' },
  { title: 'LIMITE CRÉDIT', key: 'limite_credit', width: '110px', align: 'end' as const },
  { title: 'STATUT', key: 'actif', width: '90px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '110px', align: 'end' as const },
]

const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]
const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(t => (t.code?.toLowerCase().includes(q)) || (t.raison_sociale?.toLowerCase().includes(q)) || (t.email?.toLowerCase().includes(q)))
  if (filterType.value != null) list = list.filter(t => t.type_tiers_id === filterType.value)
  if (filterStatut.value === 'actif') list = list.filter(t => t.actif)
  if (filterStatut.value === 'inactif') list = list.filter(t => !t.actif)
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
const hasActiveFilters = computed(() => (searchQuery.value?.trim() ?? '') !== '' || filterType.value != null || filterStatut.value !== 'all')

async function loadTypes() {
  try { typesTiers.value = await listTypesTiers({ limit: 100 }) }
  catch { typesTiers.value = [] }
}
async function load() {
  const eid = entrepriseId.value
  if (eid == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listTiers({ entreprise_id: eid, limit: 200, actif_only: filterStatut.value === 'actif' ? true : undefined, search: searchQuery.value?.trim() || undefined })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}
function onFiltersChange() { page.value = 1; load() }
function resetFilters() { searchQuery.value = ''; filterType.value = null; filterStatut.value = 'all'; page.value = 1; load() }
onMounted(() => { loadTypes(); load() })
watch([searchQuery, filterType, filterStatut], onFiltersChange)
watch(entrepriseId, load)

function openCreate() { editingId.value = null; formModalOpen.value = true }
function openEdit(row: TiersResponse) { editingId.value = row.id; formModalOpen.value = true }
async function openConfirmDelete(row: TiersResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Supprimer le partenaire <strong>« ${row.code} – ${row.raison_sociale} »</strong> ?`,
    showCancelButton: true,
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
    cancelButtonColor: 'rgb(var(--v-theme-primary))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  try {
    await deleteTiers(row.id)
    toastStore.success('Tiers supprimé.')
    await load()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}
function onFormSaved() { formModalOpen.value = false; editingId.value = null; load() }
function onFormCancel() { formModalOpen.value = false; editingId.value = null }
function prevPage() { if (canPrev.value) page.value-- }
function nextPage() { if (canNext.value) page.value++ }

const typeFilterItems = computed(() => [
  { title: 'Tous les types', value: null },
  ...typesTiers.value.map(t => ({ title: t.libelle, value: t.id })),
])
</script>

<template>
  <div class="partenaires-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12"><VAlert type="info" variant="tonal" class="rounded-lg">Aucune entreprise associée. Les partenaires (clients / fournisseurs) sont rattachés à une entreprise.</VAlert></VCol>
    </VRow>
    <VCard v-else class="partenaires-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="searchQuery" placeholder="Rechercher (code, raison sociale, email, ville…)" density="compact" hide-details clearable style="min-width: 220px; max-width: 280px;" prepend-inner-icon="ri-search-line" variant="outlined" bg-color="grey-lighten-5" />
          <VSelect v-model="filterType" :items="typeFilterItems" item-title="title" item-value="value" label="Type" density="compact" hide-details variant="outlined" style="width: 160px;" />
          <VSelect v-model="filterStatut" :items="[{ title: 'Tous', value: 'all' }, { title: 'Actifs', value: 'actif' }, { title: 'Inactifs', value: 'inactif' }]" label="Statut" item-title="title" item-value="value" density="compact" hide-details variant="outlined" style="width: 120px;" />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">Réinitialiser</VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">Ajouter un partenaire</VBtn>
        </div>
        <VDivider />
        <div class="partenaires-table-wrap">
          <VTable class="partenaires-table" :class="{ 'table-loading': loading }">
            <thead>
              <tr>
                <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
              <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun partenaire.</td></tr>
              <tr v-else v-for="item in paginatedItems" :key="item.id" class="partenaires-row">
                <td class="py-3 px-4"><VChip size="small" color="primary" variant="tonal" class="code-chip">{{ item.code }}</VChip></td>
                <td class="py-3 px-4 text-body-2">{{ item.raison_sociale || '—' }}</td>
                <td class="py-3 px-4 text-body-2">{{ typeMap[item.type_tiers_id] ?? item.type_tiers_id }}</td>
                <td class="py-3 px-4 text-body-2">{{ item.ville || '—' }}</td>
                <td class="py-3 px-4 text-body-2">{{ item.telephone || '—' }}</td>
                <td class="py-3 px-4 text-body-2">{{ item.email || '—' }}</td>
                <td class="py-3 px-4 text-end text-body-2">{{ item.limite_credit != null ? item.limite_credit : '—' }}</td>
                <td class="py-3 px-4"><VChip :color="item.actif ? 'success' : 'default'" size="small" variant="tonal">{{ item.actif ? 'Actif' : 'Inactif' }}</VChip></td>
                <td class="py-3 px-4 text-right">
                  <VMenu location="bottom end" :close-on-content-click="true">
                    <template #activator="{ props: menuProps }">
                      <VBtn v-bind="menuProps" size="small">Options <VIcon icon="ri-settings-4-line" class="ml-1" size="22" /></VBtn>
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
        </div>
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
    <TiersFormModal v-if="entrepriseId && typesTiers.length" v-model="formModalOpen" :entreprise-id="entrepriseId" :tiers-id="editingId" :types-tiers="typesTiers" @saved="onFormSaved" @cancel="onFormCancel" />
  </div>
</template>

<style scoped>
.partenaires-page { max-width: 100%; }
.partenaires-card { border-radius: 12px; overflow: hidden; }
.partenaires-table-wrap { overflow: hidden; }
.partenaires-table { border-collapse: collapse; }
.partenaires-table :deep(thead th) { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.partenaires-table th { white-space: nowrap; }
.partenaires-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.code-chip { font-size: 0.75rem; font-weight: 600; }
.list-item-danger :deep(.v-list-item-title), .list-item-danger :deep(.v-icon) { color: rgb(var(--v-theme-error)) !important; }
</style>
