<script setup lang="ts">
import { useRoute } from 'vue-router'
import { listReceptionsByCommande, listCommandesFournisseurs } from '@/api/achats'
import { listTiers } from '@/api/partenaires'
import type { CommandeFournisseurResponse, ReceptionResponse, DepotResponse } from '@/api/types/achats'
import type { TiersResponse } from '@/api/types/partenaires'
import ReceptionFormModal from '@/components/achats/ReceptionFormModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const route = useRoute()
const authStore = useAuthStore()
const toastStore = useToastStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const commandes = ref<CommandeFournisseurResponse[]>([])
const fournisseurs = ref<TiersResponse[]>([])
const depots = ref<DepotResponse[]>([])
const selectedCommandeId = ref<number | null>(null)
const items = ref<ReceptionResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)

const headers = [
  { title: 'N° réception', key: 'numero', width: '130px' },
  { title: 'N° BL fournisseur', key: 'numero_bl_fournisseur', width: '140px' },
  { title: 'Date réception', key: 'date_reception', width: '120px' },
  { title: 'Dépôt', key: 'depot_id', width: '100px' },
  { title: 'État', key: 'etat', width: '100px' },
  { title: 'Actions', key: 'actions', width: '120px', align: 'end' as const },
]

const commandeOptions = computed(() => {
  const list = commandes.value
  const tiers = fournisseurs.value
  const byId: Record<number, TiersResponse> = {}
  for (const t of tiers) byId[t.id] = t
  return [{ title: '— Choisir une commande —', value: null }, ...list.map(c => ({
    title: `${c.numero} (${byId[c.fournisseur_id]?.raison_sociale ?? c.fournisseur_id})`,
    value: c.id,
  }))]
})

function etatLabel(etat: string) {
  const map: Record<string, string> = { brouillon: 'Brouillon', validee: 'Validée', annulee: 'Annulée' }
  return map[etat] ?? etat
}

async function loadCommandesAndTiers() {
  const eid = entrepriseId.value
  if (!eid) { commandes.value = []; fournisseurs.value = []; return }
  try {
    const [cmdList, tiers] = await Promise.all([
      listCommandesFournisseurs({ entreprise_id: eid, limit: 200 }),
      listTiers({ entreprise_id: eid, limit: 200 }),
    ])
    commandes.value = cmdList
    fournisseurs.value = tiers
  } catch {
    commandes.value = []
    fournisseurs.value = []
  }
}

async function loadReceptions() {
  const cid = selectedCommandeId.value
  if (cid == null) { items.value = []; return }
  loading.value = true
  try {
    items.value = await listReceptionsByCommande(cid, { limit: 100 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    items.value = []
  } finally {
    loading.value = false
  }
}

function onCommandeChange() { loadReceptions() }

onMounted(async () => {
  await loadCommandesAndTiers()
  const q = route.query.commande
  if (q) {
    const id = Number(q)
    if (!Number.isNaN(id)) selectedCommandeId.value = id
  }
})
watch(entrepriseId, loadCommandesAndTiers)
watch(selectedCommandeId, () => { loadReceptions() }, { immediate: true })

function openCreate() {
  if (!selectedCommandeId.value) {
    toastStore.warning('Sélectionnez d\'abord une commande fournisseur.')
    return
  }
  editingId.value = null
  formModalOpen.value = true
}
function openEdit(row: ReceptionResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}
function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadReceptions()
}
function onFormCancel() {
  formModalOpen.value = false
  editingId.value = null
}
</script>

<template>
  <div class="achats-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12"><VAlert type="info" variant="tonal" class="rounded-lg">Aucune entreprise associée.</VAlert></VCol>
    </VRow>
    <VCard v-else class="achats-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VSelect v-model="selectedCommandeId" :items="commandeOptions" item-title="title" item-value="value" label="Commande fournisseur" density="compact" hide-details variant="outlined" style="min-width: 320px;" />
          <VBtn color="primary" prepend-icon="ri-add-line" :disabled="!selectedCommandeId" @click="openCreate">Nouvelle réception</VBtn>
        </div>
        <VDivider />
        <template v-if="selectedCommandeId">
          <VTable class="achats-table" :class="{ 'table-loading': loading }">
            <thead>
              <tr>
                <th v-for="h in headers" :key="h.key" :class="['text-left text-body-2 font-weight-bold py-4 px-4', h.align === 'end' && 'text-right']" :style="h.width ? { width: h.width } : undefined">{{ h.title }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading"><td :colspan="headers.length" class="text-center py-8"><VProgressCircular indeterminate color="primary" size="32" /></td></tr>
              <tr v-else-if="items.length === 0"><td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">Aucune réception pour cette commande.</td></tr>
              <tr v-else v-for="item in items" :key="item.id" class="achats-row">
                <td class="py-3 px-4"><VChip size="small" color="primary" variant="tonal" class="code-chip">{{ item.numero }}</VChip></td>
                <td class="py-3 px-4 text-body-2">{{ item.numero_bl_fournisseur || '—' }}</td>
                <td class="py-3 px-4 text-body-2">{{ item.date_reception }}</td>
                <td class="py-3 px-4 text-body-2">{{ depotLibelle(item.depot_id) }}</td>
                <td class="py-3 px-4"><VChip :color="item.etat === 'validee' ? 'success' : item.etat === 'annulee' ? 'error' : 'default'" size="small" variant="tonal">{{ etatLabel(item.etat) }}</VChip></td>
                <td class="py-3 px-4 text-right">
                  <VBtn size="small" variant="text" prepend-icon="ri-pencil-line" @click="openEdit(item)">Modifier</VBtn>
                </td>
              </tr>
            </tbody>
          </VTable>
        </template>
        <div v-else class="pa-8 text-center text-medium-emphasis">Sélectionnez une commande fournisseur pour afficher les réceptions.</div>
      </VCardText>
    </VCard>
    <ReceptionFormModal
      v-if="selectedCommandeId && entrepriseId"
      v-model="formModalOpen"
      :entreprise-id="entrepriseId"
      :commande-fournisseur-id="selectedCommandeId"
      :reception-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />
  </div>
</template>

<style scoped>
.achats-page { max-width: 100%; }
.achats-card { border-radius: 12px; overflow: hidden; }
.achats-table :deep(thead th) { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.achats-row:hover { background-color: rgba(var(--v-theme-on-surface), 0.04); }
.code-chip { font-size: 0.75rem; font-weight: 600; }
</style>
