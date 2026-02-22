<script setup lang="ts">
import { getCanalVente, createCanalVente, updateCanalVente } from '@/api/catalogue'
import type { CanalVenteCreate, CanalVenteUpdate } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ entrepriseId: number; canalId: number | null }>()
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
  ordre: 0,
  actif: true,
})

const rules = {
  code: [required(), maxLength(30, 'Max. 30 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.canalId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le canal de vente' : 'Nouveau canal de vente'))

async function load() {
  if (!props.canalId) return
  loading.value = true
  try {
    const c = await getCanalVente(props.canalId)
    form.value = { code: c.code, libelle: c.libelle, ordre: c.ordre, actif: c.actif }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.canalId] as const, ([open, id]) => {
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '', ordre: 0, actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer le canal « ${form.value.code.trim() } » ?`,
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
    if (isEdit.value && props.canalId) {
      await updateCanalVente(props.canalId, { code: form.value.code.trim(), libelle: form.value.libelle.trim(), ordre: form.value.ordre, actif: form.value.actif } as CanalVenteUpdate)
      toastStore.success('Canal mis à jour.')
    } else {
      await createCanalVente({ entreprise_id: props.entrepriseId, code: form.value.code.trim(), libelle: form.value.libelle.trim(), ordre: form.value.ordre, actif: form.value.actif } as CanalVenteCreate)
      toastStore.success('Canal créé.')
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
  <VDialog :model-value="visible" max-width="560" persistent content-class="catalogue-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="catalogue-modal-card overflow-hidden">
      <div class="catalogue-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="catalogue-modal-icon"><VIcon icon="ri-store-3-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">Code, libellé et ordre d'affichage</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="catalogue-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="catalogue-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model.number="form.ordre" label="Ordre" type="number" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6" class="d-flex align-center">
              <VSwitch v-model="form.actif" label="Actif" color="primary" hide-details />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4 gap-2">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onClose">Annuler</VBtn>
        <VBtn color="primary" variant="flat" :loading="saving" @click="onSubmit">Enregistrer</VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.catalogue-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.catalogue-modal-card { border-radius: 16px; overflow: hidden; }
.catalogue-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.catalogue-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.catalogue-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.catalogue-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.catalogue-modal-close { flex-shrink: 0; }
.catalogue-modal-body { padding: 0 24px 16px; }
</style>
