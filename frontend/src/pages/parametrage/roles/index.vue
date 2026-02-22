<script setup lang="ts">
import { listRoles } from '@/api/parametrage'
import type { RoleResponse } from '@/api/types/parametrage'
import RoleFormModal from '@/components/parametrage/RoleFormModal.vue'
import PermissionsRoleModal from '@/components/parametrage/PermissionsRoleModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const toastStore = useToastStore()
const roles = ref<RoleResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const editingId = ref<number | null>(null)
const searchQuery = ref('')
const permissionsModalOpen = ref(false)
const roleForPermissions = ref<RoleResponse | null>(null)

const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)

const headers = [
  { title: 'CODE', key: 'code', sortable: true, width: 'min(140px, 18%)' },
  { title: 'LIBELLÉ', key: 'libelle', sortable: true },
  { title: 'TYPE', key: 'entreprise_id', width: '110px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '140px', align: 'end' as const },
]

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  const list = Array.isArray(roles.value) ? roles.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (!q) return list
  return list.filter(
    r =>
      (r.code && r.code.toLowerCase().includes(q)) ||
      (r.libelle && r.libelle.toLowerCase().includes(q)),
  )
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

async function loadRoles() {
  const eid = entrepriseId.value
  if (eid == null) {
    roles.value = []
    return
  }
  loading.value = true
  try {
    const data = await listRoles({ entreprise_id: eid, limit: 100 })
    roles.value = Array.isArray(data) ? data : []
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des rôles.')
  } finally {
    loading.value = false
  }
}

onMounted(loadRoles)
watch(entrepriseId, loadRoles)

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: RoleResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

function openPermissions(row: RoleResponse) {
  roleForPermissions.value = row
  permissionsModalOpen.value = true
}

function onPermissionsUpdated() {
  loadRoles()
}

function closePermissionsModal() {
  permissionsModalOpen.value = false
  roleForPermissions.value = null
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadRoles()
}

function onFormCancel() {
  formModalOpen.value = false
  editingId.value = null
}

function prevPage() {
  if (canPrev.value) page.value--
}

function nextPage() {
  if (canNext.value) page.value++
}
</script>

<template>
  <div class="roles-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12">
        <VAlert type="info" variant="tonal" class="rounded-lg">
          Aucune entreprise associée. Les rôles sont rattachés à une entreprise.
        </VAlert>
      </VCol>
    </VRow>

    <VCard v-else class="roles-card">
      <VCardText class="pa-0">
        <div class="d-flex flex-wrap align-center gap-4 pa-5 pb-4 w-100">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher un rôle (code ou libellé)"
            density="compact"
            hide-details
            clearable
            class="roles-search flex-grow-1"
            style="min-width: 200px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VBtn color="primary" prepend-icon="ri-add-line" class="add-role-btn flex-shrink-0" @click="openCreate">
            Ajouter
          </VBtn>
        </div>

        <VDivider />

        <VTable :class="{ 'table-loading': loading }">
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
                Aucun rôle trouvé.
              </td>
            </tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="role-row">
              <td class="py-3 px-4 font-weight-medium">
                <VChip size="small" color="primary" variant="tonal" class="code-chip">
                  {{ item.code }}
                </VChip>
              </td>
              <td class="py-3 px-4 text-body-2">
                {{ item.libelle || '—' }}
              </td>
              <td class="py-3 px-4">
                <VChip size="small" variant="tonal" :color="item.entreprise_id == null ? 'secondary' : 'default'">
                  {{ item.entreprise_id == null ? 'Système' : 'Entreprise' }}
                </VChip>
              </td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props }">
                    <VBtn v-bind="props" size="small">
                      Options
                      <VIcon icon="ri-settings-4-line" class="ml-1" size="22" />
                    </VBtn>
                  </template>
                  <VList density="compact" min-width="200">
                    <VListItem
                      prepend-icon="ri-pencil-line"
                      title="Modifier le rôle"
                      @click="openEdit(item)"
                    />
                    <VListItem
                      prepend-icon="ri-lock-2-line"
                      title="Gérer les permissions"
                      @click="openPermissions(item)"
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

    <RoleFormModal
      v-model="formModalOpen"
      :entreprise-id="entrepriseId ?? 0"
      :role-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />

    <PermissionsRoleModal
      v-model="permissionsModalOpen"
      :role="roleForPermissions"
      @close="closePermissionsModal"
      @updated="onPermissionsUpdated"
    />
  </div>
</template>

<style scoped>
.roles-page {
  max-width: 100%;
}

.roles-card {
  border-radius: 12px;
  overflow: hidden;
}

.roles-table-wrap {
  overflow: hidden;
}

.roles-table {
  border-collapse: collapse;
}

.roles-table :deep(thead th) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.roles-table th {
  white-space: nowrap;
}

.role-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.02);
}

.code-chip {
  font-size: 0.75rem;
  font-weight: 600;
}

.rows-select :deep(.v-field) {
  font-size: 0.875rem;
}
</style>
