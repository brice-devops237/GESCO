<script setup lang="ts">
import { getRole, createRole, updateRole } from '@/api/parametrage'
import type { RoleCreate, RoleUpdate } from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  entrepriseId: number
  roleId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({ code: '', libelle: '' })

const rules = {
  code: [required(), maxLength(50, 'Max. 50 caractères')],
  libelle: [required(), maxLength(100, 'Max. 100 caractères')],
}

const isEdit = computed(() => props.roleId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le rôle' : 'Nouveau rôle'))

async function loadRole() {
  if (!props.roleId) return
  loading.value = true
  try {
    const r = await getRole(props.roleId)
    form.value = { code: r.code, libelle: r.libelle }
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
  () => [visible.value, props.roleId] as const,
  ([open, id]) => {
    if (open && id) loadRole()
    if (open && !id) form.value = { code: '', libelle: '' }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return

  const confirmResult = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value
      ? `Enregistrer les modifications sur le rôle <br><strong>« ${form.value.code} - ${form.value.libelle} »</strong> ?`
      : `Créer le rôle « ${form.value.code.trim()} - ${form.value.libelle.trim()} » ?`,
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
    if (isEdit.value && props.roleId) {
      await updateRole(props.roleId, {
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
      })
      toastStore.success('Rôle mis à jour.')
    } else {
      const body: RoleCreate = {
        entreprise_id: props.entrepriseId || null,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
      }
      await createRole(body)
      toastStore.success('Rôle créé.')
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
    max-width="520"
    persistent
    content-class="role-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="role-modal-card overflow-hidden">
      <div class="role-modal-header">
        <div class="role-modal-header-content">
          <div class="role-modal-icon-wrap">
            <VIcon icon="ri-user-shared-line" size="50" />
          </div>
          <div class="role-modal-title-wrap">
            <h2 class="role-modal-title">{{ modalTitle }}</h2>
            <p class="role-modal-subtitle">
              {{ isEdit ? 'Modifier le code et le libellé du rôle' : 'Rôle entreprise ou rôle système (sans entreprise)' }}
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="role-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <div v-if="loading" class="role-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="role-modal-body">
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
                class="role-field"
                prepend-inner-icon="ri-barcode-line"
                placeholder="Ex. MANAGER"
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
                class="role-field"
                prepend-inner-icon="ri-text"
                placeholder="Ex. Gestionnaire"
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="role-modal-actions">
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
.role-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.role-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.role-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
}

.role-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.role-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-modal-title-wrap {
  min-width: 0;
}

.role-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.role-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.role-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.role-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.role-modal-loading {
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

.role-modal-body {
  padding: 24px 24px 20px;
}

.role-field :deep(.v-field) {
  border-radius: 10px;
}

.role-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
