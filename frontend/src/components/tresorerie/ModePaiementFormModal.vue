<script setup lang="ts">
import { getModePaiement, createModePaiement, updateModePaiement } from '@/api/tresorerie'
import type { ModePaiementCreate, ModePaiementUpdate } from '@/api/types/tresorerie'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  modePaiementId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({
  code: '',
  libelle: '',
  code_operateur: '' as string | null,
  actif: true,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.modePaiementId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le mode de paiement' : 'Nouveau mode de paiement'))

async function loadModePaiement() {
  if (!props.modePaiementId) return
  loading.value = true
  try {
    const d = await getModePaiement(props.modePaiementId)
    form.value = {
      code: d.code,
      libelle: d.libelle,
      code_operateur: d.code_operateur ?? '',
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
  () => [visible.value, props.modePaiementId] as const,
  ([open, id]) => {
    if (open && id) loadModePaiement()
    if (open && !id) {
      form.value = { code: '', libelle: '', code_operateur: '', actif: true }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = (await formRef.value?.validate().then(r => r.valid)) ?? false
  if (!valid) return

  const confirmResult = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value
      ? `Enregistrer les modifications sur le mode de paiement <b>« ${String(form.value.code).trim()} »</b> ?`
      : `Créer le mode de paiement « ${String(form.value.code).trim()} - ${String(form.value.libelle).trim()} » ?`,
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

  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) {
    toastStore.error('Entreprise non définie.')
    return
  }

  saving.value = true
  try {
    if (isEdit.value && props.modePaiementId) {
      const body: ModePaiementUpdate = {
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        code_operateur: form.value.code_operateur?.trim() || null,
        actif: form.value.actif,
      }
      await updateModePaiement(props.modePaiementId, body)
      toastStore.success('Mode de paiement mis à jour.')
    } else {
      const body: ModePaiementCreate = {
        entreprise_id: entrepriseId,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        code_operateur: form.value.code_operateur?.trim() || null,
        actif: form.value.actif,
      }
      await createModePaiement(body)
      toastStore.success('Mode de paiement créé.')
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
    max-width="600"
    persistent
    content-class="mode-paiement-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="mode-paiement-modal-card overflow-hidden">
      <div class="d-flex align-center justify-space-between pa-4 pb-2">
        <h2 class="text-h6">{{ modalTitle }}</h2>
        <VBtn icon variant="text" size="small" @click="onClose">
          <VIcon icon="ri-close-line" />
        </VBtn>
      </div>
      <div v-if="loading" class="d-flex flex-column align-center justify-center pa-8">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>
      <VCardText v-else class="pt-0">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.code"
                label="Code"
                :rules="rules.code"
                :readonly="isEdit"
                variant="outlined"
                density="compact"
                hide-details="auto"
                prepend-inner-icon="ri-barcode-line"
                placeholder="Ex. VIREMENT, CB"
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
                prepend-inner-icon="ri-text"
                placeholder="Ex. Virement bancaire"
              />
            </VCol>
            <VCol cols="12">
              <VTextField
                v-model="form.code_operateur"
                label="Code opérateur (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
                placeholder="Code externe"
              />
            </VCol>
            <VCol cols="12">
              <VSwitch
                v-model="form.actif"
                label="Mode de paiement actif"
                color="primary"
                hide-details
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
        <VBtn color="primary" :loading="saving" :disabled="loading" @click="onSubmit">
          {{ isEdit ? 'Modifier' : 'Enregistrer' }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.mode-paiement-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}
.mode-paiement-modal-card {
  border-radius: 12px;
}
</style>
