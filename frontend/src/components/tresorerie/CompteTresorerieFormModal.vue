<script setup lang="ts">
import { getCompteTresorerie, createCompteTresorerie, updateCompteTresorerie } from '@/api/tresorerie'
import { listDevises } from '@/api/parametrage'
import type { DeviseResponse } from '@/api/types/parametrage'
import type { CompteTresorerieCreate, CompteTresorerieUpdate } from '@/api/types/tresorerie'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  compteTresorerieId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: []; cancel: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const { required } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const devises = ref<DeviseResponse[]>([])

const typeCompteOptions = [
  { title: 'Banque', value: 'banque' },
  { title: 'Caisse', value: 'caisse' },
]

const form = ref({
  type_compte: 'banque',
  libelle: '',
  numero_compte: '' as string | null,
  iban: '' as string | null,
  devise_id: null as number | null,
  actif: true,
})

const rules = {
  libelle: [required()],
  devise_id: [required()],
}

const isEdit = computed(() => props.compteTresorerieId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier le compte trésorerie' : 'Nouveau compte trésorerie'))

const deviseItems = computed(() =>
  devises.value.map(d => ({ title: `${d.code} - ${d.libelle}`, value: d.id })),
)

async function loadDevises() {
  try {
    devises.value = (await listDevises({ limit: 100 })).items ?? []
  } catch {
    devises.value = []
  }
}

async function loadCompteTresorerie() {
  if (!props.compteTresorerieId) return
  loading.value = true
  try {
    const d = await getCompteTresorerie(props.compteTresorerieId)
    form.value = {
      type_compte: d.type_compte || 'banque',
      libelle: d.libelle,
      numero_compte: d.numero_compte ?? '',
      iban: d.iban ?? '',
      devise_id: d.devise_id,
      actif: d.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    emit('cancel')
  } finally {
    loading.value = false
  }
}

function onClose() {
  emit('cancel')
}

watch(
  () => [visible.value, props.compteTresorerieId] as const,
  async ([open, id]) => {
    if (open) await loadDevises()
    if (open && id) loadCompteTresorerie()
    if (open && !id) {
      form.value = {
        type_compte: 'banque',
        libelle: '',
        numero_compte: '',
        iban: '',
        devise_id: null,
        actif: true,
      }
    }
  },
  { immediate: true },
)

async function onSubmit() {
  const valid = (await formRef.value?.validate().then(r => r.valid)) ?? false
  if (!valid) return

  const confirmResult = await Swal.fire({
    title: 'Confirmer',
    html: isEdit.value
      ? `Enregistrer les modifications sur le compte <b>« ${String(form.value.libelle).trim()} »</b> ?`
      : `Créer le compte trésorerie « ${String(form.value.libelle).trim()} » ?`,
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

  const entrepriseId = authStore.userInfo?.entreprise_id
  if (!entrepriseId) {
    toastStore.error('Entreprise non définie.')
    return
  }
  if (!form.value.devise_id) {
    toastStore.error('Veuillez sélectionner une devise.')
    return
  }

  saving.value = true
  try {
    if (isEdit.value && props.compteTresorerieId) {
      const body: CompteTresorerieUpdate = {
        type_compte: form.value.type_compte,
        libelle: form.value.libelle.trim(),
        numero_compte: form.value.numero_compte?.trim() || null,
        iban: form.value.iban?.trim() || null,
        devise_id: form.value.devise_id,
        actif: form.value.actif,
      }
      await updateCompteTresorerie(props.compteTresorerieId, body)
      toastStore.success('Compte trésorerie mis à jour.')
    } else {
      const body: CompteTresorerieCreate = {
        entreprise_id: entrepriseId,
        type_compte: form.value.type_compte,
        libelle: form.value.libelle.trim(),
        numero_compte: form.value.numero_compte?.trim() || null,
        iban: form.value.iban?.trim() || null,
        devise_id: form.value.devise_id,
        actif: form.value.actif,
      }
      await createCompteTresorerie(body)
      toastStore.success('Compte trésorerie créé.')
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
  <VDialog
    :model-value="visible"
    max-width="600"
    persistent
    content-class="compte-tresorerie-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="compte-tresorerie-modal-card overflow-hidden">
      <div class="d-flex align-center justify-space-between pa-4 pb-2">
        <h2 class="text-h6">{{ modalTitle }}</h2>
        <VBtn icon variant="text" size="small" @click="onClose">
          <VIcon icon="ri-close-line" />
        </VBtn>
      </div>
      <div v-if="loading" class="d-flex flex-column align-center justify-center pa-8">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>
      <VCardText v-else class="pt-0">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense>
            <VCol cols="12" sm="6">
              <VSelect
                v-model="form.type_compte"
                :items="typeCompteOptions"
                item-title="title"
                item-value="value"
                label="Type de compte"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.libelle"
                label="Libellé"
                :rules="rules.libelle"
                variant="outlined"
                density="compact"
                hide-details="auto"
                placeholder="Ex. Compte principal"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.numero_compte"
                label="Numéro de compte (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
              />
            </VCol>
            <VCol cols="12" sm="6">
              <VTextField
                v-model="form.iban"
                label="IBAN (optionnel)"
                variant="outlined"
                density="compact"
                hide-details="auto"
                placeholder="Ex. FR76…"
              />
            </VCol>
            <VCol cols="12">
              <VSelect
                v-model="form.devise_id"
                :items="deviseItems"
                :rules="rules.devise_id"
                label="Devise"
                variant="outlined"
                density="compact"
                hide-details="auto"
                clearable
              />
            </VCol>
            <VCol cols="12">
              <VSwitch
                v-model="form.actif"
                label="Compte actif"
                color="primary"
                hide-details
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
      <VDivider />
      <VCardActions class="pa-4">
        <VSpacer />
        <VBtn variant="outlined" color="secondary" :disabled="saving" @click="onClose">
          Annuler
        </VBtn>
        <VBtn color="primary" :loading="saving" :disabled="loading" @click="onSubmit">
          {{ isEdit ? 'Modifier' : 'Enregistrer' }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.compte-tresorerie-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}
.compte-tresorerie-modal-card {
  border-radius: 12px;
}
</style>
