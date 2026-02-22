<script setup lang="ts">
import { listTypesTiers, deleteTypeTiers } from '@/api/partenaires'
import type { TypeTiersResponse } from '@/api/types/partenaires'
import TypeTiersFormModal from '@/components/partenaires/TypeTiersFormModal.vue'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const toastStore = useToastStore()
const items = ref<TypeTiersResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')

const headers = [
  { title: 'CODE', key: 'code', sortable: true, width: 'min(100px, 12%)' },
  { title: 'LIBELLÉ', key: 'libelle', sortable: true },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '120px', align: 'end' as const },
]

const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]
const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(t => (t.code?.toLowerCase().includes(q)) || (t.libelle?.toLowerCase().includes(q)))
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
  loading.value = true
  try {
    items.value = await listTypesTiers({ limit: 200 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}
function onFiltersChange() { page.value = 1; load() }
onMounted(load)
watch(searchQuery, onFiltersChange)

function openCreate() { editingId.value = null; formModalOpen.value = true }
function openEdit(row: TypeTiersResponse) { editingId.value = row.id; formModalOpen.value = true }
async function openConfirmDelete(row: TypeTiersResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Supprimer le type <strong>« ${row.code} - ${row.libelle} »</strong> ?`,
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
    await deleteTypeTiers(row.id)
    toastStore.success('Type de tiers supprimé.')
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
  <div class="partenaires-page">
    <VCard class="partenaires-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (code, libellé…)"
            density="compact"
            hide-details
            clearable
            style="min-width: 220px; max-width: 280px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">Ajouter</VBtn>
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
              <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun type de tiers.</td></tr>
              <tr v-else v-for="item in paginatedItems" :key="item.id" class="partenaires-row">
                <td class="py-3 px-4"><VChip size="small" color="primary" variant="tonal" class="code-chip">{{ item.code }}</VChip></td>
                <td class="py-3 px-4 text-body-2">{{ item.libelle || '—' }}</td>
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
    <TypeTiersFormModal v-model="formModalOpen" :type-tiers-id="editingId" @saved="onFormSaved" @cancel="onFormCancel" />
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
