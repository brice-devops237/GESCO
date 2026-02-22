<script setup lang="ts">
import { listFacturesFournisseurs } from '@/api/achats'
import { listTiers } from '@/api/partenaires'
import type { FactureFournisseurResponse } from '@/api/types/achats'
import type { TiersResponse } from '@/api/types/partenaires'
import FactureFournisseurFormModal from '@/components/achats/FactureFournisseurFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const items = ref<FactureFournisseurResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')
const filterFournisseurId = ref<number | null>(null)

const headers = [
  { title: 'N° fournisseur', key: 'numero_fournisseur', width: '130px' },
  { title: 'Fournisseur', key: 'fournisseur_id', width: '100px' },
  { title: 'Type', key: 'type_facture', width: '100px' },
  { title: 'Date facture', key: 'date_facture', width: '120px' },
  { title: 'Échéance', key: 'date_echeance', width: '120px' },
  { title: 'TTC', key: 'montant_ttc', width: '110px', align: 'end' as const },
  { title: 'Restant dû', key: 'montant_restant_du', width: '110px', align: 'end' as const },
  { title: 'Statut', key: 'statut_paiement', width: '100px' },
  { title: 'Actions', key: 'actions', width: '100px', align: 'end' as const },
]

const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]
const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(items.value) ? items.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) list = list.filter(f => (f.numero_fournisseur?.toLowerCase().includes(q)) || String(f.fournisseur_id).includes(q))
  if (filterFournisseurId.value != null) list = list.filter(f => f.fournisseur_id === filterFournisseurId.value)
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
const hasActiveFilters = computed(() => (searchQuery.value?.trim() ?? '') !== '' || filterFournisseurId.value != null)

const fournisseurFilterItems = computed(() => {
  const tiers = fournisseurs.value
  return [{ title: 'Tous les fournisseurs', value: null }, ...tiers.map(t => ({ title: `${t.code} – ${t.raison_sociale}`, value: t.id }))]
})
const fournisseurs = ref<TiersResponse[]>([])
const fournisseurLibelle = (id: number) => fournisseurs.value.find(t => t.id === id)?.raison_sociale ?? String(id)

function typeLabel(type: string) {
  const map: Record<string, string> = { facture: 'Facture', avoir: 'Avoir', proforma: 'Proforma' }
  return map[type] ?? type
}
function statutLabel(s: string) {
  const map: Record<string, string> = { non_paye: 'Non payé', partiel: 'Partiel', paye: 'Payé' }
  return map[s] ?? s
}

async function loadFournisseurs() {
  const eid = entrepriseId.value
  if (!eid) { fournisseurs.value = []; return }
  try { fournisseurs.value = await listTiers({ entreprise_id: eid, limit: 200 }) }
  catch { fournisseurs.value = [] }
}
async function load() {
  const eid = entrepriseId.value
  if (eid == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listFacturesFournisseurs({
      entreprise_id: eid,
      limit: 200,
      fournisseur_id: filterFournisseurId.value ?? undefined,
    })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}

function onFiltersChange() { page.value = 1; load() }
function resetFilters() { searchQuery.value = ''; filterFournisseurId.value = null; page.value = 1; load() }
onMounted(() => { loadFournisseurs(); load() })
watch([searchQuery, filterFournisseurId], onFiltersChange)
watch(entrepriseId, () => { loadFournisseurs(); load() })

function openCreate() { editingId.value = null; formModalOpen.value = true }
function openEdit(row: FactureFournisseurResponse) { editingId.value = row.id; formModalOpen.value = true }
function onFormSaved() { formModalOpen.value = false; editingId.value = null; load() }
function onFormCancel() { formModalOpen.value = false; editingId.value = null }
function prevPage() { if (canPrev.value) page.value-- }
function nextPage() { if (canNext.value) page.value++ }
</script>

<template>
  <div class="achats-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12"><VAlert type="info" variant="tonal" class="rounded-lg">Aucune entreprise associée.</VAlert></VCol>
    </VRow>
    <VCard v-else class="achats-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField v-model="searchQuery" placeholder="Rechercher (n° facture, fournisseur)…" density="compact" hide-details clearable style="min-width: 240px;" prepend-inner-icon="ri-search-line" variant="outlined" bg-color="grey-lighten-5" />
          <VSelect v-model="filterFournisseurId" :items="fournisseurFilterItems" item-title="title" item-value="value" label="Fournisseur" density="compact" hide-details variant="outlined" style="min-width: 200px;" />
          <VBtn v-if="hasActiveFilters" variant="outlined" color="secondary" size="small" prepend-icon="ri-refresh-line" @click="resetFilters">Réinitialiser</VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">Nouvelle facture fournisseur</VBtn>
        </div>
        <VDivider />
        <VTable class="achats-table" :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
            <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune facture fournisseur.</td></tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="achats-row">
              <td class="py-3 px-4"><VChip size="small" color="primary" variant="tonal" class="code-chip">{{ item.numero_fournisseur }}</VChip></td>
              <td class="py-3 px-4 text-body-2">{{ fournisseurLibelle(item.fournisseur_id) }}</td>
              <td class="py-3 px-4 text-body-2">{{ typeLabel(item.type_facture) }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_facture }}</td>
              <td class="py-3 px-4 text-body-2">{{ item.date_echeance || '—' }}</td>
              <td class="py-3 px-4 text-end font-weight-medium">{{ item.montant_ttc ?? '—' }}</td>
              <td class="py-3 px-4 text-end">{{ item.montant_restant_du ?? '—' }}</td>
              <td class="py-3 px-4"><VChip :color="item.statut_paiement === 'paye' ? 'success' : item.statut_paiement === 'partiel' ? 'warning' : 'default'" size="small" variant="tonal">{{ statutLabel(item.statut_paiement) }}</VChip></td>
              <td class="py-3 px-4 text-right">
                <VBtn size="small" variant="text" prepend-icon="ri-pencil-line" @click="openEdit(item)">Modifier</VBtn>
              </td>
            </tr>
          </tbody>
        </VTable>
        <VDivider />
        <div class="d-flex flex-wrap align-center gap-4 pa-4">
          <VSelect :model-value="itemsPerPage" :items="itemsPerPageOptions" item-value="value" item-title="title" density="compact" hide-details variant="outlined" style="width: 72px;" @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }" />
          <VSpacer />
          <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
          <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="prevPage"><VIcon icon="ri-arrow-left-s-line" /></VBtn>
          <VBtn icon variant="text" size="small" :disabled="!canNext" @click="nextPage"><VIcon icon="ri-arrow-right-s-line" /></VBtn>
        </div>
      </VCardText>
    </VCard>
    <FactureFournisseurFormModal v-if="entrepriseId && fournisseurs.length" v-model="formModalOpen" :entreprise-id="entrepriseId" :facture-id="editingId" :fournisseurs="fournisseurs" @saved="onFormSaved" @cancel="onFormCancel" />
  </div>
</template>

<style scoped>
.achats-page { max-width: 100%; }
.achats-card { border-radius: 12px; overflow: hidden; }
.achats-table :deep(thead th) { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.achats-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.code-chip { font-size: 0.75rem; font-weight: 600; }
</style>
