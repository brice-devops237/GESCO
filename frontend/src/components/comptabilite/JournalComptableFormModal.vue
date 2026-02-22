<script setup lang="ts">
import { getJournalComptable, createJournalComptable, updateJournalComptable } from '@/api/comptabilite'
import type { JournalComptableCreate, JournalComptableUpdate } from '@/api/types/comptabilite'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ journalId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const form = ref({ code: '', libelle: '', actif: true })
const rules = { code: [required()], libelle: [required()] }
const isEdit = computed(() => props.journalId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le journal' : 'Nouveau journal comptable'))

async function load() {
  if (!props.journalId) return
  loading.value = true
  try {
    const d = await getJournalComptable(props.journalId)
    form.value = { code: d.code, libelle: d.libelle, actif: d.actif }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() { emit('cancel') }

watch(
  () => [visible.value, props.journalId] as const,
  ([open, id]) => {
    if (open && id) load()
    if (open && !id) form.value = { code: '', libelle: '', actif: true }
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
    html: isEdit.value ? `Enregistrer les modifications sur le journal <b>${form.value.code}</b> ?` : `Créer le journal « ${form.value.code} » ?`,
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
    if (isEdit.value && props.journalId) {
      await updateJournalComptable(props.journalId, { code: form.value.code.trim(), libelle: form.value.libelle.trim(), actif: form.value.actif })
      toastStore.success('Journal mis à jour.')
    } else {
      await createJournalComptable({ entreprise_id: entrepriseId, code: form.value.code.trim(), libelle: form.value.libelle.trim(), actif: form.value.actif })
      toastStore.success('Journal créé.')
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
              <VTextField v-model="form.code" label="Code" :rules="rules.code" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VSwitch v-model="form.actif" label="Journal actif" color="primary" hide-details />
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
