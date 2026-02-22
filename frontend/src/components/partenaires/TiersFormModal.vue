<script setup lang="ts">
import { getTiers, createTiers, updateTiers } from '@/api/partenaires'
import { listCanauxVente } from '@/api/catalogue'
import type { TiersCreate, TiersUpdate } from '@/api/types/partenaires'
import type { TypeTiersResponse } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  tiersId: number | null
  entrepriseId: number
  typesTiers: TypeTiersResponse[]
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const canauxVente = ref<{ id: number; code: string; libelle: string }[]>([])

const PAYS_OPTIONS = [
  { title: 'Cameroun', value: 'CMR' },
  { title: 'France', value: 'FRA' },
  { title: 'Sénégal', value: 'SEN' },
  { title: 'Côte d\'Ivoire', value: 'CIV' },
  { title: 'Gabon', value: 'GAB' },
  { title: 'Autre', value: 'XXX' },
]

const form = ref({
  code: '',
  raison_sociale: '',
  sigle: '' as string | null,
  type_tiers_id: 0,
  nom_contact: '' as string | null,
  niu: '' as string | null,
  rccm: '' as string | null,
  adresse: '' as string | null,
  code_postal: '' as string | null,
  boite_postale: '' as string | null,
  ville: '' as string | null,
  region: '' as string | null,
  pays: 'CMR',
  telephone: '' as string | null,
  telephone_secondaire: '' as string | null,
  email: '' as string | null,
  canal_vente_id: null as number | null,
  limite_credit: null as number | string | null,
  delai_paiement_jours: null as number | null,
  compte_bancaire: '' as string | null,
  mobile_money_numero: '' as string | null,
  mobile_money_operateur: '' as string | null,
  segment: '' as string | null,
  notes: '' as string | null,
  actif: true,
})

const rules = {
  code: [required(), maxLength(30, 'Max. 30 caractères')],
  raison_sociale: [required(), maxLength(255, 'Max. 255 caractères')],
  type_tiers_id: [() => form.value.type_tiers_id > 0 || 'Sélectionnez un type de tiers'],
}

const typeOptions = computed(() =>
  props.typesTiers.map(t => ({ title: `${t.code} – ${t.libelle}`, value: t.id })),
)
const canalVenteOptions = computed(() => [
  { title: '— Aucun —', value: null },
  ...canauxVente.value.map(c => ({ title: `${c.code} – ${c.libelle}`, value: c.id })),
])

const isEdit = computed(() => props.tiersId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le partenaire' : 'Nouveau partenaire (client / fournisseur)'))

async function loadCanauxVente() {
  try {
    canauxVente.value = await listCanauxVente({ entreprise_id: props.entrepriseId, limit: 100 })
  } catch {
    canauxVente.value = []
  }
}

async function load() {
  if (!props.tiersId) return
  loading.value = true
  try {
    const u = await getTiers(props.tiersId)
    form.value = {
      code: u.code,
      raison_sociale: u.raison_sociale,
      sigle: u.sigle ?? '',
      type_tiers_id: u.type_tiers_id,
      nom_contact: u.nom_contact ?? '',
      niu: u.niu ?? '',
      rccm: u.rccm ?? '',
      adresse: u.adresse ?? '',
      code_postal: u.code_postal ?? '',
      boite_postale: u.boite_postale ?? '',
      ville: u.ville ?? '',
      region: u.region ?? '',
      pays: u.pays || 'CMR',
      telephone: u.telephone ?? '',
      telephone_secondaire: u.telephone_secondaire ?? '',
      email: u.email ?? '',
      canal_vente_id: u.canal_vente_id ?? null,
      limite_credit: u.limite_credit != null ? Number(u.limite_credit) : null,
      delai_paiement_jours: u.delai_paiement_jours ?? null,
      compte_bancaire: u.compte_bancaire ?? '',
      mobile_money_numero: u.mobile_money_numero ?? '',
      mobile_money_operateur: u.mobile_money_operateur ?? '',
      segment: u.segment ?? '',
      notes: u.notes ?? '',
      actif: u.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    code: '',
    raison_sociale: '',
    sigle: '',
    type_tiers_id: props.typesTiers[0]?.id ?? 0,
    nom_contact: '',
    niu: '',
    rccm: '',
    adresse: '',
    code_postal: '',
    boite_postale: '',
    ville: '',
    region: '',
    pays: 'CMR',
    telephone: '',
    telephone_secondaire: '',
    email: '',
    canal_vente_id: null,
    limite_credit: null,
    delai_paiement_jours: null,
    compte_bancaire: '',
    mobile_money_numero: '',
    mobile_money_operateur: '',
    segment: '',
    notes: '',
    actif: true,
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.tiersId] as const, async ([open, id]) => {
  if (open) await loadCanauxVente()
  if (open && id) load()
  if (open && !id) resetForm()
}, { immediate: true })

watch(() => props.typesTiers, (types) => {
  if (visible.value && !props.tiersId && types.length && !form.value.type_tiers_id) form.value.type_tiers_id = types[0].id
}, { immediate: true })

function toNum(val: number | string | null): number | null {
  if (val == null || val === '') return null
  const n = Number(val)
  return Number.isNaN(n) ? null : n
}

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value ? `Enregistrer les modifications sur « ${form.value.raison_sociale} » ?` : `Créer le partenaire « ${form.value.raison_sociale.trim()} » ?`,
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
    const payload = {
      type_tiers_id: form.value.type_tiers_id,
      code: form.value.code.trim(),
      raison_sociale: form.value.raison_sociale.trim(),
      sigle: form.value.sigle?.trim() || null,
      nom_contact: form.value.nom_contact?.trim() || null,
      niu: form.value.niu?.trim() || null,
      rccm: form.value.rccm?.trim() || null,
      adresse: form.value.adresse?.trim() || null,
      code_postal: form.value.code_postal?.trim() || null,
      boite_postale: form.value.boite_postale?.trim() || null,
      ville: form.value.ville?.trim() || null,
      region: form.value.region?.trim() || null,
      pays: form.value.pays,
      telephone: form.value.telephone?.trim() || null,
      telephone_secondaire: form.value.telephone_secondaire?.trim() || null,
      email: form.value.email?.trim() || null,
      canal_vente_id: form.value.canal_vente_id ?? null,
      limite_credit: toNum(form.value.limite_credit),
      delai_paiement_jours: form.value.delai_paiement_jours ?? null,
      compte_bancaire: form.value.compte_bancaire?.trim() || null,
      mobile_money_numero: form.value.mobile_money_numero?.trim() || null,
      mobile_money_operateur: form.value.mobile_money_operateur?.trim() || null,
      segment: form.value.segment?.trim() || null,
      notes: form.value.notes?.trim() || null,
      actif: form.value.actif,
    }
    if (isEdit.value && props.tiersId) {
      await updateTiers(props.tiersId, payload as TiersUpdate)
      toastStore.success('Partenaire mis à jour.')
    } else {
      await createTiers({
        ...payload,
        entreprise_id: props.entrepriseId,
      } as TiersCreate)
      toastStore.success('Partenaire créé.')
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
  <VDialog :model-value="visible" max-width="720" persistent content-class="partenaires-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="partenaires-modal-card overflow-hidden">
      <div class="partenaires-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="partenaires-modal-icon"><VIcon icon="ri-group-line" size="28" /></div>
          <div>
            <h2 class="partenaires-modal-title">{{ modalTitle }}</h2>
            <p class="partenaires-modal-subtitle">Identification légale, adresse, conditions commerciales et moyens de paiement</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="partenaires-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="partenaires-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <!-- Identification -->
          <p class="text-subtitle-2 text-medium-emphasis mb-2">Identification</p>
          <VRow dense class="mb-4">
            <VCol cols="12" sm="4">
              <VTextField v-model="form.code" label="Code partenaire" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VSelect v-model="form.type_tiers_id" :items="typeOptions" item-title="title" item-value="value" label="Type (client / fournisseur)" :rules="rules.type_tiers_id" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.sigle" label="Sigle" variant="outlined" density="compact" hide-details="auto" placeholder="Ex. SA, SARL" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.raison_sociale" label="Raison sociale" :rules="rules.raison_sociale" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.nom_contact" label="Contact principal (nom)" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.niu" label="NIU" variant="outlined" density="compact" hide-details="auto" placeholder="Numéro fiscal" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.rccm" label="RCCM" variant="outlined" density="compact" hide-details="auto" placeholder="Registre commerce" />
            </VCol>
          </VRow>

          <!-- Adresse -->
          <p class="text-subtitle-2 text-medium-emphasis mb-2">Adresse</p>
          <VRow dense class="mb-4">
            <VCol cols="12">
              <VTextField v-model="form.adresse" label="Adresse" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.code_postal" label="Code postal" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.boite_postale" label="Boîte postale" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.ville" label="Ville" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.region" label="Région" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.pays" :items="PAYS_OPTIONS" item-title="title" item-value="value" label="Pays" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
          </VRow>

          <!-- Coordonnées & commercial -->
          <p class="text-subtitle-2 text-medium-emphasis mb-2">Coordonnées et commercial</p>
          <VRow dense class="mb-4">
            <VCol cols="12" sm="4">
              <VTextField v-model="form.telephone" label="Téléphone" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.telephone_secondaire" label="Téléphone secondaire" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.email" label="Email" type="email" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.canal_vente_id" :items="canalVenteOptions" item-title="title" item-value="value" label="Canal de vente" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.limite_credit" label="Limite crédit" type="number" min="0" step="0.01" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.delai_paiement_jours" label="Délai paiement (jours)" type="number" min="0" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
          </VRow>

          <!-- Paiement -->
          <p class="text-subtitle-2 text-medium-emphasis mb-2">Moyens de paiement</p>
          <VRow dense class="mb-4">
            <VCol cols="12" sm="6">
              <VTextField v-model="form.compte_bancaire" label="Compte bancaire / IBAN" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.mobile_money_numero" label="Mobile Money (n°)" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField v-model="form.mobile_money_operateur" label="Opérateur" variant="outlined" density="compact" hide-details="auto" placeholder="MTN, Orange…" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.segment" label="Segment" variant="outlined" density="compact" hide-details="auto" placeholder="Ex. Grand compte, PME" />
            </VCol>
          </VRow>

          <!-- Notes & statut -->
          <VRow dense>
            <VCol cols="12">
              <VTextField v-model="form.notes" label="Notes internes" variant="outlined" density="compact" hide-details="auto" multiline rows="2" />
            </VCol>
            <VCol cols="12">
              <VSwitch v-model="form.actif" label="Partenaire actif" color="primary" hide-details />
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
.partenaires-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.partenaires-modal-card { border-radius: 16px; overflow: hidden; }
.partenaires-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.partenaires-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.partenaires-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.partenaires-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.partenaires-modal-close { flex-shrink: 0; }
.partenaires-modal-body { padding: 0 24px 16px; max-height: 60vh; overflow-y: auto; }
</style>
