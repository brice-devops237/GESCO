<script setup lang="ts">
import { getTypeTiers, createTypeTiers, updateTypeTiers } from '@/api/partenaires'
import type { TypeTiersCreate, TypeTiersUpdate } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ typeTiersId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({ code: '', libelle: '' })

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.typeTiersId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le type de tiers' : 'Nouveau type de tiers'))

async function load() {
  if (!props.typeTiersId) return
  loading.value = true
  try {
    const u = await getTypeTiers(props.typeTiersId)
    form.value = { code: u.code, libelle: u.libelle }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.typeTiersId] as const, ([open, id]) => {
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '' }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur « ${form.value.code} » ?` : `Créer le type « ${form.value.code.trim()} » ?`,
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
    if (isEdit.value && props.typeTiersId) {
      await updateTypeTiers(props.typeTiersId, { code: form.value.code.trim(), libelle: form.value.libelle.trim() } as TypeTiersUpdate)
      toastStore.success('Type de tiers mis à jour.')
    } else {
      await createTypeTiers({ code: form.value.code.trim(), libelle: form.value.libelle.trim() } as TypeTiersCreate)
      toastStore.success('Type de tiers créé.')
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
  <VDialog :model-value="visible" max-width="560" persistent content-class="partenaires-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="partenaires-modal-card overflow-hidden">
      <div class="partenaires-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="partenaires-modal-icon"><VIcon icon="ri-bookmark-line" size="28" /></div>
          <div>
            <h2 class="partenaires-modal-title">{{ modalTitle }}</h2>
            <p class="partenaires-modal-subtitle">{{ isEdit ? 'Modifier le type de partenaire' : 'Ex. Client, Fournisseur, Prospect – utilisé pour classer les tiers' }}</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="partenaires-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="partenaires-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
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
.partenaires-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.partenaires-modal-card { border-radius: 16px; overflow: hidden; }
.partenaires-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.partenaires-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.partenaires-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.partenaires-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.partenaires-modal-close { flex-shrink: 0; }
.partenaires-modal-body { padding: 0 24px 16px; }
</style>
