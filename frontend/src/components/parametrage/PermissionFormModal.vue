<script setup lang="ts">
import { createPermission } from '@/api/parametrage'
import type { PermissionCreate } from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({ module: '', action: '', libelle: '' })

const rules = {
  module: [required(), maxLength(50, 'Max. 50 caractères')],
  action: [required(), maxLength(50, 'Max. 50 caractères')],
  libelle: [required(), maxLength(150, 'Max. 150 caractères')],
}

watch(visible, open => {
  if (open) form.value = { module: '', action: '', libelle: '' }
})

function onClose() {
  emit('cancel')
}

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return

  const confirmResult = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: `Créer la permission <strong>${form.value.module}.${form.value.action}</strong> (${form.value.libelle}) ?`,
    showCancelButton: true,
    confirmButtonText: 'Créer',
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
    const body: PermissionCreate = {
      module: form.value.module.trim(),
      action: form.value.action.trim(),
      libelle: form.value.libelle.trim(),
    }
    await createPermission(body)
    toastStore.success('Permission créée.')
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
    max-width="560"
    persistent
    content-class="permission-modal-dialog"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="permission-modal-card overflow-hidden">
      <div class="permission-modal-header">
        <div class="permission-modal-header-content">
          <div class="permission-modal-icon-wrap">
            <VIcon icon="ri-lock-2-line" size="28" />
          </div>
          <div class="permission-modal-title-wrap">
            <h2 class="permission-modal-title">Nouvelle permission</h2>
            <p class="permission-modal-subtitle">
              Module et action (ex. parametrage.read, parametrage.write) et libellé pour l’affichage.
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="permission-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" />
        </VBtn>
      </div>

      <VCardText class="permission-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense class="mt-4">
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.module"
                label="Module"
                :rules="rules.module"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="permission-field"
                prepend-inner-icon="ri-folder-line"
                placeholder="Ex. parametrage"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.action"
                label="Action"
                :rules="rules.action"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="permission-field"
                prepend-inner-icon="ri-checkbox-circle-line"
                placeholder="Ex. read, write"
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12">
              <VTextField
                v-model="form.libelle"
                label="Libellé"
                :rules="rules.libelle"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="permission-field"
                prepend-inner-icon="ri-text"
                placeholder="Ex. Lire le paramétrage"
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="permission-modal-actions">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onClose">
          Annuler
        </VBtn>
        <VBtn
          color="primary"
          variant="outlined"
          :loading="saving"
          @click="onSubmit"
        >
          Créer
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.permission-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.permission-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
}

.permission-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
}

.permission-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.permission-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.permission-modal-title-wrap {
  min-width: 0;
}

.permission-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.permission-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.permission-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.permission-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.permission-modal-body {
  padding: 24px 24px 20px;
}

.permission-field :deep(.v-field) {
  border-radius: 10px;
}

.permission-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
