<script setup lang="ts">
import { getDevise, createDevise, updateDevise } from '@/api/parametrage'
import type { DeviseCreate, DeviseUpdate } from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  deviseId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({
  code: '',
  libelle: '',
  symbole: '',
  decimales: 2,
  actif: true,
})

const rules = {
  code: [required(), maxLength(10, 'Max. 10 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.deviseId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la devise' : 'Nouvelle devise'))

async function loadDevise() {
  if (!props.deviseId) return
  loading.value = true
  try {
    const d = await getDevise(props.deviseId)
    form.value = {
      code: d.code,
      libelle: d.libelle,
      symbole: d.symbole ?? '',
      decimales: d.decimales,
      actif: d.actif,
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
  () => [visible.value, props.deviseId] as const,
  ([open, id]) => {
    if (open && id) loadDevise()
    if (open && !id) {
      form.value = { code: '', libelle: '', symbole: '', decimales: 2, actif: true }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return

  // Éviter "Blocked aria-hidden": retirer le focus du bouton/modal avant d'ouvrir une 2e overlay (Swal)
  const activeEl = document.activeElement as HTMLElement | null
  if (activeEl?.focus != null) activeEl.blur()

  const confirmResult = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: isEdit.value
      ? `Les modifications faites sur cette la devise <br> <b>« ${String(form.value.code).trim()} - ${String(form.value.libelle).trim()} »</b> seront enregistrées.`
      : `La devise « ${String(form.value.code).trim()} - ${String(form.value.libelle).trim()} » sera créée.`,
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
    if (isEdit.value && props.deviseId) {
      await updateDevise(props.deviseId, {
        libelle: form.value.libelle,
        symbole: form.value.symbole || null,
        decimales: form.value.decimales,
        actif: form.value.actif,
      })
      toastStore.success('Devise mise à jour.')
    } else {
      await createDevise({
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        symbole: form.value.symbole?.trim() || null,
        decimales: form.value.decimales,
        actif: form.value.actif,
      })
      toastStore.success('Devise créée.')
    }
    try {
      emit('saved')
    } catch (err) {
      toastStore.error(getApiErrorMessage(err) ?? 'Erreur après enregistrement.')
    }
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
    content-class="devise-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="devise-modal-card overflow-hidden">
      <!-- Header -->
      <div class="devise-modal-header">
        <div class="devise-modal-header-content">
          <div class="devise-modal-icon-wrap">
            <VIcon icon="ri-money-dollar-circle-line" size="50" />
          </div>
          <div class="devise-modal-title-wrap">
            <h2 class="devise-modal-title">{{ modalTitle }}</h2>
            <p class="devise-modal-subtitle">
              {{ isEdit ? 'Modifier les informations de la devise' : 'Renseignez les informations de la nouvelle devise (code ISO 4217)' }}
            </p>
          </div>
        </div>
        <VBtn
          icon
          variant="text"
          size="small"
          class="devise-modal-close"
          @click="onClose"
        >
          <VIcon icon="ri-close-line" size="22" color="secondary"/>
        </VBtn>
      </div>

      <div v-if="loading" class="devise-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="devise-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <div class="devise-modal-section">
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
                  class="devise-field"
                  prepend-inner-icon="ri-barcode-line"
                  placeholder="Ex. XAF, EUR"
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
                  class="devise-field"
                  prepend-inner-icon="ri-text"
                  placeholder="Ex. Franc CFA"
                />
              </VCol>
            </VRow>
            <VRow dense class="mt-4">
              <VCol cols="12" sm="6">
                <VTextField
                  v-model="form.symbole"
                  label="Symbole"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="devise-field"
                  prepend-inner-icon="ri-currency-line"
                  placeholder="Ex. F, €, $"
                />
              </VCol>
              <VCol cols="12" sm="6">
                <VTextField
                  v-model.number="form.decimales"
                  label="Décimales"
                  type="number"
                  min="0"
                  max="6"
                  variant="outlined"
                  density="compact"
                  hide-details="auto"
                  class="devise-field"
                  prepend-inner-icon="ri-number-0"
                />
              </VCol>
            </VRow>
          </div>

          <div class="devise-modal-section">
            <div class="devise-status-switch">
              <VSwitch
                v-model="form.actif"
                label="Devise active"
                color="secondary"
                hide-details
                density="compact"
                class="mt-0"
              />
              <p class="text-caption text-medium-emphasis mt-1 mb-0">
                Une devise inactive n'apparaîtra pas dans les sélecteurs.
              </p>
            </div>
          </div>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="devise-modal-actions">
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
.devise-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.devise-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.devise-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
  position: relative;
}

.devise-modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 24px;
  pointer-events: none;
}

.devise-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.devise-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.devise-modal-title-wrap {
  min-width: 0;
}

.devise-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.devise-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.devise-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.devise-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.devise-modal-loading {
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

.devise-modal-body {
  padding: 24px 24px 20px;
  max-height: min(70vh, 420px);
  overflow-y: auto;
}

.devise-modal-section {
  margin-bottom: 24px;
}

.devise-modal-section:last-of-type {
  margin-bottom: 0;
}

.devise-modal-section-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.devise-status-switch {
  padding: 12px 16px;
  background: rgba(var(--v-theme-primary), 0.06);
  border-radius: 12px;
  border: 1px solid rgba(var(--v-theme-primary), 0.12);
}

.devise-field :deep(.v-field) {
  border-radius: 10px;
}

.devise-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
