<script setup lang="ts">
import {
  getProduit,
  listProduitConditionnements,
  createProduitConditionnement,
  updateProduitConditionnement,
  deleteProduitConditionnement,
  listConditionnements,
  listPrixByProduit,
  createPrixProduit,
  updatePrixProduit,
  deletePrixProduit,
  listVariantesByProduit,
  createVarianteProduit,
  updateVarianteProduit,
  deleteVarianteProduit,
  listCanauxVente,
} from '@/api/catalogue'
import { listPointsVente } from '@/api/parametrage'
import type {
  ProduitResponse,
  ProduitConditionnementResponse,
  ProduitConditionnementCreate,
  ProduitConditionnementUpdate,
  PrixProduitResponse,
  PrixProduitCreate,
  PrixProduitUpdate,
  VarianteProduitResponse,
  VarianteProduitCreate,
  VarianteProduitUpdate,
  ConditionnementResponse,
  CanalVenteResponse,
} from '@/api/types/catalogue'
import type { PointDeVenteResponse } from '@/api/types/parametrage'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ produitId: number; entrepriseId: number }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ close: [] }>()

const toastStore = useToastStore()
const activeTab = ref<string | number>(0)
const product = ref<ProduitResponse | null>(null)
const loadingProduct = ref(false)

// Conditionnements
const conditionnementsList = ref<ProduitConditionnementResponse[]>([])
const conditionnementsRef = ref<ConditionnementResponse[]>([])
const loadingCond = ref(false)
const condForm = ref({ open: false, id: null as number | null, conditionnement_id: null as number | null, quantite_unites: '' as string, prix_vente_ttc: '' as string })
const savingCond = ref(false)

// Prix
const prixList = ref<PrixProduitResponse[]>([])
const canaux = ref<CanalVenteResponse[]>([])
const pointsVente = ref<PointDeVenteResponse[]>([])
const loadingPrix = ref(false)
const prixForm = ref({
  open: false,
  id: null as number | null,
  canal_vente_id: null as number | null,
  point_de_vente_id: null as number | null,
  prix_ttc: '' as string,
  date_debut: '' as string,
  date_fin: '' as string,
})
const savingPrix = ref(false)

// Variantes
const variantesList = ref<VarianteProduitResponse[]>([])
const loadingVariantes = ref(false)
const varianteForm = ref({
  open: false,
  id: null as number | null,
  code: '' as string,
  libelle: '' as string,
  prix_ttc_supplement: '0' as string,
  stock_separe: false,
  actif: true,
})
const savingVariante = ref(false)

const condMap = computed(() => {
  const m: Record<number, string> = {}
  for (const c of conditionnementsRef.value) m[c.id] = `${c.code} — ${c.libelle}`
  return m
})
const canalMap = computed(() => {
  const m: Record<number, string> = {}
  for (const c of canaux.value) m[c.id] = c.libelle
  return m
})
const pdvMap = computed(() => {
  const m: Record<number, string> = {}
  for (const p of pointsVente.value) m[p.id] = p.libelle
  return m
})

async function loadProduct() {
  loadingProduct.value = true
  try {
    product.value = await getProduit(props.produitId)
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement produit')
    emit('close')
  } finally {
    loadingProduct.value = false
  }
}

async function loadConditionnements() {
  loadingCond.value = true
  try {
    const [list, refs] = await Promise.all([
      listProduitConditionnements(props.produitId, { limit: 200 }),
      listConditionnements({ entreprise_id: props.entrepriseId, limit: 200 }),
    ])
    conditionnementsList.value = list
    conditionnementsRef.value = refs
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement conditionnements')
  } finally {
    loadingCond.value = false
  }
}

async function loadPrix() {
  loadingPrix.value = true
  try {
    const [list, c, pv] = await Promise.all([
      listPrixByProduit(props.produitId, { limit: 200 }),
      listCanauxVente({ entreprise_id: props.entrepriseId, limit: 200 }),
      listPointsVente(props.entrepriseId, { limit: 200 }),
    ])
    prixList.value = list
    canaux.value = c
    pointsVente.value = pv
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement prix')
  } finally {
    loadingPrix.value = false
  }
}

async function loadVariantes() {
  loadingVariantes.value = true
  try {
    variantesList.value = await listVariantesByProduit(props.produitId, { limit: 200 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement variantes')
  } finally {
    loadingVariantes.value = false
  }
}

function onClose() {
  emit('close')
}

watch(visible, async (v) => {
  if (v && props.produitId) {
    activeTab.value = 0
    await loadProduct()
    await loadConditionnements()
  }
})

watch(activeTab, (tab) => {
  const t = Number(tab)
  if (t === 1 && prixList.value.length === 0 && visible.value) loadPrix()
  if (t === 2 && variantesList.value.length === 0 && visible.value) loadVariantes()
})

// --- Conditionnements CRUD ---
const condOptions = computed(() =>
  conditionnementsRef.value.map(c => ({ title: `${c.code} — ${c.libelle}`, value: c.id })),
)

function openAddCond() {
  condForm.value = { open: true, id: null, conditionnement_id: null, quantite_unites: '', prix_vente_ttc: '' }
}

function openEditCond(row: ProduitConditionnementResponse) {
  condForm.value = {
    open: true,
    id: row.id,
    conditionnement_id: row.conditionnement_id,
    quantite_unites: row.quantite_unites,
    prix_vente_ttc: row.prix_vente_ttc ?? '',
  }
}

function closeCondForm() {
  condForm.value.open = false
}

async function saveCond() {
  const q = Number(condForm.value.quantite_unites)
  if (Number.isNaN(q) || q <= 0) {
    toastStore.error('Quantité invalide')
    return
  }
  savingCond.value = true
  try {
    if (condForm.value.id != null) {
      await updateProduitConditionnement(condForm.value.id, {
        quantite_unites: q,
        prix_vente_ttc: condForm.value.prix_vente_ttc ? Number(condForm.value.prix_vente_ttc) : null,
      } as ProduitConditionnementUpdate)
      toastStore.success('Liaison mise à jour.')
    } else {
      if (condForm.value.conditionnement_id == null) {
        toastStore.error('Choisissez un conditionnement')
        return
      }
      await createProduitConditionnement({
        produit_id: props.produitId,
        conditionnement_id: condForm.value.conditionnement_id,
        quantite_unites: q,
        prix_vente_ttc: condForm.value.prix_vente_ttc ? Number(condForm.value.prix_vente_ttc) : null,
      } as ProduitConditionnementCreate)
      toastStore.success('Liaison ajoutée.')
    }
    closeCondForm()
    await loadConditionnements()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement')
  } finally {
    savingCond.value = false
  }
}

async function deleteCond(row: ProduitConditionnementResponse) {
  const ok = await Swal.fire({
    title: 'Supprimer la liaison ?',
    showCancelButton: true,
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
  })
  if (!ok.isConfirmed) return
  try {
    await deleteProduitConditionnement(row.id)
    toastStore.success('Liaison supprimée.')
    await loadConditionnements()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur suppression')
  }
}

// --- Prix CRUD ---
function openAddPrix() {
  const today = new Date().toISOString().slice(0, 10)
  prixForm.value = { open: true, id: null, canal_vente_id: null, point_de_vente_id: null, prix_ttc: '', date_debut: today, date_fin: '' }
}

function openEditPrix(row: PrixProduitResponse) {
  prixForm.value = {
    open: true,
    id: row.id,
    canal_vente_id: row.canal_vente_id ?? null,
    point_de_vente_id: row.point_de_vente_id ?? null,
    prix_ttc: row.prix_ttc,
    date_debut: row.date_debut?.slice(0, 10) ?? '',
    date_fin: row.date_fin?.slice(0, 10) ?? '',
  }
}

function closePrixForm() {
  prixForm.value.open = false
}

async function savePrix() {
  const prix = Number(prixForm.value.prix_ttc)
  if (Number.isNaN(prix) || prix < 0) {
    toastStore.error('Prix invalide')
    return
  }
  if (!prixForm.value.date_debut) {
    toastStore.error('Date de début requise')
    return
  }
  savingPrix.value = true
  try {
    if (prixForm.value.id != null) {
      await updatePrixProduit(prixForm.value.id, {
        canal_vente_id: prixForm.value.canal_vente_id,
        point_de_vente_id: prixForm.value.point_de_vente_id,
        prix_ttc: prix,
        date_debut: prixForm.value.date_debut,
        date_fin: prixForm.value.date_fin || null,
      } as PrixProduitUpdate)
      toastStore.success('Prix mis à jour.')
    } else {
      await createPrixProduit({
        produit_id: props.produitId,
        canal_vente_id: prixForm.value.canal_vente_id,
        point_de_vente_id: prixForm.value.point_de_vente_id,
        prix_ttc: prix,
        date_debut: prixForm.value.date_debut,
        date_fin: prixForm.value.date_fin || null,
      } as PrixProduitCreate)
      toastStore.success('Prix ajouté.')
    }
    closePrixForm()
    await loadPrix()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement')
  } finally {
    savingPrix.value = false
  }
}

async function deletePrix(row: PrixProduitResponse) {
  const ok = await Swal.fire({
    title: 'Supprimer ce prix ?',
    showCancelButton: true,
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
  })
  if (!ok.isConfirmed) return
  try {
    await deletePrixProduit(row.id)
    toastStore.success('Prix supprimé.')
    await loadPrix()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur suppression')
  }
}

// --- Variantes CRUD ---
function openAddVariante() {
  varianteForm.value = { open: true, id: null, code: '', libelle: '', prix_ttc_supplement: '0', stock_separe: false, actif: true }
}

function openEditVariante(row: VarianteProduitResponse) {
  varianteForm.value = {
    open: true,
    id: row.id,
    code: row.code,
    libelle: row.libelle,
    prix_ttc_supplement: row.prix_ttc_supplement,
    stock_separe: row.stock_separe,
    actif: row.actif,
  }
}

function closeVarianteForm() {
  varianteForm.value.open = false
}

async function saveVariante() {
  if (!varianteForm.value.code?.trim() || !varianteForm.value.libelle?.trim()) {
    toastStore.error('Code et libellé requis')
    return
  }
  savingVariante.value = true
  try {
    const supplement = Number(varianteForm.value.prix_ttc_supplement) || 0
    if (varianteForm.value.id != null) {
      await updateVarianteProduit(varianteForm.value.id, {
        code: varianteForm.value.code.trim(),
        libelle: varianteForm.value.libelle.trim(),
        prix_ttc_supplement: supplement,
        stock_separe: varianteForm.value.stock_separe,
        actif: varianteForm.value.actif,
      } as VarianteProduitUpdate)
      toastStore.success('Variante mise à jour.')
    } else {
      await createVarianteProduit({
        produit_id: props.produitId,
        code: varianteForm.value.code.trim(),
        libelle: varianteForm.value.libelle.trim(),
        prix_ttc_supplement: supplement,
        stock_separe: varianteForm.value.stock_separe,
        actif: varianteForm.value.actif,
      } as VarianteProduitCreate)
      toastStore.success('Variante ajoutée.')
    }
    closeVarianteForm()
    await loadVariantes()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement')
  } finally {
    savingVariante.value = false
  }
}

async function deleteVariante(row: VarianteProduitResponse) {
  const ok = await Swal.fire({
    title: 'Supprimer cette variante ?',
    showCancelButton: true,
    confirmButtonText: 'Supprimer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
  })
  if (!ok.isConfirmed) return
  try {
    await deleteVarianteProduit(row.id)
    toastStore.success('Variante supprimée.')
    await loadVariantes()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur suppression')
  }
}
</script>

<template>
  <VDialog :model-value="visible" max-width="960" persistent content-class="produit-detail-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="produit-detail-card overflow-hidden">
      <div class="d-flex align-center justify-space-between pa-4">
        <div class="d-flex align-center gap-3">
          <VAvatar color="primary" variant="tonal" size="48">
            <VIcon icon="ri-product-hunt-line" size="28" />
          </VAvatar>
          <div v-if="loadingProduct">
            <VProgressCircular indeterminate size="24" />
          </div>
          <div v-else-if="product">
            <h2 class="text-h6 font-weight-medium mb-0">
              {{ product.code }} — {{ product.libelle }}
            </h2>
            <p class="text-caption text-medium-emphasis mb-0">
              Détail produit : conditionnements, prix et variantes
            </p>
          </div>
        </div>
        <VBtn icon variant="text" @click="onClose">
          <VIcon icon="ri-close-line" size="24" />
        </VBtn>
      </div>
      <VDivider />
      <template v-if="product">
        <VTabs v-model="activeTab" class="px-4">
          <VTab :value="0">Conditionnements</VTab>
          <VTab :value="1">Prix</VTab>
          <VTab :value="2">Variantes</VTab>
        </VTabs>
        <VWindow v-model="activeTab" class="pa-4">
          <!-- Tab Conditionnements -->
          <VWindowItem :value="0">
            <div class="mb-3 d-flex justify-space-between align-center">
              <span class="text-body-2 text-medium-emphasis">Liaisons produit ↔ conditionnement</span>
              <VBtn size="small" color="primary" prepend-icon="ri-add-line" @click="openAddCond">Ajouter</VBtn>
            </div>
            <VTable v-if="loadingCond" class="mb-4">
              <tbody><tr><td class="text-center py-6"><VProgressCircular indeterminate size="28" /></td></tr></tbody>
            </VTable>
            <VTable v-else-if="conditionnementsList.length === 0" class="mb-4" density="compact">
              <tbody><tr><td class="text-medium-emphasis py-4">Aucun conditionnement associé.</td></tr></tbody>
            </VTable>
            <VTable v-else class="mb-4" density="compact">
              <thead>
                <tr>
                  <th>Conditionnement</th>
                  <th>Qté unités</th>
                  <th>Prix vente TTC</th>
                  <th width="100" class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in conditionnementsList" :key="row.id">
                  <td>{{ condMap[row.conditionnement_id] ?? `#${row.conditionnement_id}` }}</td>
                  <td>{{ row.quantite_unites }}</td>
                  <td>{{ row.prix_vente_ttc ?? '—' }}</td>
                  <td class="text-end">
                    <VBtn icon size="x-small" variant="text" @click="openEditCond(row)"><VIcon icon="ri-pencil-line" /></VBtn>
                    <VBtn icon size="x-small" variant="text" color="error" @click="deleteCond(row)"><VIcon icon="ri-delete-bin-line" /></VBtn>
                  </td>
                </tr>
              </tbody>
            </VTable>
            <VExpandTransition>
              <VCard v-if="condForm.open" variant="tonal" class="pa-4 mb-4">
                <VRow dense>
                  <VCol cols="12" md="4">
                    <VSelect
                      v-model="condForm.conditionnement_id"
                      :items="condOptions"
                      item-title="title"
                      item-value="value"
                      label="Conditionnement"
                      density="compact"
                      :disabled="condForm.id != null"
                      hide-details
                    />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="condForm.quantite_unites" label="Qté unités" type="number" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="condForm.prix_vente_ttc" label="Prix TTC" type="number" step="0.01" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="4" class="d-flex align-center gap-2">
                    <VBtn size="small" :loading="savingCond" @click="saveCond">Enregistrer</VBtn>
                    <VBtn size="small" variant="outlined" @click="closeCondForm">Annuler</VBtn>
                  </VCol>
                </VRow>
              </VCard>
            </VExpandTransition>
          </VWindowItem>

          <!-- Tab Prix -->
          <VWindowItem value="1">
            <div class="mb-3 d-flex justify-space-between align-center">
              <span class="text-body-2 text-medium-emphasis">Prix par canal / point de vente</span>
              <VBtn size="small" color="primary" prepend-icon="ri-add-line" @click="openAddPrix">Ajouter</VBtn>
            </div>
            <VTable v-if="loadingPrix" class="mb-4">
              <tbody><tr><td class="text-center py-6"><VProgressCircular indeterminate size="28" /></td></tr></tbody>
            </VTable>
            <VTable v-else-if="prixList.length === 0" class="mb-4" density="compact">
              <tbody><tr><td class="text-medium-emphasis py-4">Aucun prix défini.</td></tr></tbody>
            </VTable>
            <VTable v-else class="mb-4" density="compact">
              <thead>
                <tr>
                  <th>Canal</th>
                  <th>Point de vente</th>
                  <th>Prix TTC</th>
                  <th>Début</th>
                  <th>Fin</th>
                  <th width="100" class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in prixList" :key="row.id">
                  <td>{{ row.canal_vente_id != null ? (canalMap[row.canal_vente_id] ?? `#${row.canal_vente_id}`) : '—' }}</td>
                  <td>{{ row.point_de_vente_id != null ? (pdvMap[row.point_de_vente_id] ?? `#${row.point_de_vente_id}`) : '—' }}</td>
                  <td>{{ row.prix_ttc }}</td>
                  <td>{{ row.date_debut }}</td>
                  <td>{{ row.date_fin ?? '—' }}</td>
                  <td class="text-end">
                    <VBtn icon size="x-small" variant="text" @click="openEditPrix(row)"><VIcon icon="ri-pencil-line" /></VBtn>
                    <VBtn icon size="x-small" variant="text" color="error" @click="deletePrix(row)"><VIcon icon="ri-delete-bin-line" /></VBtn>
                  </td>
                </tr>
              </tbody>
            </VTable>
            <VExpandTransition>
              <VCard v-if="prixForm.open" variant="tonal" class="pa-4 mb-4">
                <VRow dense>
                  <VCol cols="12" md="3">
                    <VSelect
                      v-model="prixForm.canal_vente_id"
                      :items="canaux.map(c => ({ title: c.libelle, value: c.id }))"
                      item-title="title"
                      item-value="value"
                      label="Canal"
                      density="compact"
                      clearable
                      hide-details
                    />
                  </VCol>
                  <VCol cols="12" md="3">
                    <VSelect
                      v-model="prixForm.point_de_vente_id"
                      :items="pointsVente.map(p => ({ title: p.libelle, value: p.id }))"
                      item-title="title"
                      item-value="value"
                      label="Point de vente"
                      density="compact"
                      clearable
                      hide-details
                    />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="prixForm.prix_ttc" label="Prix TTC" type="number" step="0.01" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="prixForm.date_debut" label="Début" type="date" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="prixForm.date_fin" label="Fin" type="date" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" class="d-flex gap-2">
                    <VBtn size="small" :loading="savingPrix" @click="savePrix">Enregistrer</VBtn>
                    <VBtn size="small" variant="outlined" @click="closePrixForm">Annuler</VBtn>
                  </VCol>
                </VRow>
              </VCard>
            </VExpandTransition>
          </VWindowItem>

          <!-- Tab Variantes -->
          <VWindowItem :value="2">
            <div class="mb-3 d-flex justify-space-between align-center">
              <span class="text-body-2 text-medium-emphasis">Variantes du produit</span>
              <VBtn size="small" color="primary" prepend-icon="ri-add-line" @click="openAddVariante">Ajouter</VBtn>
            </div>
            <VTable v-if="loadingVariantes" class="mb-4">
              <tbody><tr><td class="text-center py-6"><VProgressCircular indeterminate size="28" /></td></tr></tbody>
            </VTable>
            <VTable v-else-if="variantesList.length === 0" class="mb-4" density="compact">
              <tbody><tr><td class="text-medium-emphasis py-4">Aucune variante.</td></tr></tbody>
            </VTable>
            <VTable v-else class="mb-4" density="compact">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Libellé</th>
                  <th>Supplément TTC</th>
                  <th>Stock séparé</th>
                  <th>Actif</th>
                  <th width="100" class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in variantesList" :key="row.id">
                  <td>{{ row.code }}</td>
                  <td>{{ row.libelle }}</td>
                  <td>{{ row.prix_ttc_supplement }}</td>
                  <td><VChip :color="row.stock_separe ? 'info' : 'default'" size="x-small">{{ row.stock_separe ? 'Oui' : 'Non' }}</VChip></td>
                  <td><VChip :color="row.actif ? 'success' : 'default'" size="x-small">{{ row.actif ? 'Oui' : 'Non' }}</VChip></td>
                  <td class="text-end">
                    <VBtn icon size="x-small" variant="text" @click="openEditVariante(row)"><VIcon icon="ri-pencil-line" /></VBtn>
                    <VBtn icon size="x-small" variant="text" color="error" @click="deleteVariante(row)"><VIcon icon="ri-delete-bin-line" /></VBtn>
                  </td>
                </tr>
              </tbody>
            </VTable>
            <VExpandTransition>
              <VCard v-if="varianteForm.open" variant="tonal" class="pa-4 mb-4">
                <VRow dense>
                  <VCol cols="12" md="3">
                    <VTextField v-model="varianteForm.code" label="Code" density="compact" :disabled="varianteForm.id != null" hide-details />
                  </VCol>
                  <VCol cols="12" md="3">
                    <VTextField v-model="varianteForm.libelle" label="Libellé" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VTextField v-model="varianteForm.prix_ttc_supplement" label="Suppl. TTC" type="number" step="0.01" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2" class="d-flex align-center">
                    <VSwitch v-model="varianteForm.stock_separe" label="Stock séparé" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" md="2" class="d-flex align-center">
                    <VSwitch v-model="varianteForm.actif" label="Actif" density="compact" hide-details />
                  </VCol>
                  <VCol cols="12" class="d-flex gap-2">
                    <VBtn size="small" :loading="savingVariante" @click="saveVariante">Enregistrer</VBtn>
                    <VBtn size="small" variant="outlined" @click="closeVarianteForm">Annuler</VBtn>
                  </VCol>
                </VRow>
              </VCard>
            </VExpandTransition>
          </VWindowItem>
        </VWindow>
      </template>
    </VCard>
  </VDialog>
</template>

<style scoped>
.produit-detail-dialog :deep(.v-overlay__content) { max-height: 90vh; overflow: auto; }
.produit-detail-card { border-radius: 16px; }
</style>
