<script setup lang="ts">
import { listTiers, listContactsByTiers, deleteContact } from '@/api/partenaires'
import type { TiersResponse, ContactResponse } from '@/api/types/partenaires'
import ContactFormModal from '@/components/partenaires/ContactFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const tiersList = ref<TiersResponse[]>([])
const selectedTiersId = ref<number | null>(null)
const items = ref<ContactResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingContactId = ref<number | null>(null)

const headers = [
  { title: 'CIVILITÉ', key: 'civilite', width: '80px' },
  { title: 'NOM', key: 'nom', width: '140px' },
  { title: 'PRÉNOM', key: 'prenom', width: '120px' },
  { title: 'FONCTION', key: 'fonction', width: '140px' },
  { title: 'TÉLÉPHONE', key: 'telephone', width: '130px' },
  { title: 'EMAIL', key: 'email' },
  { title: 'PRINCIPAL', key: 'est_principal', width: '90px' },
  { title: 'STATUT', key: 'actif', width: '90px' },
  { title: 'ACTIONS', key: 'actions', width: '110px', align: 'end' as const },
]

const itemsPerPageOptions = [{ value: 10, title: '10' }, { value: 25, title: '25' }, { value: 50, title: '50' }]
const itemsPerPage = ref(10)
const page = ref(1)
const paginatedItems = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  return items.value.slice(start, start + itemsPerPage.value)
})
const totalFiltered = computed(() => items.value.length)
const pageRangeText = computed(() => {
  const total = totalFiltered.value
  if (total === 0) return '0 sur 0'
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, total)
  return `${start}-${end} sur ${total}`
})
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

const selectedTiers = computed(() => tiersList.value.find(t => t.id === selectedTiersId.value))
const selectedTiersLabel = computed(() => selectedTiers.value ? `${selectedTiers.value.code} - ${selectedTiers.value.raison_sociale}` : '')
const tiersSelectItems = computed(() => tiersList.value.map(t => ({ title: `${t.code} – ${t.raison_sociale}`, value: t.id })))

async function loadTiers() {
  const eid = entrepriseId.value
  if (eid == null) { tiersList.value = []; return }
  try {
    tiersList.value = await listTiers({ entreprise_id: eid, limit: 200 })
    if (tiersList.value.length && !selectedTiersId.value) selectedTiersId.value = tiersList.value[0].id
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement tiers.')
  }
}

async function load() {
  const tid = selectedTiersId.value
  if (tid == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listContactsByTiers(tid, { limit: 200 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des contacts.')
  } finally {
    loading.value = false
  }
}

watch(selectedTiersId, () => { page.value = 1; load() })
watch(entrepriseId, () => { loadTiers() })
onMounted(() => { loadTiers() })
watch(tiersList, (list) => {
  if (list.length && !selectedTiersId.value) selectedTiersId.value = list[0].id
}, { immediate: true })

function openCreate() {
  if (!selectedTiersId.value) return
  editingContactId.value = null
  formModalOpen.value = true
}
function openEdit(row: ContactResponse) { editingContactId.value = row.id; formModalOpen.value = true }
async function openConfirmDelete(row: ContactResponse) {
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Supprimer le contact <strong>« ${row.nom} ${row.prenom || ''} »</strong> ?`,
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
    await deleteContact(row.id)
    toastStore.success('Contact supprimé.')
    await load()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}
function onFormSaved() { formModalOpen.value = false; editingContactId.value = null; load() }
function onFormCancel() { formModalOpen.value = false; editingContactId.value = null }
</script>

<template>
  <div class="partenaires-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12"><VAlert type="info" variant="tonal" class="rounded-lg">Aucune entreprise associée.</VAlert></VCol>
    </VRow>
    <VCard v-else class="partenaires-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VSelect
            v-model="selectedTiersId"
            :items="tiersSelectItems"
            item-title="title"
            item-value="value"
            label="Tiers"
            density="compact"
            hide-details
            variant="outlined"
            style="min-width: 280px; max-width: 400px;"
          />
          <VBtn color="primary" prepend-icon="ri-add-line" :disabled="!selectedTiersId" @click="openCreate">Ajouter un contact</VBtn>
        </div>
        <VDivider />
        <div v-if="!selectedTiersId" class="pa-8 text-center text-medium-emphasis">
          Sélectionnez un tiers pour afficher ses contacts.
        </div>
        <template v-else>
          <div class="partenaires-table-wrap">
            <VTable class="partenaires-table" :class="{ 'table-loading': loading }">
              <thead>
                <tr>
                  <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
                <tr v-else-if="paginatedItems.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucun contact pour ce tiers.</td></tr>
                <tr v-else v-for="item in paginatedItems" :key="item.id" class="partenaires-row">
                  <td class="py-3 px-4 text-body-2">{{ item.civilite || '—' }}</td>
                  <td class="py-3 px-4 text-body-2">{{ item.nom }}</td>
                  <td class="py-3 px-4 text-body-2">{{ item.prenom || '—' }}</td>
                  <td class="py-3 px-4 text-body-2">{{ item.fonction || '—' }}</td>
                  <td class="py-3 px-4 text-body-2">{{ item.telephone || '—' }}</td>
                  <td class="py-3 px-4 text-body-2">{{ item.email || '—' }}</td>
                  <td class="py-3 px-4"><VChip v-if="item.est_principal" size="small" color="primary" variant="tonal">Oui</VChip><span v-else>—</span></td>
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
        </template>
        <template v-if="selectedTiersId && items.length > 0">
          <VDivider />
          <div class="d-flex flex-wrap align-center gap-4 pa-4">
            <div class="d-flex align-center gap-2">
              <span class="text-body-2 text-medium-emphasis">Lignes par page :</span>
              <VSelect :model-value="itemsPerPage" :items="itemsPerPageOptions" item-value="value" item-title="title" density="compact" hide-details variant="outlined" style="width: 72px;" @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }" />
            </div>
            <VSpacer />
            <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
            <div class="d-flex gap-1">
              <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="page--"><VIcon icon="ri-arrow-left-s-line" /></VBtn>
              <VBtn icon variant="text" size="small" :disabled="!canNext" @click="page++"><VIcon icon="ri-arrow-right-s-line" /></VBtn>
            </div>
          </div>
        </template>
      </VCardText>
    </VCard>
    <ContactFormModal
      v-if="selectedTiersId && selectedTiersLabel"
      v-model="formModalOpen"
      :contact-id="editingContactId"
      :tiers-id="selectedTiersId"
      :tiers-label="selectedTiersLabel"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
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
.list-item-danger :deep(.v-list-item-title), .list-item-danger :deep(.v-icon) { color: rgb(var(--v-theme-error)) !important; }
</style>
