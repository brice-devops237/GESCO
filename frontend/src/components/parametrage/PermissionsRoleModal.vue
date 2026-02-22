<script setup lang="ts">
import {
  listPermissions,
  addPermissionToRole,
  removePermissionFromRole,
} from '@/api/parametrage'
import type { PermissionWithRolesResponse, RoleResponse } from '@/api/types/parametrage'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = withDefaults(
  defineProps<{
    role: RoleResponse | null
    modelValue?: boolean
  }>(),
  { modelValue: false },
)
const emit = defineEmits<{ updated: [] ; close: [] ; 'update:modelValue': [value: boolean] }>()

const toastStore = useToastStore()
const permissions = ref<PermissionWithRolesResponse[]>([])
const loading = ref(false)
const updating = ref<Record<number, boolean>>({})
const searchPerm = ref('')

const filteredPermissions = computed(() => {
  let list = permissions.value
  const q = searchPerm.value?.trim().toLowerCase()
  if (q) {
    list = list.filter(
      p =>
        (p.module && p.module.toLowerCase().includes(q)) ||
        (p.action && p.action.toLowerCase().includes(q)) ||
        (p.libelle && p.libelle.toLowerCase().includes(q)),
    )
  }
  return list
})

function isAssigned(perm: PermissionWithRolesResponse): boolean {
  if (!props.role) return false
  return (perm.roles || []).some(r => r.id === props.role!.id)
}

async function loadPermissions() {
  loading.value = true
  try {
    permissions.value = await listPermissions({ limit: 200, include_roles: true })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des permissions.')
  } finally {
    loading.value = false
  }
}

async function toggle(perm: PermissionWithRolesResponse) {
  if (!props.role) return
  const assigned = isAssigned(perm)
  const permLabel = `${perm.module}.${perm.action}`
  const roleLabel = props.role.libelle || props.role.code || `Rôle #${props.role.id}`
  const result = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: assigned
      ? `Retirer la permission <br><strong>${permLabel}</strong> du rôle <strong>« ${roleLabel} »</strong> ?`
      : `Affecter la permission <br><strong>${permLabel}</strong> au rôle <strong>« ${roleLabel} »</strong> ?`,
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
  updating.value = { ...updating.value, [perm.id]: true }
  try {
    if (assigned) {
      await removePermissionFromRole(props.role.id, perm.id)
      toastStore.success(`Permission ${permLabel} retirée du rôle.`)
    } else {
      await addPermissionToRole({ role_id: props.role.id, permission_id: perm.id })
      toastStore.success(`Permission ${permLabel} affectée au rôle.`)
    }
    await loadPermissions()
    emit('updated')
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la mise à jour.')
  } finally {
    updating.value = { ...updating.value, [perm.id]: false }
  }
}

watch(() => props.modelValue, open => {
  if (open) {
    searchPerm.value = ''
    loadPermissions()
  }
})

function onClose() {
  emit('update:modelValue', false)
  emit('close')
  emit('updated')
}
</script>

<template>
  <VDialog
    :model-value="modelValue"
    max-width="640"
    persistent
    content-class="perm-role-modal-dialog"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="perm-role-modal-card">
      <div class="perm-role-modal-header">
        <div class="d-flex align-center gap-3">
          <div class="perm-role-modal-icon">
            <VIcon icon="ri-lock-2-line" size="50" />
          </div>
          <div>
            <h2 class="perm-role-modal-title">Permissions du rôle</h2>
            <p v-if="role" class="perm-role-modal-subtitle">
              {{ role.code }} — {{ role.libelle }}
            </p>
          </div>
        </div>
        <VBtn type="button" icon variant="text" size="small" class="perm-role-modal-close" @click.prevent="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <VCardText class="perm-role-modal-body">
        <VTextField
          v-model="searchPerm"
          placeholder="Filtrer par module, action ou libellé…"
          density="compact"
          hide-details
          clearable
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="ri-search-line"
        />

        <div v-if="loading" class="d-flex justify-center py-8">
          <VProgressCircular indeterminate color="primary" size="40" />
        </div>

        <div v-else class="perm-role-list">
          <div
            v-for="perm in filteredPermissions"
            :key="perm.id"
            class="perm-role-item d-flex align-center justify-space-between py-2 px-3 rounded"
          >
            <div class="flex-grow-1 min-width-0 d-flex align-center gap-2 flex-wrap">
              <VChip size="x-small" color="primary" variant="tonal" class="perm-module-chip">{{ perm.module }}</VChip>
              <span class="text-body-2 font-weight-medium">{{ perm.action }}</span>
              <span v-if="perm.libelle" class="text-medium-emphasis text-body-2">— {{ perm.libelle }}</span>
            </div>
            <VSwitch
              :model-value="isAssigned(perm)"
              :disabled="!!updating[perm.id]"
              color="primary"
              hide-details
              density="compact"
              @update:model-value="() => toggle(perm)"
            />
          </div>
          <p v-if="!loading && filteredPermissions.length === 0" class="text-center text-medium-emphasis py-4">
            Aucune permission trouvée.
          </p>
        </div>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<style scoped>
.perm-role-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.perm-role-modal-card {
  border-radius: 16px;
  overflow: hidden;
}

.perm-role-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
}

.perm-role-modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.perm-role-modal-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.perm-role-modal-subtitle {
  font-size: 0.875rem;
  margin: 4px 0 0;
}

.perm-role-modal-close {
  flex-shrink: 0;
}

.perm-role-modal-body {
  padding: 0 24px 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.perm-role-item:hover {
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.perm-role-list {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  border-radius: 12px;
  overflow: hidden;
}

.perm-module-chip {
  font-size: 0.7rem;
  font-weight: 600;
}
</style>
