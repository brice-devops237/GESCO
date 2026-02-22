<script setup lang="ts">
import {
  getEntreprise,
  createEntreprise,
  updateEntreprise,
} from '@/api/parametrage'
import type {
  EntrepriseCreate,
  EntrepriseUpdate,
  EntrepriseResponse,
  RegimeFiscal,
  ModeGestion,
} from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import countriesList from '@/data/countries.json'
import Swal from 'sweetalert2'

const props = defineProps<{
  entrepriseId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{
  saved: []
  cancel: []
}>()

const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const regimeOptions: { title: string; value: RegimeFiscal }[] = [
  { title: 'Informel', value: 'informel' },
  { title: 'Libératoire', value: 'liberatoire' },
  { title: 'Forfait', value: 'forfait' },
  { title: 'Réel simplifié', value: 'reel_simplifie' },
  { title: 'Réel normal', value: 'reel_normal' },
]

const modeOptions: { title: string; value: ModeGestion }[] = [
  { title: 'Standard', value: 'standard' },
  { title: 'Simplifié', value: 'simplifie' },
]

/** Tous les pays du monde (ISO 3166-1 alpha-2), dédupliqués par code pour éviter les IDs dupliqués Vuetify */
const countryOptions = (() => {
  const list = countriesList as { code: string; name: string }[]
  const seen = new Set<string>()
  return list
    .filter(c => {
      if (seen.has(c.code)) return false
      seen.add(c.code)
      return true
    })
    .map(c => ({ ...c, title: `${c.name} (${c.code})` }))
})()

const form = ref<Record<string, unknown>>({
  code: '',
  raison_sociale: '',
  sigle: '',
  niu: '',
  regime_fiscal: 'reel_simplifie' as RegimeFiscal,
  mode_gestion: 'standard' as ModeGestion,
  pays: 'CM',
  devise_principale: 'XAF',
  ville: '',
  region: '',
  adresse: '',
  telephone: '',
  email: '',
  actif: true,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  raison_sociale: [required(), maxLength(200, 'Max. 200 caractères')],
}

const isEdit = computed(() => props.entrepriseId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier l\'entreprise' : 'Nouvelle entreprise'))

async function loadEntreprise() {
  if (!props.entrepriseId) return
  loading.value = true
  try {
    const e = await getEntreprise(props.entrepriseId)
    form.value = {
      code: e.code,
      raison_sociale: e.raison_sociale,
      sigle: e.sigle ?? '',
      niu: e.niu ?? '',
      regime_fiscal: e.regime_fiscal,
      mode_gestion: e.mode_gestion,
      pays: e.pays,
      devise_principale: e.devise_principale,
      ville: e.ville ?? '',
      region: e.region ?? '',
      adresse: '',
      telephone: '',
      email: '',
      actif: e.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

watch(
  () => [visible.value, props.entrepriseId] as const,
  ([open, id]) => {
    if (open && id) loadEntreprise()
    if (open && !id) {
      form.value = {
        code: '',
        raison_sociale: '',
        sigle: '',
        niu: '',
        regime_fiscal: 'reel_simplifie',
        mode_gestion: 'standard',
        pays: 'CM',
        devise_principale: 'XAF',
        ville: '',
        region: '',
        adresse: '',
        telephone: '',
        email: '',
        actif: true,
      }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return

  const confirmResult = await Swal.fire({
    title: 'Êtes vous sûres?',
    text: isEdit.value
      ? 'Les modifications apportées à l\'entreprise seront enregistrées.'
      : `L'entreprise « ${String(form.value.raison_sociale).trim()} » sera créée.`,
    showCancelButton: true,
    confirmButtonText: isEdit.value ? 'Modifier' : 'Enregistrer',
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
    if (isEdit.value && props.entrepriseId) {
      const body: EntrepriseUpdate = {
        raison_sociale: String(form.value.raison_sociale),
        sigle: form.value.sigle ? String(form.value.sigle) : null,
        niu: form.value.niu ? String(form.value.niu) : null,
        regime_fiscal: form.value.regime_fiscal as EntrepriseUpdate['regime_fiscal'],
        mode_gestion: form.value.mode_gestion as EntrepriseUpdate['mode_gestion'],
        pays: form.value.pays ? String(form.value.pays) : null,
        devise_principale: form.value.devise_principale ? String(form.value.devise_principale) : null,
        ville: form.value.ville ? String(form.value.ville) : null,
        region: form.value.region ? String(form.value.region) : null,
        actif: form.value.actif as boolean,
      }
      await updateEntreprise(props.entrepriseId, body)
      toastStore.success('Entreprise mise à jour.')
    } else {
      const body: EntrepriseCreate = {
        code: String(form.value.code).trim(),
        raison_sociale: String(form.value.raison_sociale).trim(),
        sigle: form.value.sigle ? String(form.value.sigle).trim() : null,
        niu: form.value.niu ? String(form.value.niu).trim() : null,
        regime_fiscal: form.value.regime_fiscal as RegimeFiscal,
        mode_gestion: form.value.mode_gestion as ModeGestion,
        pays: form.value.pays ? String(form.value.pays) : undefined,
        devise_principale: form.value.devise_principale ? String(form.value.devise_principale) : undefined,
        ville: form.value.ville ? String(form.value.ville).trim() : null,
        region: form.value.region ? String(form.value.region).trim() : null,
        actif: form.value.actif as boolean,
      }
      await createEntreprise(body)
      toastStore.success('Entreprise créée.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de l\'enregistrement.')
  } finally {
    saving.value = false
  }
}

function onClose() {
  emit('cancel')
}
</script>

<template>
  <VDialog
    :model-value="visible"
    max-width="800"
    persistent
    content-class="entreprise-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="entreprise-modal-card overflow-hidden">
      <!-- Header avec icône et titre -->
      <div class="entreprise-modal-header">
        <div class="entreprise-modal-header-content">
          <div class="entreprise-modal-icon-wrap">
            <VIcon icon="ri-building-4-line" size="28" />
          </div>
          <div class="entreprise-modal-title-wrap">
            <h2 class="entreprise-modal-title">{{ modalTitle }}</h2>
            <p class="entreprise-modal-subtitle">
              {{ isEdit ? 'Modifier les informations de l\'entreprise' : 'Renseignez les informations de la nouvelle entreprise' }}
            </p>
          </div>
        </div>
        <VBtn
          icon
          variant="text"
          size="small"
          class="entreprise-modal-close"
          @click="onClose"
        >
          <VIcon icon="ri-close-line" size="22" />
        </VBtn>
      </div>

      <!-- Overlay chargement -->
      <div v-if="loading" class="entreprise-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="entreprise-modal-body">
        <VForm
          ref="formRef"
          @submit.prevent="onSubmit"
        >
          <!-- Section Identification -->
          <div class="entreprise-modal-section">
            <VRow dense class="mt-4">
              <VCol cols="12" sm="8">
                <VTextField
                  v-model="form.raison_sociale"
                  label="Raison sociale"
                  :rules="rules.raison_sociale"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-building-2-line"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VTextField
                  v-model="form.code"
                  label="Code"
                  :rules="rules.code"
                  :readonly="isEdit"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-barcode-line"
                />
              </VCol>
            </VRow>
            <VRow dense class="mt-4">
              <VCol cols="12" sm="8">
                <VTextField
                  v-model="form.sigle"
                  label="Sigle"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  placeholder="Ex. GES"
                  prepend-inner-icon="ri-text"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VTextField
                  v-model="form.niu"
                  label="NIU"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  placeholder="Numéro d'identification unique"
                  prepend-inner-icon="ri-id-card-line"
                />
              </VCol>
            </VRow>

            <VRow dense class="mt-4">
              <VCol cols="12" sm="4">
                <VSelect
                  v-model="form.regime_fiscal"
                  label="Régime fiscal"
                  :items="regimeOptions"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-file-list-3-line"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VSelect
                  v-model="form.mode_gestion"
                  label="Mode de gestion"
                  :items="modeOptions"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-dashboard-line"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VAutocomplete
                  v-model="form.pays"
                  label="Pays"
                  :items="countryOptions"
                  item-title="title"
                  item-value="code"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  placeholder="Rechercher un pays..."
                  prepend-inner-icon="ri-global-line"
                  clearable
                />
              </VCol>
            </VRow>
            <VRow dense class="mt-4">
              <VCol cols="12" sm="4">
                <VTextField
                  v-model="form.devise_principale"
                  label="Devise principale"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  placeholder="Ex. XAF"
                  prepend-inner-icon="ri-money-dollar-circle-line"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VTextField
                  v-model="form.ville"
                  label="Ville"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-map-pin-line"
                />
              </VCol>
              <VCol cols="12" sm="4">
                <VTextField
                  v-model="form.region"
                  label="Région"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="entreprise-field"
                  prepend-inner-icon="ri-map-2-line"
                />
              </VCol>
            </VRow>
          </div>

          </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="entreprise-modal-actions">
        <VBtn
          variant="outlined"
          color="error"
          :disabled="saving"
          @click="onClose"
        >
          Annuler
        </VBtn>
        <VBtn
          color="primary"
          variant="outlined"
          :loading="saving"
          :disabled="loading"
          @click="onSubmit"
        >
          {{ isEdit ? 'Modifier' : 'Enregistrer' }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.entreprise-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.entreprise-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

/* Header */
.entreprise-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
  position: relative;
}

.entreprise-modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 24px;
  pointer-events: none;
}

.entreprise-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.entreprise-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.entreprise-modal-title-wrap {
  min-width: 0;
}

.entreprise-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.entreprise-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.entreprise-modal-close {
  color: rgba(0, 0, 0, 0.9) !important;
  flex-shrink: 0;
}

.entreprise-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: rgb(0, 0, 0) !important;
}

/* Loading overlay */
.entreprise-modal-loading {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
  border-radius: 0 0 16px 16px;
}

/* Body */
.entreprise-modal-body {
  padding: 24px 24px 20px;
  max-height: min(70vh, 520px);
  overflow-y: auto;
}

.entreprise-modal-section {
  margin-bottom: 24px;
}

.entreprise-modal-section:last-of-type {
  margin-bottom: 0;
}

.entreprise-modal-section-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.entreprise-field :deep(.v-field) {
  border-radius: 10px;
  color: rgb(0, 0, 0);
}

/* Actions */
.entreprise-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
