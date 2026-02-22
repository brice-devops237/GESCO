<script setup lang="ts">
import { changePasswordUtilisateur } from '@/api/parametrage'
import type { UtilisateurResponse } from '@/api/types/parametrage'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  utilisateur: UtilisateurResponse | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ saved: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()

const saving = ref(false)
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)
const showAncien = ref(false)
const showNouveau = ref(false)
const showConfirmer = ref(false)

const isOwnAccount = computed(
  () => props.utilisateur != null && authStore.userInfo?.user_id === props.utilisateur.id,
)

const form = ref({
  ancien_mot_de_passe: '',
  nouveau_mot_de_passe: '',
  confirmer: '',
})

const rules = {
  nouveau_mot_de_passe: [
    (v: string) => !!v?.trim() || 'Le nouveau mot de passe est requis.',
    (v: string) => (v?.trim()?.length ?? 0) >= 8 || 'Minimum 8 caractères.',
  ],
  confirmer: [
    (v: string) => !!v?.trim() || 'Veuillez confirmer le mot de passe.',
    (v: string) => v === form.value.nouveau_mot_de_passe || 'Les mots de passe ne correspondent pas.',
  ],
  ancien_mot_de_passe: [
    (v: string) => !isOwnAccount.value || !!v?.trim() || 'Le mot de passe actuel est requis.',
  ],
}

watch(visible, (open) => {
  if (open) {
    form.value = {
      ancien_mot_de_passe: '',
      nouveau_mot_de_passe: '',
      confirmer: '',
    }
    showAncien.value = false
    showNouveau.value = false
    showConfirmer.value = false
  }
})

async function onSubmit() {
  const { valid } = (await formRef.value?.validate()) ?? { valid: false }
  if (!valid || !props.utilisateur) return
  if (form.value.nouveau_mot_de_passe !== form.value.confirmer) {
    toastStore.error('Les mots de passe ne correspondent pas.')
    return
  }
  const name = [props.utilisateur.nom, props.utilisateur.prenom].filter(Boolean).join(' ') || props.utilisateur.login
  const result = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: `Modifier le mot de passe de l'utilisateur<br> <strong>« ${name} »</strong> ?`,
    showCancelButton: true,
    confirmButtonText: 'Enregistrer',
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
    await changePasswordUtilisateur(props.utilisateur.id, {
      ancien_mot_de_passe: isOwnAccount.value ? form.value.ancien_mot_de_passe?.trim() || undefined : undefined,
      nouveau_mot_de_passe: form.value.nouveau_mot_de_passe.trim(),
    })
    toastStore.success('Mot de passe modifié.')
    visible.value = false
    emit('saved')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du changement de mot de passe.')
  } finally {
    saving.value = false
  }
}

function onClose() {
  visible.value = false
}
</script>

<template>
  <VDialog
    :model-value="visible"
    max-width="460"
    persistent
    content-class="mdp-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="mdp-modal-card overflow-hidden">
      <div class="mdp-modal-header">
        <div class="mdp-modal-header-content">
          <div class="mdp-modal-icon-wrap">
            <VIcon icon="ri-lock-password-line" size="50" />
          </div>
          <div class="mdp-modal-title-wrap">
            <h2 class="mdp-modal-title">Changer le mot de passe</h2>
            <p v-if="utilisateur" class="mdp-modal-subtitle">
              {{ utilisateur.login }} — {{ utilisateur.nom }} {{ utilisateur.prenom || '' }}
            </p>
            <p v-else class="mdp-modal-subtitle">
              Saisissez l'ancien et le nouveau mot de passe.
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="mdp-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <VCardText class="mdp-modal-body">
        <VForm ref="formRef" @submit.prevent="onSubmit">
          <VTextField
            v-if="isOwnAccount"
            v-model="form.ancien_mot_de_passe"
            label="Mot de passe actuel"
            :type="showAncien ? 'text' : 'password'"
            :rules="rules.ancien_mot_de_passe"
            variant="outlined"
            density="compact"
            hide-details="auto"
            class="mdp-field mb-3"
            prepend-inner-icon="ri-lock-line"
            :append-inner-icon="showAncien ? 'ri-eye-off-line' : 'ri-eye-line'"
            autocomplete="current-password"
            @click:append-inner="showAncien = !showAncien"
          />
          <VTextField
            v-model="form.nouveau_mot_de_passe"
            label="Nouveau mot de passe"
            :type="showNouveau ? 'text' : 'password'"
            :rules="rules.nouveau_mot_de_passe"
            variant="outlined"
            density="compact"
            hide-details="auto"
            class="mdp-field mb-3"
            prepend-inner-icon="ri-key-line"
            :append-inner-icon="showNouveau ? 'ri-eye-off-line' : 'ri-eye-line'"
            placeholder="Minimum 8 caractères"
            autocomplete="new-password"
            @click:append-inner="showNouveau = !showNouveau"
          />
          <VTextField
            v-model="form.confirmer"
            label="Confirmer le mot de passe"
            :type="showConfirmer ? 'text' : 'password'"
            :rules="rules.confirmer"
            variant="outlined"
            density="compact"
            hide-details="auto"
            class="mdp-field"
            prepend-inner-icon="ri-key-line"
            :append-inner-icon="showConfirmer ? 'ri-eye-off-line' : 'ri-eye-line'"
            autocomplete="new-password"
            @click:append-inner="showConfirmer = !showConfirmer"
          />
        </VForm>
      </VCardText>

      <VDivider />

      <VCardActions class="mdp-modal-actions">
        <VBtn variant="outlined" color="error" :disabled="saving" @click="onClose">
          Annuler
        </VBtn>
        <VBtn color="primary" variant="flat" :loading="saving" @click="onSubmit">
          Modifier
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>

<style scoped>
.mdp-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.mdp-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
}

.mdp-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
}

.mdp-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.mdp-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mdp-modal-title-wrap {
  min-width: 0;
}

.mdp-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.mdp-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.mdp-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.mdp-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.mdp-modal-body {
  padding: 24px 24px 20px;
}

.mdp-field :deep(.v-field) {
  border-radius: 10px;
}

.mdp-modal-actions {
  padding: 16px 24px 20px;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
