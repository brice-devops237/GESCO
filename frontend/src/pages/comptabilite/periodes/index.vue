<script setup lang="ts">
import { listPeriodesComptables } from '@/api/comptabilite'
import type { PeriodeComptableResponse } from '@/api/types/comptabilite'
import PeriodeComptableFormModal from '@/components/comptabilite/PeriodeComptableFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<PeriodeComptableResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')

const headers = [
  { title: 'LIBELLÉ', key: 'libelle' },
  { title: 'DATE DÉBUT', key: 'date_debut', width: '130px' },
  { title: 'DATE FIN', key: 'date_fin', width: '130px' },
  { title: 'CLÔTURÉE', key: 'cloturee', width: '100px' },
  { title: 'ACTIONS', key: 'actions', width: '100px', align: 'end' as const },
]

const itemsPerPage = ref(10)
const page = ref(1)
const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(p => (p.libelle?.toLowerCase().includes(q)) || (p.date_debut?.toLowerCase().includes(q)) || (p.date_fin?.toLowerCase().includes(q)))
  return list
})
const paginatedItems = computed(() => { const start = (page.value - 1) * itemsPerPage.value; return filteredItems.value.slice(start, start + itemsPerPage.value) })
const totalFiltered = computed(() => filteredItems.value.length)
const pageRangeText = computed(() => { const total = totalFiltered.value; if (total === 0) return '0 sur 0'; const start = (page.value - 1) * itemsPerPage.value + 1; const end = Math.min(page.value * itemsPerPage.value, total); return `${start}-${end} sur ${total}` })
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)
const hasActiveFilters = computed(() => (searchQuery.value?.trim() ?? '') !== '')

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listPeriodesComptables({ entreprise_id: entrepriseId, limit: 200 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
  } finally {
    loading.value = false
  }
}

function onFiltersChange() { page.value = 1; load() }
function resetFilters() { searchQuery.value = ''; page.value = 1 }
onMounted(load)
watch(searchQuery, onFiltersChange)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })

function openCreate() { editingId.value = null; formModalOpen.value = true }
function openEdit(row: PeriodeComptableResponse) { editingId.value = row.id; formModalOpen.value = true }
function onFormSaved() { formModalOpen.value = false; editingId.value = null; load() }
function onFormCancel() { formModalOpen.value = false; editingId.value = null }
function prevPage() { if (canPrev.value) page.value-- }
function nextPage() { if (canNext.value) page.value++ }
</script>

<template>
  <div class="module-page">
    <VCard>
      <VCardText class="pa-0">
        <div class="d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="searchQuery" placeholder="Rechercher (libellé, dates…)" density="compact" hide-details clearable style="min-width: 220px;" prepend-inner-icon="ri-search-line" variant="outlined" />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">Réinitialiser</VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">Ajouter</VBtn>
        </div>
        <VDivider />
        <VTable :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune période trouvée.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4 font-weight-medium">{{ item.libelle || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_debut }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_fin }}</td>
              <td class="py-3 px-4">{{ item.cloturee ? 'Oui' : 'Non' }}</td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props: menuProps }"><VBtn v-bind="menuProps" size="small">Options <VIcon icon="ri-settings-4-line" class="ml-1" size="22" /></VBtn></template>
                  <VList density="compact" min-width="200"><VListItem prepend-icon="ri-pencil-line" title="Modifier" @click="openEdit(item)" /></VList>
                </VMenu>
              </td>
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
    <PeriodeComptableFormModal v-model="formModalOpen" :periode-id="editingId" @saved="onFormSaved" @cancel="onFormCancel" />
  </div>
</template>

<style scoped>
.module-page { max-width: 100%; }
.data-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.02); }
</style>
