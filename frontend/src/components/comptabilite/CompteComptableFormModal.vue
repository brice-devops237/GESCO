<script setup lang="ts">
import { getCompteComptable, createCompteComptable, updateCompteComptable } from '@/api/comptabilite'
import type { CompteComptableCreate, CompteComptableUpdate } from '@/api/types/comptabilite'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{ compteId: number | null }>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const sensOptions = [
  { title: 'Débit', value: 'debit' },
  { title: 'Crédit', value: 'credit' },
]
const typeCompteOptions = [
  { title: '—', value: '' },
  { title: 'Actif', value: 'actif' },
  { title: 'Passif', value: 'passif' },
  { title: 'Charge', value: 'charge' },
  { title: 'Produit', value: 'produit' },
]

const form = ref({
  numero: '',
  libelle: '',
  type_compte: '' as string | null,
  sens_normal: 'debit',
  actif: true,
})

const rules = { numero: [required()], libelle: [required()] }
const isEdit = computed(() => props.compteId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le compte' : 'Nouveau compte comptable'))

async function load() {
  if (!props.compteId) return
  loading.value = true
  try {
    const d = await getCompteComptable(props.compteId)
    form.value = {
      numero: d.numero,
      libelle: d.libelle,
      type_compte: d.type_compte ?? '',
      sens_normal: d.sens_normal || 'debit',
      actif: d.actif,
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
  () => [visible.value, props.compteId] as const,
  ([open, id]) => {
    if (open && id) load()
    if (open && !id) form.value = { numero: '', libelle: '', type_compte: '', sens_normal: 'debit', actif: true }
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
    html: isEdit.value ? `Enregistrer les modifications sur le compte <b>${form.value.numero}</b> ?` : `Créer le compte « ${form.value.numero} » ?`,
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
    if (isEdit.value && props.compteId) {
      await updateCompteComptable(props.compteId, {
        numero: form.value.numero.trim(),
        libelle: form.value.libelle.trim(),
        type_compte: form.value.type_compte || null,
        sens_normal: form.value.sens_normal,
        actif: form.value.actif,
      })
      toastStore.success('Compte mis à jour.')
    } else {
      await createCompteComptable({
        entreprise_id: entrepriseId,
        numero: form.value.numero.trim(),
        libelle: form.value.libelle.trim(),
        type_compte: form.value.type_compte || null,
        sens_normal: form.value.sens_normal,
        actif: form.value.actif,
      })
      toastStore.success('Compte créé.')
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
  <VDialog :model-value="visible" max-width="560" persistent @update:model-value="(v: boolean) => !v && onClose()">
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
              <VTextField v-model="form.numero" label="Numéro" :rules="rules.numero" :readonly="isEdit" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.libelle" label="Libellé" :rules="rules.libelle" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.type_compte" :items="typeCompteOptions" item-title="title" item-value="value" label="Type de compte" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="6">
              <VSelect v-model="form.sens_normal" :items="sensOptions" item-title="title" item-value="value" label="Sens normal" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VSwitch v-model="form.actif" label="Compte actif" color="primary" hide-details />
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
