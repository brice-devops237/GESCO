<script setup lang="ts">
import { getContact, createContact, updateContact } from '@/api/partenaires'
import type { ContactCreate, ContactUpdate } from '@/api/types/partenaires'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  contactId: number | null
  tiersId: number
  tiersLabel: string
}>()
const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()
const toastStore = useToastStore()
const { required, maxLength } = useFormValidation()
const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const CIVILITE_OPTIONS = [
  { title: '—', value: '' },
  { title: 'M.', value: 'M.' },
  { title: 'Mme', value: 'Mme' },
  { title: 'Mlle', value: 'Mlle' },
  { title: 'Dr.', value: 'Dr.' },
  { title: 'Pr.', value: 'Pr.' },
]

const form = ref({
  civilite: '' as string | null,
  nom: '',
  prenom: '' as string | null,
  fonction: '' as string | null,
  telephone: '' as string | null,
  email: '' as string | null,
  est_principal: false,
  actif: true,
})

const rules = {
  nom: [required(), maxLength(80, 'Max. 80 caractères')],
}

const isEdit = computed(() => props.contactId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le contact' : 'Nouveau contact'))

async function load() {
  if (!props.contactId) return
  loading.value = true
  try {
    const u = await getContact(props.contactId)
    form.value = {
      nom: u.nom,
      prenom: u.prenom ?? '',
      fonction: u.fonction ?? '',
      telephone: u.telephone ?? '',
      email: u.email ?? '',
      est_principal: u.est_principal,
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

watch(() => [visible.value, props.contactId] as const, ([open, id]) => {
  if (open && id) load()
  if (open && !id) form.value = { nom: '', prenom: '', fonction: '', telephone: '', email: '', est_principal: false, actif: true }
}, { immediate: true })

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value && props.contactId) {
      await updateContact(props.contactId, {
        nom: form.value.nom.trim(),
        prenom: form.value.prenom?.trim() || null,
        fonction: form.value.fonction?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        email: form.value.email?.trim() || null,
        est_principal: form.value.est_principal,
        actif: form.value.actif,
      } as ContactUpdate)
      toastStore.success('Contact mis à jour.')
    } else {
      await createContact({
        tiers_id: props.tiersId,
        nom: form.value.nom.trim(),
        prenom: form.value.prenom?.trim() || null,
        fonction: form.value.fonction?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        email: form.value.email?.trim() || null,
        est_principal: form.value.est_principal,
        actif: form.value.actif,
      } as ContactCreate)
      toastStore.success('Contact créé.')
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
          <div class="partenaires-modal-icon"><VIcon icon="ri-contacts-book-line" size="28" /></div>
          <div>
            <h2 class="partenaires-modal-title">{{ modalTitle }}</h2>
            <p class="partenaires-modal-subtitle">Tiers : {{ tiersLabel }}</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="partenaires-modal-close" @click="onClose"><VIcon icon="ri-close-line" size="22" /></VBtn>
      </div>
      <div v-if="loading" class="d-flex justify-center py-8"><VProgressCircular indeterminate color="primary" size="40" /></div>
      <VCardText v-else class="partenaires-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="3">
              <VSelect v-model="form.civilite" :items="CIVILITE_OPTIONS" item-title="title" item-value="value" label="Civilité" variant="outlined" density="compact" hide-details="auto" clearable />
            </VCol>
            <VCol cols="12" sm="4">
              <VTextField v-model="form.nom" label="Nom" :rules="rules.nom" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="5">
              <VTextField v-model="form.prenom" label="Prénom" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12">
              <VTextField v-model="form.fonction" label="Fonction" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.telephone" label="Téléphone" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField v-model="form.email" label="Email" type="email" variant="outlined" density="compact" hide-details="auto" />
            </VCol>
            <VCol cols="12" class="d-flex gap-4">
              <VSwitch v-model="form.est_principal" label="Contact principal" color="primary" hide-details />
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
.partenaires-modal-dialog :deep(.v-overlay__content) { align-items: center; justify-content: center; }
.partenaires-modal-card { border-radius: 16px; overflow: hidden; }
.partenaires-modal-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 20px 24px; }
.partenaires-modal-icon { width: 48px; height: 48px; border-radius: 12px; background: rgba(var(--v-theme-primary), 0.12); display: flex; align-items: center; justify-content: center; }
.partenaires-modal-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.partenaires-modal-subtitle { font-size: 0.875rem; margin: 4px 0 0; opacity: 0.9; }
.partenaires-modal-close { flex-shrink: 0; }
.partenaires-modal-body { padding: 0 24px 16px; }
</style>
