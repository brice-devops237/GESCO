<script setup lang="ts">
import {
  listRoles,
  addPermissionToRole,
  removePermissionFromRole,
} from '@/api/parametrage'
import type { PermissionWithRolesResponse, RoleResponse } from '@/api/types/parametrage'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  permission: PermissionWithRolesResponse | null
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ updated: [] }>()

const authStore = useAuthStore()
const toastStore = useToastStore()
const roles = ref<RoleResponse[]>([])
const loading = ref(false)
const updating = ref<Record<number, boolean>>({})
const searchRole = ref('')

const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)

const filteredRoles = computed(() => {
  let list = roles.value
  const q = searchRole.value?.trim().toLowerCase()
  if (q) {
    list = list.filter(
      r =>
        (r.code && r.code.toLowerCase().includes(q)) ||
        (r.libelle && r.libelle.toLowerCase().includes(q)),
    )
  }
  return list
})

function isAssigned(role: RoleResponse): boolean {
  if (!props.permission || !props.permission.roles) return false
  return props.permission.roles.some(r => r.id === role.id)
}

async function loadRoles() {
  const eid = entrepriseId.value
  if (eid == null) {
    roles.value = []
    return
  }
  loading.value = true
  try {
    roles.value = await listRoles({ entreprise_id: eid, limit: 100 })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des rôles.')
  } finally {
    loading.value = false
  }
}

async function toggle(role: RoleResponse) {
  if (!props.permission) return
  const assigned = isAssigned(role)
  const roleLabel = role.libelle || role.code || `Rôle #${role.id}`
  const permLabel = `${props.permission.module}.${props.permission.action}`
  const result = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: assigned
      ? `Souhaitez vous réellement retirer le rôle <br><strong>${roleLabel}</strong> de la permission <strong>${permLabel}</strong> ?`
      : `Souhaitez vous réellement affecter le rôle <br><strong>${roleLabel}</strong> à la permission <strong>${permLabel}</strong> ?`,
    showCancelButton: true,
    confirmButtonText: assigned ? 'Retirer' : 'Affecter',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  updating.value = { ...updating.value, [role.id]: true }
  try {
    if (assigned) {
      await removePermissionFromRole(role.id, props.permission.id)
      toastStore.success(`Rôle ${role.code} retiré de la permission.`)
    } else {
      await addPermissionToRole({ role_id: role.id, permission_id: props.permission.id })
      toastStore.success(`Rôle ${role.code} affecté à la permission.`)
    }
    emit('updated')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la mise à jour.')
  } finally {
    updating.value = { ...updating.value, [role.id]: false }
  }
}

watch(visible, open => {
  if (open) {
    searchRole.value = ''
    loadRoles()
  }
})

function onClose() {
  visible.value = false
  emit('updated')
}
</script>

<template>
  <VDialog
    :model-value="visible"
    max-width="560"
    persistent
    content-class="roles-perm-modal-dialog"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="roles-perm-modal-card">
      <div class="roles-perm-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="roles-perm-modal-icon">
            <VIcon icon="ri-user-shared-line" size="50" />
          </div>
          <div>
            <h2 class="roles-perm-modal-title">Rôles pour cette permission</h2>
            <p v-if="permission" class="roles-perm-modal-subtitle">
              {{ permission.module }}.{{ permission.action }}
              <span v-if="permission.libelle"> — {{ permission.libelle }}</span>
            </p>
          </div>
        </div>
        <VBtn icon variant="text" size="small" class="roles-perm-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <VCardText class="roles-perm-modal-body">
        <VTextField
          v-model="searchRole"
          placeholder="Filtrer par code ou libellé…"
          density="compact"
          hide-details
          clearable
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="ri-search-line"
        />

        <VAlert v-if="entrepriseId == null" type="info" variant="tonal" density="compact" class="mb-4">
          Aucune entreprise en session. Les rôles sont chargés par entreprise.
        </VAlert>

        <div v-else-if="loading" class="d-flex justify-center py-8">
          <VProgressCircular indeterminate color="primary" size="40" />
        </div>

        <div v-else class="roles-perm-list">
          <div
            v-for="role in filteredRoles"
            :key="role.id"
            class="roles-perm-item d-flex align-center justify-space-between py-2 px-3 rounded"
          >
            <div class="flex-grow-1 min-width-0">
              <!-- <VChip size="small" color="primary" variant="tonal" class="mr-2">
                {{ role.code }}
              </VChip> -->
              <span class="text-body-2">{{ role.libelle || '—' }}</span>
              <VChip size="x-small"  class="ml-2" :color="role.entreprise_id == null ? 'secondary' : 'default'">
                {{ role.entreprise_id == null ? 'Système' : 'Entreprise' }}
              </VChip>
            </div>
            <VSwitch
              :model-value="isAssigned(role)"
              :disabled="!!updating[role.id]"
              color="primary"
              hide-details
              density="compact"
              @update:model-value="() => toggle(role)"
            />
          </div>
          <p v-if="!loading && filteredRoles.length === 0" class="text-center text-medium-emphasis py-4">
            Aucun rôle trouvé.
          </p>
        </div>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<style scoped>
.roles-perm-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.roles-perm-modal-card {
  border-radius: 16px;
  overflow: hidden;
}

.roles-perm-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
}

.roles-perm-modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.roles-perm-modal-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.roles-perm-modal-subtitle {
  font-size: 0.875rem;
  margin: 4px 0 0;
}

.roles-perm-modal-close {
  flex-shrink: 0;
}

.roles-perm-modal-body {
  padding: 0 24px 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.roles-perm-item:hover {
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.roles-perm-list {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 12px;
  overflow: hidden;
}
</style>
