<script setup lang="ts">
import { getUniteMesure, createUniteMesure, updateUniteMesure } from '@/api/catalogue'
import type { UniteMesureCreate, UniteMesureUpdate, TypeUniteMesure } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ uniteId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const typeOptions: { title: string; value: TypeUniteMesure }[] = [
  { title: 'Unité', value: 'unite' },
  { title: 'Poids', value: 'poids' },
  { title: 'Volume', value: 'volume' },
  { title: 'Longueur', value: 'longueur' },
  { title: 'Surface', value: 'surface' },
]

const form = ref({
  code: '',
  libelle: '',
  symbole: '',
  type: 'unite' as TypeUniteMesure,
  code_cefact: '',
  actif: true,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.uniteId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier l\'unité de mesure' : 'Nouvelle unité de mesure'))

async function load() {
  if (!props.uniteId) return
  loading.value = true
  try {
    const u = await getUniteMesure(props.uniteId)
    form.value = {
      code: u.code,
      libelle: u.libelle,
      symbole: u.symbole ?? '',
      type: (u.type as TypeUniteMesure) || 'unite',
      code_cefact: u.code_cefact ?? '',
      actif: u.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.uniteId] as const, ([open, id]) => {
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '', symbole: '', type: 'unite', code_cefact: '', actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer l'unité « ${form.value.code.trim() } » ?`,
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
    if (isEdit.value && props.uniteId) {
      await updateUniteMesure(props.uniteId, {
        libelle: form.value.libelle.trim(),
        symbole: form.value.symbole?.trim() || null,
        type: form.value.type,
        code_cefact: form.value.code_cefact?.trim() || null,
        actif: form.value.actif,
      } as UniteMesureUpdate)
      toastStore.success('Unité mise à jour.')
    } else {
      await createUniteMesure({
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        symbole: form.value.symbole?.trim() || null,
        type: form.value.type,
        code_cefact: form.value.code_cefact?.trim() || null,
        actif: form.value.actif,
      } as UniteMesureCreate)
      toastStore.success('Unité créée.')
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
          <div class="catalogue-modal-icon"><VIcon icon="ri-ruler-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">{{ isEdit ? 'Modifier les informations' : 'Renseignez le code et le libellé' }}</p>
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
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.symbole" label="Symbole" variant="outlined" density="compact" hide-details="auto" placeholder="Ex. kg, L" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.type" :items="typeOptions" item-title="title" item-value="value" label="Type" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code_cefact" label="Code CEFACT" variant="outlined" density="compact" hide-details="auto" placeholder="Optionnel" />
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
