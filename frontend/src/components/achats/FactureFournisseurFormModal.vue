<script setup lang="ts">
import { getFactureFournisseur, createFactureFournisseur, updateFactureFournisseur, listCommandesFournisseurs } from '@/api/achats'
import { listDevises } from '@/api/parametrage'
import type { FactureFournisseurCreate, FactureFournisseurUpdate } from '@/api/types/achats'
import type { TiersResponse } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  factureId: number | null
  entrepriseId: number
  fournisseurs: TiersResponse[]
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const firstFieldRef = ref<{ focus: () => void } | null>(null)
const commandes = ref<{ id: number; numero: string }[]>([])
const devises = ref<{ id: number; code: string; libelle: string }[]>([])

const typeFactureItems = [
  { title: 'Facture', value: 'facture' },
  { title: 'Avoir', value: 'avoir' },
  { title: 'Proforma', value: 'proforma' },
]
const statutPaiementItems = [
  { title: 'Non payé', value: 'non_paye' },
  { title: 'Partiel', value: 'partiel' },
  { title: 'Payé', value: 'paye' },
]

const form = ref({
  fournisseur_id: 0,
  commande_fournisseur_id: null as number | null,
  numero_fournisseur: '',
  type_facture: 'facture',
  date_facture: '',
  date_echeance: '' as string | null,
  date_reception_facture: '' as string | null,
  montant_ht: '' as string | number,
  montant_tva: '' as string | number,
  montant_ttc: '' as string | number,
  montant_restant_du: '' as string | number,
  devise_id: 0,
  statut_paiement: 'non_paye',
  notes: '' as string | null,
})

const rules = {
  fournisseur_id: [() => form.value.fournisseur_id > 0 || 'Sélectionnez un fournisseur'],
  numero_fournisseur: [required()],
  date_facture: [required()],
  devise_id: [() => form.value.devise_id > 0 || 'Sélectionnez une devise'],
}

const fournisseurOptions = computed(() => props.fournisseurs.map(t => ({ title: `${t.code} – ${t.raison_sociale}`, value: t.id })))
const commandeOptions = computed(() => [{ title: '— Aucune —', value: null }, ...commandes.value.map(c => ({ title: c.numero, value: c.id }))])
const deviseOptions = computed(() => devises.value.map(d => ({ title: `${d.code} – ${d.libelle}`, value: d.id })))

const isEdit = computed(() => props.factureId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la facture fournisseur' : 'Nouvelle facture fournisseur'))

async function loadCommandes() {
  try {
    const list = await listCommandesFournisseurs({
      entreprise_id: props.entrepriseId,
      fournisseur_id: form.value.fournisseur_id || undefined,
      limit: 200,
    })
    commandes.value = list.map(c => ({ id: c.id, numero: c.numero }))
  } catch {
    commandes.value = []
  }
}
async function loadDevises() {
  try {
    devises.value = (await listDevises({ limit: 100 })).items ?? []
  } catch {
    devises.value = []
  }
}

watch(() => form.value.fournisseur_id, () => { loadCommandes() }, { immediate: false })

async function load() {
  if (!props.factureId) return
  loading.value = true
  try {
    const u = await getFactureFournisseur(props.factureId)
    form.value = {
      fournisseur_id: u.fournisseur_id,
      commande_fournisseur_id: u.commande_fournisseur_id ?? null,
      numero_fournisseur: u.numero_fournisseur,
      type_facture: u.type_facture ?? 'facture',
      date_facture: u.date_facture?.slice(0, 10) ?? '',
      date_echeance: u.date_echeance?.slice(0, 10) ?? '',
      date_reception_facture: u.date_reception_facture?.slice(0, 10) ?? '',
      montant_ht: '',
      montant_tva: '',
      montant_ttc: u.montant_ttc ?? '',
      montant_restant_du: u.montant_restant_du ?? '',
      devise_id: 0,
      statut_paiement: u.statut_paiement ?? 'non_paye',
      notes: '',
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  const today = new Date().toISOString().slice(0, 10)
  form.value = {
    fournisseur_id: props.fournisseurs[0]?.id ?? 0,
    commande_fournisseur_id: null,
    numero_fournisseur: '',
    type_facture: 'facture',
    date_facture: today,
    date_echeance: '',
    date_reception_facture: '',
    montant_ht: 0,
    montant_tva: 0,
    montant_ttc: 0,
    montant_restant_du: 0,
    devise_id: devises.value[0]?.id ?? 0,
    statut_paiement: 'non_paye',
    notes: '',
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.factureId] as const, async ([open, id]) => {
  if (open) await loadDevises()
  if (open && id) load()
  if (open && !id) { resetForm(); await loadCommandes() }
}, { immediate: true })

watch([devises], () => {
  if (visible.value && !props.factureId && devises.value.length && !form.value.devise_id) form.value.devise_id = devises.value[0].id
}, { immediate: true })

function toNum(v: string | number | null): number {
  if (v == null || v === '') return 0
  const n = Number(v)
  return Number.isNaN(n) ? 0 : n
}

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value ? `Enregistrer les modifications sur la facture « ${form.value.numero_fournisseur} » ?` : `Créer la facture « ${form.value.numero_fournisseur} » ?`,
    showCancelButton: true,
    confirmButtonText: isEdit.value ? 'Modifier' : 'Créer',
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
    if (isEdit.value && props.factureId) {
      await updateFactureFournisseur(props.factureId, {
        type_facture: form.value.type_facture,
        date_echeance: form.value.date_echeance || null,
        date_reception_facture: form.value.date_reception_facture || null,
        montant_restant_du: toNum(form.value.montant_restant_du),
        statut_paiement: form.value.statut_paiement,
        notes: form.value.notes?.trim() || null,
      } as FactureFournisseurUpdate)
      toastStore.success('Facture mise à jour.')
    } else {
      await createFactureFournisseur({
        entreprise_id: props.entrepriseId,
        fournisseur_id: form.value.fournisseur_id,
        commande_fournisseur_id: form.value.commande_fournisseur_id,
        numero_fournisseur: form.value.numero_fournisseur.trim(),
        type_facture: form.value.type_facture,
        date_facture: form.value.date_facture,
        date_echeance: form.value.date_echeance || null,
        date_reception_facture: form.value.date_reception_facture || null,
        montant_ht: toNum(form.value.montant_ht),
        montant_tva: toNum(form.value.montant_tva),
        montant_ttc: toNum(form.value.montant_ttc),
        montant_restant_du: toNum(form.value.montant_restant_du),
        devise_id: form.value.devise_id,
        statut_paiement: form.value.statut_paiement,
        notes: form.value.notes?.trim() || null,
      } as FactureFournisseurCreate)
      toastStore.success('Facture créée.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement.')
  } finally {
    saving.value = false
  }
}

// Éviter l’avertissement aria-hidden : focus sur le premier champ à l’ouverture
watch([visible, loading], () => {
  if (visible.value && !loading.value) nextTick(() => firstFieldRef.value?.focus())
})
</script>

<template>
  <VDialog :model-value="visible" max-width="640" persistent content-class="achats-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="achats-modal-card overflow-hidden">
      <div class="achats-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="achats-modal-icon"><VIcon icon="ri-bill-line" size="28" /></div>
          <div>
            <h2 class="achats-modal-title">{{ modalTitle }}</h2>
            <p class="achats-modal-subtitle">Facture d'achat (fournisseur, avoir, proforma)</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="achats-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="achats-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VSelect ref="firstFieldRef" v-model="form.fournisseur_id" :items="fournisseurOptions" item-title="title" item-value="value" label="Fournisseur" :rules="rules.fournisseur_id" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.commande_fournisseur_id" :items="commandeOptions" item-title="title" item-value="value" label="Commande liée (optionnel)" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.numero_fournisseur" label="N° facture fournisseur" :rules="rules.numero_fournisseur" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.type_facture" :items="typeFactureItems" item-title="title" item-value="value" label="Type" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.date_facture" label="Date facture" :rules="rules.date_facture" type="date" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.date_echeance" label="Date échéance" type="date" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.date_reception_facture" label="Date réception facture" type="date" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.devise_id" :items="deviseOptions" item-title="title" item-value="value" label="Devise" :rules="rules.devise_id" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.statut_paiement" :items="statutPaiementItems" item-title="title" item-value="value" label="Statut paiement" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.montant_ht" label="Montant HT" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.montant_tva" label="TVA" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.montant_ttc" label="TTC" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.montant_restant_du" label="Restant dû" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.notes" label="Notes" variant="outlined" density="compact" hide-details="auto" multiline rows="2" />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4 gap-2">
        <VBtn variant="outlined" color="secondary" :disabled="saving" @click="onClose">Annuler</VBtn>
        <VBtn color="primary" :loading="saving" @click="onSubmit">{{ isEdit ? 'Enregistrer' : 'Créer' }}</VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.achats-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.achats-modal-card { border-radius: 16px; overflow: hidden; }
.achats-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.achats-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.achats-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.achats-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.achats-modal-close { flex-shrink: 0; }
.achats-modal-body { padding: 0 24px 16px; }
</style>
