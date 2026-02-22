<script setup lang="ts">
import { listComptesTresorerie } from '@/api/tresorerie'
import type { CompteTresorerieResponse } from '@/api/types/tresorerie'
import CompteTresorerieFormModal from '@/components/tresorerie/CompteTresorerieFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const items = ref<CompteTresorerieResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')
const filterType = ref<string>('all')

const headers = [
  { title: 'TYPE', key: 'type_compte', width: '100px' },
  { title: 'LIBELLÉ', key: 'libelle', sortable: true },
  { title: 'N° COMPTE', key: 'numero_compte', width: '140px' },
  { title: 'IBAN', key: 'iban', width: '180px' },
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

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(c => (c.libelle?.toLowerCase().includes(q)) || (c.numero_compte?.toLowerCase().includes(q)) || (c.iban?.toLowerCase().includes(q)))
  if (filterStatut.value === 'actif') list = list.filter(c => c.actif)
  if (filterStatut.value === 'inactif') list = list.filter(c => !c.actif)
  if (filterType.value !== 'all') list = list.filter(c => c.type_compte === filterType.value)
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
const hasActiveFilters = computed(() => (searchQuery.value?.trim() ?? '') !== '' || filterStatut.value !== 'all' || filterType.value !== 'all')

async function load() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!authStore.isAuthenticated || !entrepriseId) return
  loading.value = true
  try {
    items.value = await listComptesTresorerie({
      entreprise_id: entrepriseId,
      limit: 200,
      actif_only: filterStatut.value === 'actif' ? true : undefined,
      type_compte: filterType.value === 'all' ? undefined : filterType.value,
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
  filterStatut.value = 'all'
  filterType.value = 'all'
  page.value = 1
}

onMounted(load)
watch([searchQuery, filterStatut, filterType], onFiltersChange)
watch(() => authStore.isAuthenticated, (ok) => { if (ok) load() })

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: CompteTresorerieResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  load()
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
  <div class="tresorerie-page">
    <VCard class="tresorerie-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (libellé, N° compte, IBAN…)"
            density="compact"
            hide-details
            clearable
            style="min-width: 220px; max-width: 280px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VSelect
            v-model="filterType"
            :items="[
              { title: 'Tous les types', value: 'all' },
              { title: 'Banque', value: 'banque' },
              { title: 'Caisse', value: 'caisse' },
            ]"
            label="Type"
            item-title="title"
            item-value="value"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 140px;"
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
          />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">
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
                Aucun compte trésorerie trouvé.
              </td>
            </tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="data-row">
              <td class="py-3 px-4 text-body-2">{{ item.type_compte || '—' }}</td>
              <td class="py-3 px-4 font-weight-medium">{{ item.libelle || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.numero_compte || '—' }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.iban || '—' }}</td>
              <td class="py-3 px-4">{{ item.actif ? 'Actif' : 'Inactif' }}</td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props: menuProps }">
                    <VBtn v-bind="menuProps" size="small">Options <VIcon icon="ri-settings-4-line" class="ml-1" size="22" /></VBtn>
                  </template>
                  <VList density="compact" min-width="200">
                    <VListItem prepend-icon="ri-pencil-line" title="Modifier" @click="openEdit(item)" />
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
    <CompteTresorerieFormModal
      v-model="formModalOpen"
      :compte-tresorerie-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
  </div>
</template>

<style scoped>
.tresorerie-page { max-width: 100%; }
.tresorerie-card { border-radius: 12px; overflow: hidden; }
.data-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.02); }
</style>
