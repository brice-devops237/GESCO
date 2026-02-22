<script setup lang="ts">
import { getProduit, createProduit, updateProduit, listFamillesProduits, listUnitesMesure, listTauxTva } from '@/api/catalogue'
import type { ProduitCreate, ProduitUpdate, TypeProduit } from '@/api/types/catalogue'
import type { FamilleProduitResponse, UniteMesureResponse, TauxTvaResponse } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ entrepriseId: number; produitId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const familles = ref<FamilleProduitResponse[]>([])
const unites = ref<UniteMesureResponse[]>([])
const tauxTva = ref<TauxTvaResponse[]>([])

const typeOptions: { title: string; value: TypeProduit }[] = [
  { title: 'Produit', value: 'produit' },
  { title: 'Service', value: 'service' },
  { title: 'Composant', value: 'composant' },
]

const form = ref({
  code: '',
  libelle: '',
  famille_id: null as number | null,
  type: 'produit' as TypeProduit,
  unite_vente_id: null as number | null,
  prix_vente_ttc: '' as number | string,
  taux_tva_id: null as number | null,
  actif: true,
})

const rules = {
  code: [required(), maxLength(50, 'Max. 50 caractères')],
  libelle: [required(), maxLength(120, 'Max. 120 caractères')],
  unite_vente_id: [required()],
  prix_vente_ttc: [required(), (v: string) => !isNaN(Number(v)) && Number(v) >= 0 || 'Prix ≥ 0'],
}

const isEdit = computed(() => props.produitId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le produit' : 'Nouveau produit'))
const familleOptions = computed(() => [{ title: '— Aucune', value: null as number | null }, ...familles.value.map(f => ({ title: `${f.code} — ${f.libelle}`, value: f.id }))])
const uniteOptions = computed(() => unites.value.map(u => ({ title: `${u.code} — ${u.libelle}`, value: u.id })))
const tauxTvaOptions = computed(() => [{ title: '— Aucun', value: null as number | null }, ...tauxTva.value.map(t => ({ title: `${t.code} (${t.taux} %)`, value: t.id }))])

async function loadRefs() {
  try {
    const [f, u, t] = await Promise.all([
      listFamillesProduits({ entreprise_id: props.entrepriseId, limit: 200 }),
      listUnitesMesure({ limit: 200 }),
      listTauxTva({ limit: 200 }),
    ])
    familles.value = f
    unites.value = u
    tauxTva.value = t
  } catch {
    familles.value = []
    unites.value = []
    tauxTva.value = []
  }
}

async function load() {
  if (!props.produitId) return
  loading.value = true
  try {
    const p = await getProduit(props.produitId)
    form.value = {
      code: p.code,
      libelle: p.libelle,
      famille_id: p.famille_id ?? null,
      type: (p.type as TypeProduit) || 'produit',
      unite_vente_id: p.unite_vente_id,
      prix_vente_ttc: p.prix_vente_ttc,
      taux_tva_id: p.taux_tva_id ?? null,
      actif: p.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.produitId] as const, async ([open, id]) => {
  if (open) await loadRefs()
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '', famille_id: null, type: 'produit', unite_vente_id: null, prix_vente_ttc: '', taux_tva_id: null, actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer le produit « ${form.value.code.trim() } » ?`,
    showCancelButton: true,
    confirmButtonText: isEdit.value ? 'Modifier' : 'Enregistrer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  saving.value = true
  try {
    const prix = Number(form.value.prix_vente_ttc)
    if (isEdit.value && props.produitId) {
      await updateProduit(props.produitId, {
        libelle: form.value.libelle.trim(),
        famille_id: form.value.famille_id,
        type: form.value.type,
        unite_vente_id: form.value.unite_vente_id!,
        prix_vente_ttc: isNaN(prix) ? form.value.prix_vente_ttc : prix,
        taux_tva_id: form.value.taux_tva_id,
        actif: form.value.actif,
      } as ProduitUpdate)
      toastStore.success('Produit mis à jour.')
    } else {
      await createProduit({
        entreprise_id: props.entrepriseId,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        famille_id: form.value.famille_id,
        type: form.value.type,
        unite_vente_id: form.value.unite_vente_id!,
        prix_vente_ttc: isNaN(prix) ? form.value.prix_vente_ttc : prix,
        taux_tva_id: form.value.taux_tva_id,
        actif: form.value.actif,
      } as ProduitCreate)
      toastStore.success('Produit créé.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de l\'enregistrement.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <VDialog :model-value="visible" max-width="640" persistent content-class="catalogue-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="catalogue-modal-card overflow-hidden">
      <div class="catalogue-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="catalogue-modal-icon"><VIcon icon="ri-product-hunt-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">Code, libellé, famille, unité et prix</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="catalogue-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="catalogue-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.famille_id" :items="familleOptions" item-title="title" item-value="value" label="Famille" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.type" :items="typeOptions" item-title="title" item-value="value" label="Type" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.unite_vente_id" :items="uniteOptions" :rules="rules.unite_vente_id" item-title="title" item-value="value" label="Unité de vente" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.prix_vente_ttc" label="Prix de vente TTC" :rules="rules.prix_vente_ttc" type="number" step="0.01" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.taux_tva_id" :items="tauxTvaOptions" item-title="title" item-value="value" label="Taux TVA" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6" class="d-flex align-center">
              <VSwitch v-model="form.actif" label="Actif" color="primary" hide-details />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4 gap-2">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onClose">Annuler</VBtn>
        <VBtn color="primary" variant="flat" :loading="saving" @click="onSubmit">Enregistrer</VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.catalogue-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.catalogue-modal-card { border-radius: 16px; overflow: hidden; }
.catalogue-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.catalogue-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.catalogue-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.catalogue-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.catalogue-modal-close { flex-shrink: 0; }
.catalogue-modal-body { padding: 0 24px 16px; }
</style>
