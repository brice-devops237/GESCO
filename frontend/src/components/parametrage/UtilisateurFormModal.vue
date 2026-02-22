<script setup lang="ts">
import {
  getUtilisateur,
  createUtilisateur,
  updateUtilisateur,
  listRoles,
  listPointsVente,
} from '@/api/parametrage'
import type {
  UtilisateurCreate,
  UtilisateurUpdate,
  RoleResponse,
  PointDeVenteResponse,
} from '@/api/types/parametrage'
import { useFormValidation } from '@/composables/useFormValidation'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  entrepriseId: number
  utilisateurId: number | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] ; cancel: [] }>()

const toastStore = useToastStore()
const { required, maxLength, email } = useFormValidation()

const loading = ref(false)
const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const roles = ref<RoleResponse[]>([])
const pointsVente = ref<PointDeVenteResponse[]>([])

const form = ref({
  login: '',
  mot_de_passe: '',
  nom: '',
  prenom: '',
  email: '',
  telephone: '',
  role_id: null as number | null,
  point_de_vente_id: null as number | null,
  actif: true,
})

const rules = {
  login: [required(), maxLength(80)],
  nom: [required(), maxLength(120)],
  email: [email()],
}
const passwordRules = computed(() => (isEdit.value ? [] : [required()]))
const roleOptions = computed(() =>
  roles.value.map(r => ({ title: `${r.libelle}`, value: r.id })), //${r.code} - ${r.libelle}
)
const pdvOptions = computed(() =>
  pointsVente.value.map(p => ({ title: `${p.code} - ${p.libelle}`, value: p.id })),
)

const isEdit = computed(() => props.utilisateurId != null)
const modalTitle = computed(() => (isEdit.value ? 'Modifier l\'utilisateur' : 'Nouvel utilisateur'))
const modalSubtitle = computed(() =>
  isEdit.value
    ? 'Modifier les informations et le rôle de l\'utilisateur'
    : 'Créer un compte utilisateur (login, mot de passe, rôle).',
)

async function loadOptions() {
  try {
    const [r, p] = await Promise.all([
      listRoles({ entreprise_id: props.entrepriseId, limit: 100 }),
      listPointsVente(props.entrepriseId, { limit: 100 }),
    ])
    roles.value = r
    pointsVente.value = p
  } catch {
    roles.value = []
    pointsVente.value = []
  }
}

async function loadUtilisateur() {
  if (!props.utilisateurId) return
  loading.value = true
  try {
    const u = await getUtilisateur(props.utilisateurId)
    form.value = {
      login: u.login,
      mot_de_passe: '',
      nom: u.nom,
      prenom: u.prenom ?? '',
      email: u.email ?? '',
      telephone: u.telephone ?? '',
      role_id: u.role_id,
      point_de_vente_id: u.point_de_vente_id ?? null,
      actif: u.actif,
    }
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
    onCancel()
  } finally {
    loading.value = false
  }
}

watch(
  () => [visible.value, props.utilisateurId] as const,
  async ([open, id]) => {
    if (open) {
      await loadOptions()
      if (id) loadUtilisateur()
      else {
        form.value = {
          login: '',
          mot_de_passe: '',
          nom: '',
          prenom: '',
          email: '',
          telephone: '',
          role_id: roles.value[0]?.id ?? null,
          point_de_vente_id: null,
          actif: true,
        }
      }
    }
  },
  { immediate: true },
)

function onCancel() {
  visible.value = false
  emit('cancel')
}

async function onSubmit() {
  const valid = await formRef.value?.validate().then(r => r.valid) ?? false
  if (!valid) return
  if (!form.value.role_id) {
    toastStore.error('Sélectionnez un rôle.')
    return
  }
  if (!isEdit.value && !form.value.mot_de_passe?.trim()) {
    toastStore.error('Le mot de passe est obligatoire à la création.')
    return
  }
  const name = [form.value.nom, form.value.prenom].filter(Boolean).join(' ').trim() || form.value.login
  const confirmResult = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: isEdit.value
      ? `Enregistrer les modifications sur l'utilisateur <br><strong>« ${name} »</strong> ?`
      : `Souhaitez vous réellement créer l'utilisateur <br><strong>« ${form.value.login.trim()} »</strong> ?`,
    showCancelButton: true,
    cancelButtonText: 'Annuler',
    confirmButtonText: isEdit.value ? 'Modifier' : 'Enregistrer',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!confirmResult.isConfirmed) return
  saving.value = true
  try {
    if (isEdit.value && props.utilisateurId) {
      const body: UtilisateurUpdate = {
        role_id: form.value.role_id,
        point_de_vente_id: form.value.point_de_vente_id,
        nom: form.value.nom.trim(),
        prenom: form.value.prenom?.trim() || null,
        email: form.value.email?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        actif: form.value.actif,
      }
      if (form.value.mot_de_passe?.trim()) body.mot_de_passe = form.value.mot_de_passe.trim()
      await updateUtilisateur(props.utilisateurId, body)
      toastStore.success('Utilisateur mis à jour.')
    } else {
      const body: UtilisateurCreate = {
        entreprise_id: props.entrepriseId,
        role_id: form.value.role_id,
        point_de_vente_id: form.value.point_de_vente_id ?? undefined,
        login: form.value.login.trim(),
        mot_de_passe: form.value.mot_de_passe!.trim(),
        nom: form.value.nom.trim(),
        prenom: form.value.prenom?.trim() || null,
        email: form.value.email?.trim() || null,
        telephone: form.value.telephone?.trim() || null,
        actif: form.value.actif,
      }
      await createUtilisateur(body)
      toastStore.success('Utilisateur créé.')
    }
    visible.value = false
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
    max-width="800"
    persistent
    content-class="util-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onCancel()"
  >
    <VCard class="util-modal-card overflow-hidden">
      <div class="util-modal-header">
        <div class="util-modal-header-content">
          <div class="util-modal-icon-wrap">
            <VIcon icon="ri-user-add-line" size="50" />
          </div>
          <div class="util-modal-title-wrap">
            <h2 class="util-modal-title">{{ modalTitle }}</h2>
            <p class="util-modal-subtitle">{{ modalSubtitle }}</p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="util-modal-close" @click="onCancel">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <div v-if="loading" class="util-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText class="util-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VRow dense class="mt-2">
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.login"
                label="Login"
                :rules="rules.login"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-user-line"
                placeholder="Identifiant de connexion"
                clearable
              />
            </VCol>
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.mot_de_passe"
                :label="isEdit ? 'Mot de passe' : 'Mot de passe'"
                type="password"
                :rules="passwordRules"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-lock-line"
                :placeholder="isEdit ? 'Laisser vide pour conserver' : 'Minimum 8 caractères'"
                clearable
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.nom"
                label="Nom"
                :rules="rules.nom"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-user-line"
                clearable
              />
            </VCol>
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.prenom"
                label="Prénom"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-user-line"
                clearable
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.email"
                label="Email"
                :rules="rules.email"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-mail-line"
                clearable
              />
            </VCol>
            <VCol cols="12" md="6">
              <VTextField
                v-model="form.telephone"
                label="Téléphone"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-phone-line"
                clearable
              />
            </VCol>
          </VRow>
          <VRow dense class="mt-4">
            <VCol cols="12" md="12">
              <VAutocomplete
                v-model="form.role_id"
                label="Rôle"
                :items="roleOptions"
                item-title="title"
                item-value="value"
                :rules="[required()]"
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-shield-user-line"
                clearable
              />
            </VCol>
            <VCol cols="12" md="6" class="d-none">
              <VAutocomplete
                v-model="form.point_de_vente_id"
                label="Point de vente (optionnel)"
                :items="pdvOptions"
                item-title="title"
                item-value="value"
                clearable
                variant="outlined"
                density="compact"
                hide-details="auto"
                class="util-field"
                prepend-inner-icon="ri-store-2-line"
              />
            </VCol>
          </VRow>
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="util-modal-actions">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onCancel">
          Annuler
        </VBtn>
        <VBtn
          color="primary"
          variant="flat"
          :loading="saving"
          :disabled="loading"
          @click="onSubmit"
        >
          {{ isEdit ? 'Modifier' : 'Enregistrer' }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.util-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.util-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.util-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
  }

.util-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.util-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.util-modal-title-wrap {
  min-width: 0;
}

.util-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.util-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.util-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.util-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.util-modal-loading {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
  border-radius: 0 0 16px 16px;
}

.util-modal-body {
  padding: 24px 24px 20px;
}

.util-field :deep(.v-field) {
  border-radius: 10px;
}

.util-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
