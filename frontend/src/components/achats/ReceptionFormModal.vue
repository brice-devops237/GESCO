<script setup lang="ts">
import { getReception, createReception, updateReception, listDepots } from '@/api/achats'
import type { ReceptionCreate, ReceptionUpdate } from '@/api/types/achats'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  receptionId: number | null
  entrepriseId: number
  commandeFournisseurId: number
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const firstFieldRef = ref<{ focus: () => void } | null>(null)
const depots = ref<{ id: number; code: string; libelle: string }[]>([])

const etatItems = [
  { title: 'Brouillon', value: 'brouillon' },
  { title: 'Validée', value: 'validee' },
  { title: 'Annulée', value: 'annulee' },
]

const form = ref({
  commande_fournisseur_id: 0,
  depot_id: 0,
  numero: '',
  numero_bl_fournisseur: '' as string | null,
  date_reception: '',
  etat: 'brouillon',
  notes: '' as string | null,
})

const rules = {
  depot_id: [() => form.value.depot_id > 0 || 'Sélectionnez un dépôt'],
  numero: [required()],
  date_reception: [required()],
}

const depotOptions = computed(() => depots.value.map(d => ({ title: `${d.code} – ${d.libelle}`, value: d.id })))

const isEdit = computed(() => props.receptionId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la réception' : 'Nouvelle réception'))

async function loadDepots() {
  try {
    depots.value = await listDepots({ entreprise_id: props.entrepriseId, limit: 100 })
  } catch {
    depots.value = []
  }
}

async function load() {
  if (!props.receptionId) return
  loading.value = true
  try {
    const u = await getReception(props.receptionId)
    form.value = {
      commande_fournisseur_id: u.commande_fournisseur_id,
      depot_id: u.depot_id,
      numero: u.numero,
      numero_bl_fournisseur: u.numero_bl_fournisseur ?? '',
      date_reception: u.date_reception?.slice(0, 10) ?? '',
      etat: u.etat ?? 'brouillon',
      notes: u.notes ?? '',
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  const today = new Date().toISOString().slice(0, 10)
  form.value = {
    commande_fournisseur_id: props.commandeFournisseurId,
    depot_id: depots.value[0]?.id ?? 0,
    numero: '',
    numero_bl_fournisseur: '',
    date_reception: today,
    etat: 'brouillon',
    notes: '',
  }
}

function onClose() { emit('cancel') }

watch(() => [visible.value, props.receptionId, props.commandeFournisseurId] as const, async ([open, rid, cid]) => {
  if (open) await loadDepots()
  if (open && rid) load()
  if (open && !rid) {
    resetForm()
    form.value.commande_fournisseur_id = cid
  }
}, { immediate: true })

watch(depots, () => {
  if (visible.value && !props.receptionId && depots.value.length && !form.value.depot_id) form.value.depot_id = depots.value[0].id
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  const result = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value ? `Enregistrer les modifications sur la réception « ${form.value.numero} » ?` : `Créer la réception « ${form.value.numero} » ?`,
    showCancelButton: true,
    confirmButtonText: isEdit.value ? 'Modifier' : 'Créer',
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
    if (isEdit.value && props.receptionId) {
      await updateReception(props.receptionId, {
        numero_bl_fournisseur: form.value.numero_bl_fournisseur?.trim() || null,
        etat: form.value.etat,
        notes: form.value.notes?.trim() || null,
      } as ReceptionUpdate)
      toastStore.success('Réception mise à jour.')
    } else {
      await createReception({
        commande_fournisseur_id: form.value.commande_fournisseur_id,
        depot_id: form.value.depot_id,
        numero: form.value.numero.trim(),
        numero_bl_fournisseur: form.value.numero_bl_fournisseur?.trim() || null,
        date_reception: form.value.date_reception,
        etat: form.value.etat,
        notes: form.value.notes?.trim() || null,
      } as ReceptionCreate)
      toastStore.success('Réception créée.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement.')
  } finally {
    saving.value = false
  }
}

// Éviter l’avertissement aria-hidden : focus sur le premier champ à l’ouverture
watch([visible, loading], () => {
  if (visible.value && !loading.value) nextTick(() => firstFieldRef.value?.focus())
})
</script>

<template>
  <VDialog :model-value="visible" max-width="560" persistent content-class="achats-modal-dialog" @update:model-value="(v: boolean) => !v && onClose()">
    <VCard class="achats-modal-card overflow-hidden">
      <div class="achats-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="achats-modal-icon"><VIcon icon="ri-truck-line" size="28" /></div>
          <div>
            <h2 class="achats-modal-title">{{ modalTitle }}</h2>
            <p class="achats-modal-subtitle">Bon de réception (livraison fournisseur)</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="achats-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="achats-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField ref="firstFieldRef" v-model="form.numero" label="N° réception" :rules="rules.numero" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.depot_id" :items="depotOptions" item-title="title" item-value="value" label="Dépôt" :rules="rules.depot_id" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.numero_bl_fournisseur" label="N° BL fournisseur" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.date_reception" label="Date réception" :rules="rules.date_reception" type="date" variant="outlined" density="compact" hide-details="auto" :readonly="isEdit" />
            </VCol>
            <VCol cols="12">
              <VSelect v-model="form.etat" :items="etatItems" item-title="title" item-value="value" label="État" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.notes" label="Notes" variant="outlined" density="compact" hide-details="auto" multiline rows="2" />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4 gap-2">
        <VBtn variant="outlined" color="secondary" :disabled="saving" @click="onClose">Annuler</VBtn>
        <VBtn color="primary" :loading="saving" @click="onSubmit">{{ isEdit ? 'Enregistrer' : 'Créer' }}</VBtn>
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
