<script setup lang="ts">
import { getCommandeFournisseur, createCommandeFournisseur, updateCommandeFournisseur } from '@/api/achats'
import { listDepots } from '@/api/achats'
import { listEtatsDocument } from '@/api/commercial'
import { listDevises } from '@/api/parametrage'
import type { CommandeFournisseurCreate, CommandeFournisseurUpdate } from '@/api/types/achats'
import type { TiersResponse } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  commandeId: number | null
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
const depots = ref<{ id: number; code: string; libelle: string }[]>([])
const etats = ref<{ id: number; code: string; libelle: string }[]>([])
const devises = ref<{ id: number; code: string; libelle: string }[]>([])

const form = ref({
  fournisseur_id: 0,
  depot_id: null as number | null,
  numero: '',
  numero_fournisseur: '' as string | null,
  date_commande: '',
  date_livraison_prevue: '' as string | null,
  delai_livraison_jours: null as number | null,
  etat_id: 0,
  montant_ht: '' as string | number,
  montant_tva: '' as string | number,
  montant_ttc: '' as string | number,
  devise_id: 0,
  notes: '' as string | null,
})

const rules = {
  fournisseur_id: [() => form.value.fournisseur_id > 0 || 'Sélectionnez un fournisseur'],
  numero: [required()],
  date_commande: [required()],
  etat_id: [() => form.value.etat_id > 0 || 'Sélectionnez un état'],
  devise_id: [() => form.value.devise_id > 0 || 'Sélectionnez une devise'],
}

const fournisseurOptions = computed(() => props.fournisseurs.map(t => ({ title: `${t.code} – ${t.raison_sociale}`, value: t.id })))
const depotOptions = computed(() => [{ title: '— Aucun —', value: null }, ...depots.value.map(d => ({ title: `${d.code} – ${d.libelle}`, value: d.id }))])
const etatOptions = computed(() => etats.value.map(e => ({ title: `${e.code} – ${e.libelle}`, value: e.id })))
const deviseOptions = computed(() => devises.value.map(d => ({ title: `${d.code} – ${d.libelle}`, value: d.id })))

const isEdit = computed(() => props.commandeId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la commande fournisseur' : 'Nouvelle commande fournisseur'))

async function loadDepots() {
  try {
    depots.value = await listDepots({ entreprise_id: props.entrepriseId, limit: 100 })
  } catch {
    depots.value = []
  }
}
async function loadEtats() {
  try {
    etats.value = await listEtatsDocument({ limit: 100 })
  } catch {
    etats.value = []
  }
}
async function loadDevises() {
  try {
    devises.value = (await listDevises({ limit: 100 })).items ?? []
  } catch {
    devises.value = []
  }
}

async function load() {
  if (!props.commandeId) return
  loading.value = true
  try {
    const u = await getCommandeFournisseur(props.commandeId)
    form.value = {
      fournisseur_id: u.fournisseur_id,
      depot_id: u.depot_id ?? null,
      numero: u.numero,
      numero_fournisseur: u.numero_fournisseur ?? '',
      date_commande: u.date_commande?.slice(0, 10) ?? '',
      date_livraison_prevue: u.date_livraison_prevue?.slice(0, 10) ?? '',
      delai_livraison_jours: u.delai_livraison_jours ?? null,
      etat_id: u.etat_id,
      montant_ht: u.montant_ht ?? '',
      montant_tva: u.montant_tva ?? '',
      montant_ttc: u.montant_ttc ?? '',
      devise_id: u.devise_id ?? 0,
      notes: u.notes ?? '',
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
    depot_id: null,
    numero: '',
    numero_fournisseur: '',
    date_commande: today,
    date_livraison_prevue: '',
    delai_livraison_jours: null,
    etat_id: etats.value[0]?.id ?? 0,
    montant_ht: 0,
    montant_tva: 0,
    montant_ttc: 0,
    devise_id: devises.value[0]?.id ?? 0,
    notes: '',
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.commandeId] as const, async ([open, id]) => {
  if (open) {
    await Promise.all([loadDepots(), loadEtats(), loadDevises()])
  }
  if (open && id) load()
  if (open && !id) resetForm()
}, { immediate: true })

watch([etats, devises], () => {
  if (visible.value && !props.commandeId && !form.value.numero) {
    if (etats.value.length && !form.value.etat_id) form.value.etat_id = etats.value[0].id
    if (devises.value.length && !form.value.devise_id) form.value.devise_id = devises.value[0].id
  }
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
    html: isEdit.value ? `Enregistrer les modifications sur la commande « ${form.value.numero} » ?` : `Créer la commande « ${form.value.numero} » ?`,
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
    if (isEdit.value && props.commandeId) {
      await updateCommandeFournisseur(props.commandeId, {
        depot_id: form.value.depot_id,
        date_livraison_prevue: form.value.date_livraison_prevue || null,
        delai_livraison_jours: form.value.delai_livraison_jours,
        etat_id: form.value.etat_id,
        notes: form.value.notes?.trim() || null,
      } as CommandeFournisseurUpdate)
      toastStore.success('Commande mise à jour.')
    } else {
      await createCommandeFournisseur({
        entreprise_id: props.entrepriseId,
        fournisseur_id: form.value.fournisseur_id,
        depot_id: form.value.depot_id,
        numero: form.value.numero.trim(),
        numero_fournisseur: form.value.numero_fournisseur?.trim() || null,
        date_commande: form.value.date_commande,
        date_livraison_prevue: form.value.date_livraison_prevue || null,
        delai_livraison_jours: form.value.delai_livraison_jours,
        etat_id: form.value.etat_id,
        montant_ht: toNum(form.value.montant_ht),
        montant_tva: toNum(form.value.montant_tva),
        montant_ttc: toNum(form.value.montant_ttc),
        devise_id: form.value.devise_id,
        notes: form.value.notes?.trim() || null,
      } as CommandeFournisseurCreate)
      toastStore.success('Commande créée.')
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
          <div class="achats-modal-icon"><VIcon icon="ri-shopping-cart-2-line" size="28" /></div>
          <div>
            <h2 class="achats-modal-title">{{ modalTitle }}</h2>
            <p class="achats-modal-subtitle">Commande d'achat auprès d'un fournisseur</p>
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
              <VTextField v-model="form.numero" label="N° commande" :rules="rules.numero" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.numero_fournisseur" label="N° fournisseur (réf.)" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.depot_id" :items="depotOptions" item-title="title" item-value="value" label="Dépôt livraison" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.date_commande" label="Date commande" :rules="rules.date_commande" type="date" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.date_livraison_prevue" label="Livraison prévue" type="date" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.delai_livraison_jours" label="Délai (jours)" type="number" min="0" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.etat_id" :items="etatOptions" item-title="title" item-value="value" label="État" :rules="rules.etat_id" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.devise_id" :items="deviseOptions" item-title="title" item-value="value" label="Devise" :rules="rules.devise_id" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.montant_ht" label="Montant HT" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.montant_tva" label="Montant TVA" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.montant_ttc" label="Montant TTC" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
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
