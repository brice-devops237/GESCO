<script setup lang="ts">
import { getFamilleProduit, createFamilleProduit, updateFamilleProduit, listFamillesProduits } from '@/api/catalogue'
import type { FamilleProduitCreate, FamilleProduitUpdate } from '@/api/types/catalogue'
import type { FamilleProduitResponse } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ entrepriseId: number; familleId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const famillesOptions = ref<FamilleProduitResponse[]>([])

const form = ref({
  parent_id: null as number | null,
  code: '',
  libelle: '',
  description: '',
  niveau: 0,
  ordre_affichage: 0,
  actif: true,
})

const rules = {
  code: [required(), maxLength(50, 'Max. 50 caractères')],
  libelle: [required(), maxLength(100, 'Max. 100 caractères')],
}

const isEdit = computed(() => props.familleId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la famille' : 'Nouvelle famille'))
const parentOptions = computed(() => [
  { title: '— Aucune (racine)', value: null },
  ...famillesOptions.value.filter(f => !props.familleId || f.id !== props.familleId).map(f => ({ title: `${f.code} — ${f.libelle}`, value: f.id })),
])

async function loadFamilles() {
  try {
    famillesOptions.value = await listFamillesProduits({ entreprise_id: props.entrepriseId, limit: 200 })
  } catch {
    famillesOptions.value = []
  }
}

async function load() {
  if (!props.familleId) return
  loading.value = true
  try {
    const f = await getFamilleProduit(props.familleId)
    form.value = {
      parent_id: f.parent_id ?? null,
      code: f.code,
      libelle: f.libelle,
      description: f.description ?? '',
      niveau: f.niveau,
      ordre_affichage: f.ordre_affichage,
      actif: f.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.familleId] as const, async ([open, id]) => {
  if (open) await loadFamilles()
  if (open && id) load()
  if (open && !id) form.value = { parent_id: null, code: '', libelle: '', description: '', niveau: 0, ordre_affichage: 0, actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer la famille « ${form.value.code.trim() } » ?`,
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
    if (isEdit.value && props.familleId) {
      await updateFamilleProduit(props.familleId, {
        parent_id: form.value.parent_id,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        description: form.value.description?.trim() || null,
        niveau: form.value.niveau,
        ordre_affichage: form.value.ordre_affichage,
        actif: form.value.actif,
      } as FamilleProduitUpdate)
      toastStore.success('Famille mise à jour.')
    } else {
      await createFamilleProduit({
        entreprise_id: props.entrepriseId,
        parent_id: form.value.parent_id,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        description: form.value.description?.trim() || null,
        niveau: form.value.niveau,
        ordre_affichage: form.value.ordre_affichage,
        actif: form.value.actif,
      } as FamilleProduitCreate)
      toastStore.success('Famille créée.')
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
          <div class="catalogue-modal-icon"><VIcon icon="ri-folder-open-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">Famille ou sous-famille de produits</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="catalogue-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="catalogue-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12">
              <VSelect v-model="form.parent_id" :items="parentOptions" item-title="title" item-value="value" label="Famille parente" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.description" label="Description" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model.number="form.niveau" label="Niveau" type="number" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model.number="form.ordre_affichage" label="Ordre d'affichage" type="number" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12"><VSwitch v-model="form.actif" label="Actif" color="primary" hide-details /></VCol>
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
