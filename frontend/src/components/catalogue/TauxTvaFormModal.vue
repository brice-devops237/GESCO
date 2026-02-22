<script setup lang="ts">
import { getTauxTva, createTauxTva, updateTauxTva } from '@/api/catalogue'
import type { TauxTvaCreate, TauxTvaUpdate, NatureTva } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ tauxId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const natureOptions: { title: string; value: NatureTva }[] = [
  { title: 'Normal', value: 'normal' },
  { title: 'Réduit', value: 'reduit' },
  { title: 'Exonéré', value: 'exonere' },
]

const form = ref({
  code: '',
  taux: '' as number | string,
  libelle: '',
  nature: 'normal' as NatureTva,
  actif: true,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
  taux: [required(), (v: string) => !isNaN(Number(v)) && Number(v) >= 0 && Number(v) <= 100 || 'Taux entre 0 et 100'],
}

const isEdit = computed(() => props.tauxId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le taux TVA' : 'Nouveau taux TVA'))

async function load() {
  if (!props.tauxId) return
  loading.value = true
  try {
    const t = await getTauxTva(props.tauxId)
    form.value = {
      code: t.code,
      taux: t.taux,
      libelle: t.libelle,
      nature: (t.nature as NatureTva) || 'normal',
      actif: t.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.tauxId] as const, ([open, id]) => {
  if (open && id) load()
  if (open && !id) form.value = { code: '', taux: '', libelle: '', nature: 'normal', actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer le taux TVA « ${form.value.code.trim() } » ?`,
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
    const tauxNum = Number(form.value.taux)
    if (isEdit.value && props.tauxId) {
      await updateTauxTva(props.tauxId, {
        taux: isNaN(tauxNum) ? form.value.taux : tauxNum,
        libelle: form.value.libelle.trim(),
        nature: form.value.nature,
        actif: form.value.actif,
      } as TauxTvaUpdate)
      toastStore.success('Taux TVA mis à jour.')
    } else {
      await createTauxTva({
        code: form.value.code.trim(),
        taux: isNaN(tauxNum) ? form.value.taux : tauxNum,
        libelle: form.value.libelle.trim(),
        nature: form.value.nature,
        actif: form.value.actif,
      } as TauxTvaCreate)
      toastStore.success('Taux TVA créé.')
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
          <div class="catalogue-modal-icon"><VIcon icon="ri-percent-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">{{ isEdit ? 'Modifier le taux' : 'Code, taux (%) et libellé' }}</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="catalogue-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="catalogue-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" prepend-inner-icon="ri-barcode-line" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.taux" label="Taux %" :rules="rules.taux" type="number" step="0.01" variant="outlined" density="compact" hide-details="auto" suffix="%" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.nature" :items="natureOptions" item-title="title" item-value="value" label="Nature" variant="outlined" density="compact" hide-details="auto" />
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
