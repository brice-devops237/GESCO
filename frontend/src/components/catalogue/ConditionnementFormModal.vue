<script setup lang="ts">
import { getConditionnement, createConditionnement, updateConditionnement, listUnitesMesure } from '@/api/catalogue'
import type { ConditionnementCreate, ConditionnementUpdate, TypeEmballage } from '@/api/types/catalogue'
import type { UniteMesureResponse } from '@/api/types/catalogue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ entrepriseId: number; conditionnementId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const unites = ref<UniteMesureResponse[]>([])

const typeEmballageOptions: { title: string; value: TypeEmballage }[] = [
  { title: 'Caisse', value: 'caisse' },
  { title: 'Carton', value: 'carton' },
  { title: 'Palette', value: 'palette' },
  { title: 'Sachet', value: 'sachet' },
  { title: 'Bidon', value: 'bidon' },
  { title: 'Fût', value: 'fut' },
  { title: 'Bouteille', value: 'bouteille' },
  { title: 'Autre', value: 'autre' },
]

const form = ref({
  code: '',
  libelle: '',
  quantite_unites: '' as number | string,
  unite_id: null as number | null,
  type_emballage: null as TypeEmballage | null,
  poids_net_kg: '' as number | string,
  actif: true,
})

const rules = {
  code: [required(), maxLength(30, 'Max. 30 caractères')],
  libelle: [required(), maxLength(80, 'Max. 80 caractères')],
  quantite_unites: [required(), (v: string) => !isNaN(Number(v)) && Number(v) > 0 || 'Quantité > 0'],
  unite_id: [required()],
}

const isEdit = computed(() => props.conditionnementId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le conditionnement' : 'Nouveau conditionnement'))
const uniteOptions = computed(() => unites.value.map(u => ({ title: `${u.code} — ${u.libelle}`, value: u.id })))

async function loadUnites() {
  try {
    unites.value = await listUnitesMesure({ limit: 200 })
  } catch {
    unites.value = []
  }
}

async function load() {
  if (!props.conditionnementId) return
  loading.value = true
  try {
    const c = await getConditionnement(props.conditionnementId)
    form.value = {
      code: c.code,
      libelle: c.libelle,
      quantite_unites: c.quantite_unites,
      unite_id: c.unite_id,
      type_emballage: (c.type_emballage as TypeEmballage) ?? null,
      poids_net_kg: c.poids_net_kg ?? '',
      actif: c.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.conditionnementId] as const, async ([open, id]) => {
  if (open) await loadUnites()
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '', quantite_unites: '', unite_id: null, type_emballage: null, poids_net_kg: '', actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur <strong>« ${form.value.code } »</strong> ?` : `Créer le conditionnement « ${form.value.code.trim() } » ?`,
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
    const qte = Number(form.value.quantite_unites)
    const poids = form.value.poids_net_kg === '' ? null : Number(form.value.poids_net_kg)
    if (isEdit.value && props.conditionnementId) {
      await updateConditionnement(props.conditionnementId, {
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        quantite_unites: isNaN(qte) ? form.value.quantite_unites : qte,
        unite_id: form.value.unite_id!,
        type_emballage: form.value.type_emballage,
        poids_net_kg: poids,
        actif: form.value.actif,
      } as ConditionnementUpdate)
      toastStore.success('Conditionnement mis à jour.')
    } else {
      await createConditionnement({
        entreprise_id: props.entrepriseId,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        quantite_unites: isNaN(qte) ? form.value.quantite_unites : qte,
        unite_id: form.value.unite_id!,
        type_emballage: form.value.type_emballage,
        poids_net_kg: poids,
        actif: form.value.actif,
      } as ConditionnementCreate)
      toastStore.success('Conditionnement créé.')
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
          <div class="catalogue-modal-icon"><VIcon icon="ri-inbox-line" size="28" /></div>
          <div>
            <h2 class="catalogue-modal-title">{{ modalTitle }}</h2>
            <p class="catalogue-modal-subtitle">Quantité en unités et type d'emballage</p>
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
              <VTextField v-model="form.quantite_unites" label="Quantité (unités)" :rules="rules.quantite_unites" type="number" step="any" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.unite_id" :items="uniteOptions" :rules="rules.unite_id" item-title="title" item-value="value" label="Unité de mesure" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.type_emballage" :items="typeEmballageOptions" item-title="title" item-value="value" label="Type d'emballage" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.poids_net_kg" label="Poids net (kg)" type="number" step="0.01" variant="outlined" density="compact" hide-details="auto" />
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
