<script setup lang="ts">
import { getPointVente, createPointVente, updatePointVente } from '@/api/parametrage'
import type {
  PointDeVenteCreate,
  PointDeVenteUpdate,
  TypePointDeVente,
} from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  entrepriseId: number
  pointVenteId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const typeOptions: { title: string; value: TypePointDeVente }[] = [
  { title: 'Principal', value: 'principal' },
  { title: 'Secondaire', value: 'secondaire' },
  { title: 'Dépôt', value: 'depot' },
]

/** Liste des fuseaux horaires IANA (monde entier), triée par ordre alphabétique. */
const timezoneOptions = computed(() => {
  try {
    if (typeof Intl !== 'undefined' && 'supportedValuesOf' in Intl) {
      const zones = (Intl as { supportedValuesOf?(key: 'timeZone'): string[] }).supportedValuesOf?.('timeZone')
      return [...(zones ?? [])].sort((a, b) => a.localeCompare(b))
    }
  } catch {
    // Fallback si supportedValuesOf non disponible (très anciens navigateurs)
  }
  return [
    'Africa/Douala',
    'Africa/Yaounde',
    'Europe/Paris',
    'America/New_York',
    'UTC',
  ]
})

const form = ref({
  code: '',
  libelle: '',
  type: 'principal' as TypePointDeVente,
  adresse: '',
  code_postal: '',
  ville: '',
  telephone: '',
  fuseau_horaire: '',
  latitude: '' as string | number,
  longitude: '' as string | number,
  est_depot: false,
  actif: true,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(100, 'Max. 100 caractères')],
}

const isEdit = computed(() => props.pointVenteId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le point de vente' : 'Nouveau point de vente'))

function toNum(val: string | number): number | null {
  if (val === '' || val === null || val === undefined) return null
  const n = Number(val)
  return Number.isFinite(n) ? n : null
}

async function loadPointVente() {
  if (!props.pointVenteId) return
  loading.value = true
  try {
    const p = await getPointVente(props.pointVenteId)
    form.value = {
      code: p.code,
      libelle: p.libelle,
      type: p.type as TypePointDeVente,
      adresse: p.adresse ?? '',
      code_postal: p.code_postal ?? '',
      ville: p.ville ?? '',
      telephone: p.telephone ?? '',
      fuseau_horaire: p.fuseau_horaire ?? '',
      latitude: p.latitude != null ? Number(p.latitude) : '',
      longitude: p.longitude != null ? Number(p.longitude) : '',
      est_depot: p.est_depot,
      actif: p.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() {
  emit('cancel')
}

watch(
  () => [visible.value, props.pointVenteId] as const,
  ([open, id]) => {
    if (open && id) loadPointVente()
    if (open && !id) {
      form.value = {
        code: '',
        libelle: '',
        type: 'principal',
        adresse: '',
        code_postal: '',
        ville: '',
        telephone: '',
        fuseau_horaire: '',
        latitude: '',
        longitude: '',
        est_depot: false,
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
    html: isEdit.value
      ? `Enregistrer les modifications sur le point de vente <strong>« ${form.value.code} - ${form.value.libelle} »</strong> ?`
      : `Créer le point de vente « ${form.value.code.trim()} - ${form.value.libelle.trim()} » ?`,
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
    const lat = toNum(form.value.latitude)
    const lng = toNum(form.value.longitude)
    if (isEdit.value && props.pointVenteId) {
      const body: PointDeVenteUpdate = {
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        type: form.value.type,
        adresse: form.value.adresse?.trim() || null,
        code_postal: form.value.code_postal?.trim() || null,
        ville: form.value.ville?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        fuseau_horaire: form.value.fuseau_horaire?.trim() || null,
        latitude: lat,
        longitude: lng,
        est_depot: form.value.est_depot,
        actif: form.value.actif,
      }
      await updatePointVente(props.pointVenteId, body)
      toastStore.success('Point de vente mis à jour.')
    } else {
      const body: PointDeVenteCreate = {
        entreprise_id: props.entrepriseId,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        type: form.value.type,
        adresse: form.value.adresse?.trim() || null,
        code_postal: form.value.code_postal?.trim() || null,
        ville: form.value.ville?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        fuseau_horaire: form.value.fuseau_horaire?.trim() || null,
        latitude: lat ?? undefined,
        longitude: lng ?? undefined,
        est_depot: form.value.est_depot,
        actif: form.value.actif,
      }
      await createPointVente(body)
      toastStore.success('Point de vente créé.')
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
  <VDialog
    :model-value="visible"
    max-width="800"
    persistent
    content-class="pdv-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="pdv-modal-card overflow-hidden">
      <div class="pdv-modal-header">
        <div class="pdv-modal-header-content">
          <div class="pdv-modal-icon-wrap">
            <VIcon icon="ri-store-2-line" size="50" />
          </div>
          <div class="pdv-modal-title-wrap">
            <h2 class="pdv-modal-title">{{ modalTitle }}</h2>
            <p class="pdv-modal-subtitle">
              {{ isEdit ? 'Modifier les informations du point de vente ou dépôt' : 'Magasin, agence ou dépôt rattaché à l\'entreprise' }}
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="pdv-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <div v-if="loading" class="pdv-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="pdv-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.code"
                label="Code"
                :rules="rules.code"
                :readonly="isEdit"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-barcode-line"
                placeholder="Ex. PDV01"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.libelle"
                label="Libellé"
                :rules="rules.libelle"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-text"
                placeholder="Ex. Siège, Agence Centre"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.type"
                label="Type"
                :items="typeOptions"
                item-title="title"
                item-value="value"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-store-line"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.ville"
                label="Ville"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-map-pin-line"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12">
              <VTextField
                v-model="form.adresse"
                label="Adresse"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-road-map-line"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.code_postal"
                label="Code postal"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-mail-send-line"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.telephone"
                label="Téléphone"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-phone-line"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VAutocomplete
                v-model="form.fuseau_horaire"
                label="Fuseau horaire (optionnel)"
                :items="timezoneOptions"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                prepend-inner-icon="ri-time-line"
                placeholder="Ex. Africa/Douala"
                clearable
                auto-select-first
              />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField
                v-model="form.latitude"
                label="Latitude"
                type="number"
                step="any"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                placeholder="-90 à 90"
              />
            </VCol>
            <VCol cols="12" sm="3">
              <VTextField
                v-model="form.longitude"
                label="Longitude"
                type="number"
                step="any"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="pdv-field"
                placeholder="-180 à 180"
              />
            </VCol>
          </VRow>
          <div class="pdv-modal-section mt-4">
            <div class="pdv-switches">
              <VRow dense>
                <VCol cols="12" sm="6">
                  <VSwitch
                    v-model="form.est_depot"
                    label="Est un dépôt (entrepôt)"
                    color="secondary"
                    hide-details
                    density="compact"
                    class="mt-0"
                  />
                </VCol>
                <VCol cols="12" sm="6">
                  <VSwitch
                    v-model="form.actif"
                    label="Point de vente actif"
                    color="secondary"
                    hide-details
                    density="compact"
                    class="mt-0"
                  />
                </VCol>
              </VRow>
            </div>
            <p class="text-caption text-medium-emphasis mt-3 ml-2 mb-0">
              Un point de vente inactif n'apparaîtra pas dans les sélecteurs.
            </p>
          </div>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="pdv-modal-actions">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onClose">
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
.pdv-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.pdv-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.pdv-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
  position: relative;
}

.pdv-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.pdv-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdv-modal-title-wrap {
  min-width: 0;
}

.pdv-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.pdv-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.pdv-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.pdv-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.pdv-modal-loading {
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

.pdv-modal-body {
  padding: 24px 24px 20px;
  max-height: min(75vh, 520px);
  overflow-y: auto;
}

.pdv-modal-section {
  margin-bottom: 0;
}

.pdv-switches {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 12px 16px;
  background: rgba(var(--v-theme-primary), 0.06);
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
}

.pdv-field :deep(.v-field) {
  border-radius: 10px;
}

.pdv-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
