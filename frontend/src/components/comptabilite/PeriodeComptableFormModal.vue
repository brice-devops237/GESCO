<script setup lang="ts">
import { getPeriodeComptable, createPeriodeComptable, updatePeriodeComptable } from '@/api/comptabilite'
import type { PeriodeComptableCreate, PeriodeComptableUpdate } from '@/api/types/comptabilite'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ periodeId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({ date_debut: '', date_fin: '', libelle: '', cloturee: false })
const rules = { date_debut: [required()], date_fin: [required()], libelle: [required()] }
const isEdit = computed(() => props.periodeId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier la période' : 'Nouvelle période comptable'))

async function load() {
  if (!props.periodeId) return
  loading.value = true
  try {
    const d = await getPeriodeComptable(props.periodeId)
    form.value = {
      date_debut: d.date_debut?.slice(0, 10) ?? '',
      date_fin: d.date_fin?.slice(0, 10) ?? '',
      libelle: d.libelle,
      cloturee: d.cloturee,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(
  () => [visible.value, props.periodeId] as const,
  ([open, id]) => {
    if (open && id) load()
    if (open && !id) {
      const today = new Date().toISOString().slice(0, 10)
      form.value = { date_debut: today, date_fin: today, libelle: '', cloturee: false }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = (await formRef.value?.validate().then(r => r.valid)) ?? false
  if (!valid) return
  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) { toastStore.error('Entreprise non définie.'); return }

  const confirmResult = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value ? `Enregistrer les modifications sur la période <b>${form.value.libelle}</b> ?` : `Créer la période « ${form.value.libelle} » ?`,
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
    if (isEdit.value && props.periodeId) {
      await updatePeriodeComptable(props.periodeId, {
        date_fin: form.value.date_fin,
        libelle: form.value.libelle.trim(),
        cloturee: form.value.cloturee,
      })
      toastStore.success('Période mise à jour.')
    } else {
      await createPeriodeComptable({
        entreprise_id: entrepriseId,
        date_debut: form.value.date_debut,
        date_fin: form.value.date_fin,
        libelle: form.value.libelle.trim(),
      })
      toastStore.success('Période créée.')
    }
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur enregistrement.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <VDialog :model-value="visible" max-width="520" persistent @update:model-value="(v: boolean) => !v && onClose()">
    <VCard>
      <div class="d-flex align-center justify-space-between pa-4 pb-2">
        <h2 class="text-h6">{{ modalTitle }}</h2>
        <VBtn icon variant="text" size="small" @click="onClose"><VIcon icon="ri-close-line" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex flex-column align-center pa-8"><VProgressCircular indeterminate color="primary" size="48" /></div>
      <VCardText v-else class="pt-0">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.date_debut" label="Date début" :rules="rules.date_debut" type="date" variant="outlined" density="compact" hide-details="auto" :disabled="isEdit" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.date_fin" label="Date fin" :rules="rules.date_fin" type="date" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol v-if="isEdit" cols="12">
              <VSwitch v-model="form.cloturee" label="Période clôturée" color="primary" hide-details />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4">
        <VSpacer />
        <VBtn variant="outlined" color="secondary" :disabled="saving" @click="onClose">Annuler</VBtn>
        <VBtn color="primary" :loading="saving" :disabled="loading" @click="onSubmit">{{ isEdit ? 'Modifier' : 'Enregistrer' }}</VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>
