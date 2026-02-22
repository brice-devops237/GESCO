<script setup lang="ts">
import { listProduits, deleteProduit, listFamillesProduits } from '@/api/catalogue'
import type { ProduitResponse } from '@/api/types/catalogue'
import type { FamilleProduitResponse } from '@/api/types/catalogue'
import ProduitFormModal from '@/components/catalogue/ProduitFormModal.vue'
import ProduitDetailModal from '@/components/catalogue/ProduitDetailModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const items = ref<ProduitResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const detailModalOpen = ref(false)
const detailProduitId = ref<number | null>(null)
const searchQuery = ref('')
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')
const filterFamilleId = ref<number | null>(null)
const familles = ref<FamilleProduitResponse[]>([])

const headers = [
  { title: 'CODE', key: 'code', sortable: true, width: 'min(110px, 12%)' },
  { title: 'LIBELLÉ', key: 'libelle', sortable: true },
  { title: 'FAMILLE', key: 'famille_id', width: '140px' },
  { title: 'TYPE', key: 'type', width: '100px' },
  { title: 'PRIX TTC', key: 'prix_vente_ttc', width: '110px', align: 'end' as const },
  { title: 'STATUT', key: 'actif', width: '90px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '120px', align: 'end' as const },
]

const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]
const itemsPerPage = ref(10)
const page = ref(1)

const familleMap = computed(() => {
  const m: Record<number, string> = {}
  for (const f of familles.value) m[f.id] = f.code
  return m
})
function familleCode(familleId: number | null | undefined) { return familleId != null ? (familleMap.value[familleId] ?? `#${familleId}`) : '—' }

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(p => (p.code?.toLowerCase().includes(q)) || (p.libelle?.toLowerCase().includes(q)))
  if (filterStatut.value === 'actif') list = list.filter(p => p.actif)
  if (filterStatut.value === 'inactif') list = list.filter(p => !p.actif)
  if (filterFamilleId.value != null) list = list.filter(p => p.famille_id === filterFamilleId.value)
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
const hasActiveFilters = computed(() => (searchQuery.value?.trim() ?? '') !== '' || filterStatut.value !== 'all' || filterFamilleId.value != null)
const familleOptions = computed(() => [{ title: 'Toutes', value: null as number | null }, ...familles.value.map(f => ({ title: `${f.code} — ${f.libelle}`, value: f.id }))])

async function loadFamilles() {
  const eid = entrepriseId.value
  if (eid == null) { familles.value = []; return }
  try { familles.value = await listFamillesProduits({ entreprise_id: eid, limit: 200 }) }
  catch { familles.value = [] }
}

async function load() {
  const eid = entrepriseId.value
  if (eid == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listProduits({ entreprise_id: eid, limit: 200, famille_id: filterFamilleId.value ?? undefined, actif_only: filterStatut.value === 'actif' ? true : undefined, search: searchQuery.value?.trim() || undefined })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}
function onFiltersChange() { page.value = 1; load() }
function resetFilters() { searchQuery.value = ''; filterStatut.value = 'all'; filterFamilleId.value = null; page.value = 1 }
onMounted(() => { loadFamilles(); load() })
watch([searchQuery, filterStatut, filterFamilleId], onFiltersChange)
watch(entrepriseId, () => { loadFamilles(); load() })

function openCreate() { editingId.value = null; formModalOpen.value = true }
function openEdit(row: ProduitResponse) { editingId.value = row.id; formModalOpen.value = true }
function openDetail(row: ProduitResponse) { detailProduitId.value = row.id; detailModalOpen.value = true }
function onDetailClose() { detailModalOpen.value = false; detailProduitId.value = null }
async function openConfirmDelete(row: ProduitResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Supprimer le produit <strong>« ${row.code } - ${row.libelle } »</strong> ?`,
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
    await deleteProduit(row.id)
    toastStore.success('Produit supprimé.')
    await load()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}
function onFormSaved() { formModalOpen.value = false; editingId.value = null; load() }
function onFormCancel() { formModalOpen.value = false; editingId.value = null }
function prevPage() { if (canPrev.value) page.value-- }
function nextPage() { if (canNext.value) page.value++ }
</script>

<template>
  <div class="catalogue-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12"><VAlert type="info" variant="tonal" class="rounded-lg">Aucune entreprise associée. Les produits sont rattachés à une entreprise.</VAlert></VCol>
    </VRow>
    <VCard v-else class="catalogue-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="searchQuery" placeholder="Rechercher (code, libellé…)" density="compact" hide-details clearable style="min-width: 220px; max-width: 280px;" prepend-inner-icon="ri-search-line" variant="outlined" bg-color="grey-lighten-5" />
          <VSelect v-model="filterFamilleId" :items="familleOptions" item-title="title" item-value="value" label="Famille" density="compact" hide-details variant="outlined" style="min-width: 180px;" clearable />
          <VSelect v-model="filterStatut" :items="[{ title: 'Tous', value: 'all' }, { title: 'Actifs', value: 'actif' }, { title: 'Inactifs', value: 'inactif' }]" label="Statut" item-title="title" item-value="value" density="compact" hide-details variant="outlined" style="width: 120px;" />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">Réinitialiser</VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">Ajouter</VBtn>
        </div>
        <VDivider />
        <div class="catalogue-table-wrap">
          <VTable class="catalogue-table" :class="{ 'table-loading': loading }">
            <thead>
              <tr>
                <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
              <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun produit trouvé.</td></tr>
              <tr v-else v-for="item in paginatedItems" :key="item.id" class="catalogue-row">
                <td class="py-3 px-4"><VChip size="small" color="primary" variant="tonal" class="code-chip">{{ item.code }}</VChip></td>
                <td class="py-3 px-4 text-body-2">{{ item.libelle || '—' }}</td>
                <td class="py-3 px-4 text-body-2">{{ familleCode(item.famille_id) }}</td>
                <td class="py-3 px-4 text-body-2">{{ item.type || '—' }}</td>
                <td class="py-3 px-4 text-right font-weight-medium">{{ item.prix_vente_ttc }}</td>
                <td class="py-3 px-4"><VChip :color="item.actif ? 'success' : 'default'" size="small" variant="tonal">{{ item.actif ? 'Actif' : 'Inactif' }}</VChip></td>
                <td class="py-3 px-4 text-right">
                  <VMenu location="bottom end" :close-on-content-click="true">
                    <template #activator="{ props }">
                      <VBtn v-bind="props" size="small">Options <VIcon icon="ri-settings-4-line" class="ml-1" size="22" /></VBtn>
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
    <ProduitFormModal v-if="entrepriseId" v-model="formModalOpen" :entreprise-id="entrepriseId" :produit-id="editingId" @saved="onFormSaved" @cancel="onFormCancel" />
    <ProduitDetailModal v-if="entrepriseId && detailProduitId" v-model="detailModalOpen" :produit-id="detailProduitId" :entreprise-id="entrepriseId" @close="onDetailClose" />
  </div>
</template>

<style scoped>
.catalogue-page { max-width: 100%; }
.catalogue-card { border-radius: 12px; overflow: hidden; }
.catalogue-table-wrap { overflow: hidden; }
.catalogue-table { border-collapse: collapse; }
.catalogue-table :deep(thead th) { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.catalogue-table th { white-space: nowrap; }
.catalogue-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.code-chip { font-size: 0.75rem; font-weight: 600; }
.list-item-danger :deep(.v-list-item-title), .list-item-danger :deep(.v-icon) { color: rgb(var(--v-theme-error)) !important; }
</style>
