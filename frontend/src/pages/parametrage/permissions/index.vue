<script setup lang="ts">
import { listPermissions } from '@/api/parametrage'
import type { PermissionWithRolesResponse } from '@/api/types/parametrage'
import PermissionFormModal from '@/components/parametrage/PermissionFormModal.vue'
import RolesPermissionModal from '@/components/parametrage/RolesPermissionModal.vue'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const toastStore = useToastStore()
const permissions = ref<PermissionWithRolesResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const searchQuery = ref('')
const filterModule = ref<string | null>(null)
const rolesModalOpen = ref(false)
const selectedPermissionId = ref<number | null>(null)

const permissionForRolesModal = computed(() => {
  if (selectedPermissionId.value == null) return null
  return permissions.value.find(p => p.id === selectedPermissionId.value) ?? null
})

const moduleOptions = computed(() => {
  const modules = [...new Set(permissions.value.map(p => p.module).filter(Boolean))] as string[]
  return modules.sort((a, b) => a.localeCompare(b))
})

const headers = [
  { title: 'MODULE', key: 'module', sortable: true, width: 'min(140px, 16%)' },
  { title: 'ACTION', key: 'action', sortable: true, width: 'min(120px, 14%)' },
  { title: 'PERMISSION', key: 'libelle', sortable: true },
  { title: 'ATTRIBUÉ À', key: 'roles', sortable: false, width: 'min(260px, 30%)' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '100px', align: 'end' as const },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(permissions.value) ? permissions.value : []
  if (filterModule.value) {
    list = list.filter(p => p.module === filterModule.value)
  }
  const q = searchQuery.value?.trim().toLowerCase()
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

const paginatedItems = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  return filteredItems.value.slice(start, start + itemsPerPage.value)
})

const totalFiltered = computed(() => filteredItems.value.length)

const pageRangeText = computed(() => {
  const total = totalFiltered.value
  if (total === 0) return '0 sur 0'
  const start = (page.value - 1) * itemsPerPage.value + 1
  const end = Math.min(page.value * itemsPerPage.value, total)
  return `${start}-${end} sur ${total}`
})

const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value * itemsPerPage.value < totalFiltered.value)

const hasActiveFilters = computed(
  () => (searchQuery.value?.trim() ?? '') !== '' || filterModule.value != null,
)

function roleTagColor(code: string): string {
  const c = code.toLowerCase()
  if (c.includes('admin')) return 'primary'
  if (c.includes('manager') || c.includes('gestionnaire')) return 'warning'
  if (c.includes('support')) return 'info'
  if (c.includes('restrict') || c.includes('restreint')) return 'error'
  return 'secondary'
}

async function loadPermissions() {
  loading.value = true
  try {
    const data = await listPermissions({ limit: 200, include_roles: true })
    permissions.value = Array.isArray(data) ? data : []
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des permissions.')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  searchQuery.value = ''
  filterModule.value = null
  page.value = 1
}

onMounted(loadPermissions)

function openCreate() {
  formModalOpen.value = true
}

function openRoles(item: PermissionWithRolesResponse) {
  selectedPermissionId.value = item.id
  rolesModalOpen.value = true
}

function onFormSaved() {
  formModalOpen.value = false
  loadPermissions()
}

function onFormCancel() {
  formModalOpen.value = false
}

function onRolesUpdated() {
  loadPermissions()
}

function prevPage() {
  if (canPrev.value) page.value--
}

function nextPage() {
  if (canNext.value) page.value++
}
</script>

<template>
  <div class="permissions-page">
    <VCard class="permissions-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (module, action, libellé…)"
            density="compact"
            hide-details
            clearable
            class="permissions-search"
            style="min-width: 220px; max-width: 280px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VSelect
            v-model="filterModule"
            :items="[{ title: 'Tous les modules', value: null }, ...moduleOptions.map(m => ({ title: m, value: m }))]"
            item-title="title"
            item-value="value"
            label="Module"
            density="compact"
            hide-details
            clearable
            variant="outlined"
            style="width: 180px;"
            prepend-inner-icon="ri-folder-line"
          />
          <VBtn
            v-if="hasActiveFilters"
            variant="outlined"
            color="secondary"
            size="small"
            prepend-icon="ri-refresh-line"
            @click="resetFilters"
          >
            Réinitialiser
          </VBtn>
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">
            Ajouter 
          </VBtn>
        </div>

        <VDivider />

        <VTable class="permissions-table" :class="{ 'table-loading': loading }">
          <thead>
            <tr>
              <th
                v-for="h in headers"
                :key="h.key"
                :class="[
                  'text-left text-body-2 font-weight-bold text-medium-emphasis py-4 px-4',
                  h.align === 'end' && 'text-right',
                ]"
                :style="h.width ? { width: h.width } : undefined"
              >
                {{ h.title }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="headers.length" class="text-center py-8">
                <VProgressCircular indeterminate color="primary" size="32" />
              </td>
            </tr>
            <tr v-else-if="paginatedItems.length === 0">
              <td :colspan="headers.length" class="text-center py-8 text-medium-emphasis">
                Aucune permission trouvée.
              </td>
            </tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="permission-row">
              <td class="py-3 px-4">
                {{ item.module || '—' }}
              </td>
              <td class="py-3 px-4">
                <span class="text-body-2 font-weight-medium">{{ item.action || '—' }}</span>
              </td>
              <td class="py-3 px-4 text-body-2">
                {{ item.libelle || '—' }}
              </td>
              <td class="py-3 px-4">
                <div class="d-flex flex-wrap gap-1">
                  <VChip
                    v-for="role in (item.roles || [])"
                    :key="role.id"
                    size="small"
                    :color="roleTagColor(role.code)"
                    variant="tonal"
                    class="role-tag"
                  >
                    {{ role.libelle || role.code }}
                  </VChip>
                  <span v-if="!(item.roles && item.roles.length)" class="text-medium-emphasis text-body-2">
                    —
                  </span>
                </div>
              </td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props }">
                    <VBtn v-bind="props" size="small">
                      Options
                      <VIcon icon="ri-settings-4-line" class="ml-1" size="22" />
                    </VBtn>
                  </template>
                  <VList density="compact" min-width="180">
                    <VListItem
                      prepend-icon="ri-user-shared-line"
                      title="Gérer les rôles"
                      @click="openRoles(item)"
                    />
                  </VList>
                </VMenu>
              </td>
            </tr>
          </tbody>
        </VTable>

        <VDivider />

        <div class="d-flex flex-wrap align-center gap-4 pa-4">
          <div class="d-flex align-center gap-2">
            <span class="text-body-2 text-medium-emphasis">Lignes par page :</span>
            <VSelect
              :model-value="itemsPerPage"
              :items="itemsPerPageOptions"
              item-value="value"
              item-title="title"
              density="compact"
              hide-details
              variant="outlined"
              class="rows-select"
              style="width: 72px;"
              @update:model-value="(v: number) => { itemsPerPage = v; page = 1 }"
            />
          </div>
          <VSpacer />
          <span class="text-body-2 text-medium-emphasis">{{ pageRangeText }}</span>
          <div class="d-flex gap-1">
            <VBtn icon variant="text" size="small" :disabled="!canPrev" @click="prevPage">
              <VIcon icon="ri-arrow-left-s-line" />
            </VBtn>
            <VBtn icon variant="text" size="small" :disabled="!canNext" @click="nextPage">
              <VIcon icon="ri-arrow-right-s-line" />
            </VBtn>
          </div>
        </div>
      </VCardText>
    </VCard>

    <PermissionFormModal v-model="formModalOpen" @saved="onFormSaved" @cancel="onFormCancel" />

    <RolesPermissionModal
      v-model="rolesModalOpen"
      :permission="permissionForRolesModal"
      @updated="onRolesUpdated"
    />
  </div>
</template>

<style scoped>
.permissions-page {
  max-width: 100%;
}

.permissions-card {
  border-radius: 12px;
  overflow: hidden;
}

.permissions-table th {
  white-space: nowrap;
}

.permission-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.module-chip {
  font-size: 0.75rem;
  font-weight: 600;
}

.role-tag {
  font-size: 0.75rem;
}

.rows-select :deep(.v-field) {
  font-size: 0.875rem;
}
</style>
