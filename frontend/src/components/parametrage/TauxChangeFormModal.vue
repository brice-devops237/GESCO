<script setup lang="ts">
import {
  listDevises,
  getTauxChange,
  createTauxChange,
  updateTauxChange,
} from '@/api/parametrage'
import type { TauxChangeCreate } from '@/api/types/parametrage'
import type { DeviseResponse } from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  tauxId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required } = useFormValidation()

const devises = ref<DeviseResponse[]>([])
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({
  devise_from_id: null as number | null,
  devise_to_id: null as number | null,
  taux: '',
  date_effet: '',
  source: '',
})

const rules = {
  devise_from_id: [required()],
  devise_to_id: [required()],
  taux: [required()],
  date_effet: [required()],
}

const isEdit = computed(() => props.tauxId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le taux de change' : 'Nouveau taux de change'))

const deviseOptions = computed(() =>
  devises.value.map(d => ({ title: `${d.code} - ${d.libelle}`, value: d.id })),
)

const deviseLabel = (id: number) => {
  const d = devises.value.find(x => x.id === id)
  return d ? `${d.code} - ${d.libelle}` : String(id)
}

async function loadDevises() {
  loading.value = true
  try {
    devises.value = (await listDevises({ limit: 100 })).items ?? []
  } finally {
    loading.value = false
  }
}

async function loadTaux() {
  if (!props.tauxId) return
  loading.value = true
  try {
    const t = await getTauxChange(props.tauxId)
    form.value = {
      devise_from_id: t.devise_from_id,
      devise_to_id: t.devise_to_id,
      taux: String(t.taux),
      date_effet: t.date_effet,
      source: t.source ?? '',
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
  () => [visible.value, props.tauxId] as const,
  async ([open, id]) => {
    if (!open) return
    await loadDevises()
    if (id) {
      await loadTaux()
    } else {
      const today = new Date().toISOString().slice(0, 10)
      form.value = {
        devise_from_id: null,
        devise_to_id: null,
        taux: '',
        date_effet: today,
        source: '',
      }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  if (form.value.devise_from_id == null || form.value.devise_to_id == null) {
    toastStore.error('Sélectionnez les deux devises.')
    return
  }
  if (form.value.devise_from_id === form.value.devise_to_id) {
    toastStore.error('Les devises source et cible doivent être différentes.')
    return
  }
  const tauxNum = Number(form.value.taux)
  if (!Number.isFinite(tauxNum) || tauxNum <= 0) {
    toastStore.error('Le taux doit être un nombre strictement positif.')
    return
  }

  const confirmResult = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: isEdit.value
      ? 'Enregistrer les modifications sur ce taux de change ?'
      : `Créer le taux de change ${deviseLabel(form.value.devise_from_id)} → ${deviseLabel(form.value.devise_to_id)} au ${form.value.date_effet} ?`,
    showCancelButton: true,
    confirmButtonText: isEdit.value ? 'Modifier' : 'Créer',
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
    if (isEdit.value && props.tauxId) {
      await updateTauxChange(props.tauxId, {
        taux: tauxNum,
        source: form.value.source?.trim() || null,
      })
      toastStore.success('Taux de change mis à jour.')
    } else {
      const body: TauxChangeCreate = {
        devise_from_id: form.value.devise_from_id,
        devise_to_id: form.value.devise_to_id,
        taux: tauxNum,
        date_effet: form.value.date_effet,
        source: form.value.source?.trim() || null,
      }
      await createTauxChange(body)
      toastStore.success('Taux de change créé.')
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
    max-width="700"
    persistent
    content-class="taux-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="taux-modal-card overflow-hidden">
      <div class="taux-modal-header">
        <div class="taux-modal-header-content">
          <div class="taux-modal-icon-wrap">
            <VIcon icon="ri-exchange-line" size="50" />
          </div>
          <div class="taux-modal-title-wrap">
            <h2 class="taux-modal-title">{{ modalTitle }}</h2>
            <p class="taux-modal-subtitle">
              {{ isEdit ? 'Modifier le taux et la source (devises et date non modifiables)' : 'Définir un taux de change entre deux devises à une date d\'effet' }}
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="taux-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary"/>
        </VBtn>
      </div>

      <div v-if="loading" class="taux-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="taux-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.devise_from_id"
                label="Devise source"
                :items="deviseOptions"
                item-title="title"
                item-value="value"
                :rules="rules.devise_from_id"
                :readonly="isEdit"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="taux-field"
                prepend-inner-icon="ri-arrow-right-down-line"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.devise_to_id"
                label="Devise cible"
                :items="deviseOptions"
                item-title="title"
                item-value="value"
                :rules="rules.devise_to_id"
                :readonly="isEdit"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="taux-field"
                prepend-inner-icon="ri-arrow-right-up-line"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.taux"
                label="Taux"
                :rules="rules.taux"
                type="number"
                step="any"
                min="0"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="taux-field"
                prepend-inner-icon="ri-percent-line"
                placeholder="Ex. 655.957"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.date_effet"
                label="Date d'effet"
                :rules="rules.date_effet"
                type="date"
                :readonly="isEdit"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="taux-field"
                prepend-inner-icon="ri-calendar-line"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12">
              <VTextField
                v-model="form.source"
                label="Source (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="taux-field"
                prepend-inner-icon="ri-link"
                placeholder="Ex. BCEAC, manuel, api"
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="taux-modal-actions">
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
.taux-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.taux-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.taux-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
  position: relative;
}

.taux-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.taux-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.taux-modal-title-wrap {
  min-width: 0;
}

.taux-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.taux-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.taux-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.taux-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.taux-modal-loading {
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

.taux-modal-body {
  padding: 24px 24px 20px;
  max-height: min(70vh, 420px);
  overflow-y: auto;
}

.taux-field :deep(.v-field) {
  border-radius: 10px;
}

.taux-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
