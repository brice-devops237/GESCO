<script setup lang="ts">
import { createReglement } from '@/api/tresorerie'
import { listModesPaiement, listComptesTresorerie } from '@/api/tresorerie'
import { listTiers } from '@/api/partenaires'
import type { ModePaiementResponse } from '@/api/types/tresorerie'
import type { CompteTresorerieResponse } from '@/api/types/tresorerie'
import type { TiersResponse } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required } = useFormValidation()

const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const modesPaiement = ref<ModePaiementResponse[]>([])
const comptesTresorerie = ref<CompteTresorerieResponse[]>([])
const tiers = ref<TiersResponse[]>([])

const typeReglementOptions = [
  { title: 'Encaissement', value: 'encaissement' },
  { title: 'Décaissement', value: 'decaissement' },
]

const form = ref({
  type_reglement: 'encaissement',
  tiers_id: null as number | null,
  montant: '' as string | number,
  date_reglement: '',
  date_valeur: '' as string | null,
  mode_paiement_id: null as number | null,
  compte_tresorerie_id: null as number | null,
  facture_id: null as number | null,
  facture_fournisseur_id: null as number | null,
  reference: '' as string | null,
  notes: '' as string | null,
})

const rules = {
  tiers_id: [required()],
  montant: [required()],
  date_reglement: [required()],
  mode_paiement_id: [required()],
  compte_tresorerie_id: [required()],
}

const modePaiementItems = computed(() =>
  modesPaiement.value.map(m => ({ title: `${m.code} - ${m.libelle}`, value: m.id })),
)
const compteTresorerieItems = computed(() =>
  comptesTresorerie.value.map(c => ({ title: `${c.libelle} (${c.type_compte})`, value: c.id })),
)
const tiersItems = computed(() =>
  tiers.value.map(t => ({ title: `${t.code || ''} - ${t.raison_sociale || 'Tiers'}`, value: t.id })),
)

async function loadOptions() {
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) return
  try {
    const [modes, comptes, tiersList] = await Promise.all([
      listModesPaiement({ entreprise_id: entrepriseId, limit: 100 }),
      listComptesTresorerie({ entreprise_id: entrepriseId, limit: 100 }),
      listTiers({ entreprise_id: entrepriseId, limit: 500 }),
    ])
    modesPaiement.value = modes
    comptesTresorerie.value = comptes
    tiers.value = tiersList
  } catch {
    modesPaiement.value = []
    comptesTresorerie.value = []
    tiers.value = []
  }
}

function resetForm() {
  const today = new Date().toISOString().slice(0, 10)
  form.value = {
    type_reglement: 'encaissement',
    tiers_id: null,
    montant: '',
    date_reglement: today,
    date_valeur: today,
    mode_paiement_id: null,
    compte_tresorerie_id: null,
    facture_id: null,
    facture_fournisseur_id: null,
    reference: '',
    notes: '',
  }
}

function onClose() {
  emit('cancel')
}

watch(visible, (open) => {
  if (open) {
    loadOptions()
    resetForm()
  }
})

async function onSubmit() {
  const valid = (await formRef.value?.validate().then(r => r.valid)) ?? false
  if (!valid) return

  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) {
    toastStore.error('Entreprise non définie.')
    return
  }
  if (form.value.tiers_id == null || form.value.mode_paiement_id == null || form.value.compte_tresorerie_id == null) {
    toastStore.error('Tiers, mode de paiement et compte trésorerie sont requis.')
    return
  }
  const montantNum = Number(form.value.montant)
  if (Number.isNaN(montantNum) || montantNum <= 0) {
    toastStore.error('Montant invalide.')
    return
  }

  const confirmResult = await Swal.fire({
    title: 'Enregistrer le règlement',
    html: `Montant <b>${form.value.montant}</b> – Tiers sélectionné. Confirmer ?`,
    showCancelButton: true,
    confirmButtonText: 'Enregistrer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!confirmResult.isConfirmed) return

  saving.value = true
  try {
    const factureId = form.value.facture_id != null && form.value.facture_id !== '' ? Number(form.value.facture_id) : null
    const factureFournisseurId = form.value.facture_fournisseur_id != null && form.value.facture_fournisseur_id !== '' ? Number(form.value.facture_fournisseur_id) : null
    await createReglement({
      entreprise_id: entrepriseId,
      type_reglement: form.value.type_reglement,
      tiers_id: form.value.tiers_id,
      montant: montantNum,
      date_reglement: form.value.date_reglement,
      date_valeur: form.value.date_valeur || null,
      mode_paiement_id: form.value.mode_paiement_id,
      compte_tresorerie_id: form.value.compte_tresorerie_id,
      facture_id: Number.isNaN(factureId) ? null : factureId,
      facture_fournisseur_id: Number.isNaN(factureFournisseurId) ? null : factureFournisseurId,
      reference: form.value.reference?.trim() || null,
      notes: form.value.notes?.trim() || null,
    })
    toastStore.success('Règlement enregistré.')
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de l\'enregistrement.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <VDialog
    :model-value="visible"
    max-width="640"
    persistent
    content-class="reglement-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="reglement-modal-card overflow-hidden">
      <div class="d-flex align-center justify-space-between pa-4 pb-2">
        <h2 class="text-h6">Nouveau règlement</h2>
        <VBtn icon variant="text" size="small" @click="onClose">
          <VIcon icon="ri-close-line" />
        </VBtn>
      </div>
      <VCardText class="pt-0">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.type_reglement"
                :items="typeReglementOptions"
                item-title="title"
                item-value="value"
                label="Type"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.tiers_id"
                :items="tiersItems"
                :rules="rules.tiers_id"
                label="Tiers"
                variant="outlined"
                density="compact"
                hide-details="auto"
                clearable
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.montant"
                label="Montant"
                :rules="rules.montant"
                type="number"
                step="0.01"
                min="0"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.date_reglement"
                label="Date de règlement"
                :rules="rules.date_reglement"
                type="date"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.date_valeur"
                label="Date de valeur (optionnel)"
                type="date"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.mode_paiement_id"
                :items="modePaiementItems"
                :rules="rules.mode_paiement_id"
                label="Mode de paiement"
                variant="outlined"
                density="compact"
                hide-details="auto"
                clearable
              />
            </VCol>
            <VCol cols="12">
              <VSelect
                v-model="form.compte_tresorerie_id"
                :items="compteTresorerieItems"
                :rules="rules.compte_tresorerie_id"
                label="Compte trésorerie"
                variant="outlined"
                density="compact"
                hide-details="auto"
                clearable
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.reference"
                label="Référence (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.facture_id"
                label="N° facture client (optionnel)"
                type="number"
                variant="outlined"
                density="compact"
                hide-details="auto"
                placeholder="ID facture"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.facture_fournisseur_id"
                label="N° facture fournisseur (optionnel)"
                type="number"
                variant="outlined"
                density="compact"
                hide-details="auto"
                placeholder="ID facture fournisseur"
              />
            </VCol>
            <VCol cols="12">
              <VTextField
                v-model="form.notes"
                label="Notes (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
                multiline
                rows="2"
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4">
        <VSpacer />
        <VBtn variant="outlined" color="secondary" :disabled="saving" @click="onClose">
          Annuler
        </VBtn>
        <VBtn color="primary" :loading="saving" @click="onSubmit">
          Enregistrer
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.reglement-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}
.reglement-modal-card {
  border-radius: 12px;
}
</style>
