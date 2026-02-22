<script setup lang="ts">
import { getDepot, createDepot, updateDepot } from '@/api/achats'
import type { DepotCreate, DepotUpdate } from '@/api/types/achats'
import { listPointsVente } from '@/api/parametrage'
import type { PointDeVenteResponse } from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  depotId: number | null
  entrepriseId: number
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const firstFieldRef = ref<{ focus: () => void } | null>(null)
const pointsVente = ref<PointDeVenteResponse[]>([])

const PAYS_OPTIONS = [
  { title: 'Cameroun', value: 'CMR' },
  { title: 'France', value: 'FRA' },
  { title: 'Sénégal', value: 'SEN' },
  { title: 'Côte d\'Ivoire', value: 'CIV' },
  { title: 'Gabon', value: 'GAB' },
  { title: '—', value: '' },
]

const form = ref({
  code: '',
  libelle: '',
  adresse: '' as string | null,
  ville: '' as string | null,
  code_postal: '' as string | null,
  pays: '' as string | null,
  point_de_vente_id: null as number | null,
})

const rules = {
  code: [required(), maxLength(20, 'Max. 20 caractères')],
  libelle: [required(), maxLength(100, 'Max. 100 caractères')],
}

const pdvOptions = computed(() => [
  { title: '— Aucun —', value: null },
  ...pointsVente.value.map(p => ({ title: `${p.code} - ${p.libelle}`, value: p.id })),
])

const isEdit = computed(() => props.depotId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le dépôt' : 'Nouveau dépôt'))

async function loadPdv() {
  if (!props.entrepriseId) return
  try {
    pointsVente.value = await listPointsVente(props.entrepriseId, { limit: 100 })
  } catch {
    pointsVente.value = []
  }
}

async function load() {
  if (!props.depotId) return
  loading.value = true
  try {
    const u = await getDepot(props.depotId)
    form.value = {
      code: u.code,
      libelle: u.libelle,
      adresse: u.adresse ?? '',
      ville: u.ville ?? '',
      code_postal: u.code_postal ?? '',
      pays: u.pays ?? 'CMR',
      point_de_vente_id: u.point_de_vente_id ?? null,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.depotId] as const, ([open, id]) => {
  if (open) loadPdv()
  if (open && id) load()
  if (open && !id) form.value = { code: '', libelle: '', adresse: '', ville: '', code_postal: '', pays: 'CMR', point_de_vente_id: null }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: isEdit.value ? `Enregistrer les modifications sur « ${form.value.code} » ?` : `Créer le dépôt « ${form.value.code.trim()} » ?`,
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
    if (isEdit.value && props.depotId) {
      await updateDepot(props.depotId, {
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        adresse: form.value.adresse?.trim() || null,
        ville: form.value.ville?.trim() || null,
        code_postal: form.value.code_postal?.trim() || null,
        pays: form.value.pays?.trim() || null,
        point_de_vente_id: form.value.point_de_vente_id,
      } as DepotUpdate)
      toastStore.success('Dépôt mis à jour.')
    } else {
      await createDepot({
        entreprise_id: props.entrepriseId,
        code: form.value.code.trim(),
        libelle: form.value.libelle.trim(),
        adresse: form.value.adresse?.trim() || null,
        ville: form.value.ville?.trim() || null,
        code_postal: form.value.code_postal?.trim() || null,
        pays: form.value.pays?.trim() || null,
        point_de_vente_id: form.value.point_de_vente_id,
      } as DepotCreate)
      toastStore.success('Dépôt créé.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de l\'enregistrement.')
  } finally {
    saving.value = false
  }
}

// Éviter l’avertissement aria-hidden : focus sur le premier champ à l’ouverture (pas sur le bouton fermer)
watch([visible, loading], () => {
  if (visible.value && !loading.value) nextTick(() => firstFieldRef.value?.focus())
})
</script>

<template>
  <VDialog :model-value="visible" max-width="560" persistent content-class="achats-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="achats-modal-card overflow-hidden">
      <div class="achats-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="achats-modal-icon"><VIcon icon="ri-warehouse-line" size="28" /></div>
          <div>
            <h2 class="achats-modal-title">{{ modalTitle }}</h2>
            <p class="achats-modal-subtitle">{{ isEdit ? 'Modifier l\'entrepôt' : 'Lieu de stockage (entrepôt, magasin, site)' }}</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="achats-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="achats-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField ref="firstFieldRef" v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.adresse" label="Adresse" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.ville" label="Ville" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.code_postal" label="Code postal" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.pays" :items="PAYS_OPTIONS" item-title="title" item-value="value" label="Pays" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.point_de_vente_id" :items="pdvOptions" item-title="title" item-value="value" label="Point de vente" variant="outlined" density="compact" hide-details="auto" />
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
.achats-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.achats-modal-card { border-radius: 16px; overflow: hidden; }
.achats-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.achats-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.achats-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.achats-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.achats-modal-close { flex-shrink: 0; }
.achats-modal-body { padding: 0 24px 16px; }
</style>
