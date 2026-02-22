<script setup lang="ts">
import {
  listUtilisateurs,
  listRoles,
  deleteUtilisateur,
} from '@/api/parametrage'
import type { UtilisateurResponse, RoleResponse } from '@/api/types/parametrage'
import UtilisateurFormModal from '@/components/parametrage/UtilisateurFormModal.vue'
import AffectationsPdvModal from '@/components/parametrage/AffectationsPdvModal.vue'
import ChangerMotDePasseModal from '@/components/parametrage/ChangerMotDePasseModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const authStore = useAuthStore()
const toastStore = useToastStore()
const utilisateurs = ref<UtilisateurResponse[]>([])
const roles = ref<RoleResponse[]>([])
const loading = ref(false)
const formModalOpen = ref(false)
const affectationsModalOpen = ref(false)
const passwordModalOpen = ref(false)
const editingId = ref<number | null>(null)
const affectationsUserId = ref<number | null>(null)
const passwordUserId = ref<UtilisateurResponse | null>(null)
const searchQuery = ref('')
const filterRoleId = ref<number | null>(null)
const filterStatut = ref<'all' | 'actif' | 'inactif'>('all')

const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)

const roleMap = computed(() => {
  const m: Record<number, string> = {}
  for (const r of roles.value) {
    m[r.id] = r.libelle
  }
  return m
})

const headers = [
  { title: 'UTILISATEUR', key: 'user', sortable: false, width: 'min(220px, 22%)' },
  { title: 'EMAIL', key: 'email', width: 'min(180px, 18%)' },
  { title: 'TÉLÉPHONE', key: 'telephone', width: 'min(130px, 13%)' },
  { title: 'RÔLE', key: 'role_id', width: '120px' },
  { title: 'STATUT', key: 'actif', width: '100px' },
  { title: 'ACTIONS', key: 'actions', sortable: false, width: '72px', align: 'end' as const },
]

function userInitials(u: UtilisateurResponse): string {
  if (u.nom?.trim()) return (u.nom.trim()[0] + (u.prenom?.trim()?.[0] ?? '')).toUpperCase()
  if (u.prenom?.trim()) return u.prenom.trim().slice(0, 2).toUpperCase()
  if (u.login?.trim()) return u.login.trim().slice(0, 2).toUpperCase()
  return '?'
}

function userDisplayName(u: UtilisateurResponse): string {
  const parts = [u.nom, u.prenom].filter(Boolean)
  return parts.length ? parts.join(' ') : (u.login || '—')
}

const itemsPerPageOptions = [
  { value: 10, title: '10' },
  { value: 25, title: '25' },
  { value: 50, title: '50' },
]

const itemsPerPage = ref(10)
const page = ref(1)

const filteredItems = computed(() => {
  let list = Array.isArray(utilisateurs.value) ? utilisateurs.value : []
  const q = searchQuery.value?.trim().toLowerCase()
  if (q) {
    list = list.filter(
      u =>
        (u.login && u.login.toLowerCase().includes(q)) ||
        (u.nom && u.nom.toLowerCase().includes(q)) ||
        (u.prenom && u.prenom?.toLowerCase().includes(q)) ||
        (u.email && u.email.toLowerCase().includes(q)) ||
        (u.telephone && u.telephone.replace(/\s/g, '').includes(q)),
    )
  }
  if (filterRoleId.value != null) {
    list = list.filter(u => u.role_id === filterRoleId.value)
  }
  if (filterStatut.value === 'actif') list = list.filter(u => u.actif)
  if (filterStatut.value === 'inactif') list = list.filter(u => !u.actif)
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

const roleOptionsForFilter = computed(() => [
  { title: 'Tous les rôles', value: null as number | null },
  ...roles.value.map(r => ({ title: `${r.code} — ${r.libelle}`, value: r.id })),
])

function onFiltersChange() {
  page.value = 1
}

async function loadRoles() {
  const eid = entrepriseId.value
  if (eid == null) {
    roles.value = []
    return
  }
  try {
    roles.value = await listRoles({ entreprise_id: eid, limit: 100 })
  } catch {
    roles.value = []
  }
}

async function loadUtilisateurs() {
  const eid = entrepriseId.value
  if (eid == null) {
    utilisateurs.value = []
    return
  }
  loading.value = true
  try {
    utilisateurs.value = await listUtilisateurs(eid, {
      search: searchQuery.value || undefined,
      limit: 100,
    })
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement des utilisateurs.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRoles()
  loadUtilisateurs()
})
watch(entrepriseId, () => {
  loadRoles()
  loadUtilisateurs()
})
watch([searchQuery], () => {
  loadUtilisateurs()
  onFiltersChange()
})
watch([filterRoleId, filterStatut], onFiltersChange)

function openCreate() {
  editingId.value = null
  formModalOpen.value = true
}

function openEdit(row: UtilisateurResponse) {
  editingId.value = row.id
  formModalOpen.value = true
}

function openAffectations(row: UtilisateurResponse) {
  affectationsUserId.value = row.id
  affectationsModalOpen.value = true
}

function openPassword(row: UtilisateurResponse) {
  passwordUserId.value = row
  passwordModalOpen.value = true
}

async function openConfirmDelete(row: UtilisateurResponse) {
  const name = [row.nom, row.prenom].filter(Boolean).join(' ') || row.login
  const result = await Swal.fire({
    title: 'Êtes-vous sûr ?',
    html: `Voulez-vous vraiment désactiver l'utilisateur <br><strong>« ${name} »</strong><br><span class="text-caption">Il ne pourra plus se connecter.</span>`,
    showCancelButton: true,
    confirmButtonText: 'Désactiver',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
    cancelButtonColor: 'rgb(var(--v-theme-primary))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  try {
    await deleteUtilisateur(row.id)
    toastStore.success('Utilisateur désactivé.')
    await loadUtilisateurs()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la désactivation.')
  }
}

function onFormSaved() {
  formModalOpen.value = false
  editingId.value = null
  loadUtilisateurs()
}

function onFormCancel() {
  formModalOpen.value = false
  editingId.value = null
}

function onAffectationsClose() {
  affectationsModalOpen.value = false
  affectationsUserId.value = null
}

function onPasswordSaved() {
  passwordModalOpen.value = false
  passwordUserId.value = null
}

function prevPage() {
  if (canPrev.value) page.value--
}

function nextPage() {
  if (canNext.value) page.value++
}
</script>

<template>
  <div class="utilisateurs-page">
    <VRow v-if="entrepriseId == null">
      <VCol cols="12">
        <VAlert type="info" variant="tonal" class="rounded-lg">
          Aucune entreprise associée. Les utilisateurs sont rattachés à une entreprise.
        </VAlert>
      </VCol>
    </VRow>

    <VCard v-else class="utilisateurs-card">
      <VCardText class="pa-0">
        <div class="filters-bar d-flex flex-wrap align-center gap-3 pa-5 pb-4">
          <VTextField
            v-model="searchQuery"
            placeholder="Rechercher (username, nom, prénom, email, tél.)"
            density="compact"
            hide-details
            clearable
            class="utilisateurs-search"
            style="min-width: 220px; max-width: 320px;"
            prepend-inner-icon="ri-search-line"
            variant="outlined"
            bg-color="grey-lighten-5"
          />
          <VSelect
            v-model="filterRoleId"
            :items="roleOptionsForFilter"
            item-title="title"
            item-value="value"
            label="Rôle"
            density="compact"
            hide-details
            variant="outlined"
            style="min-width: 160px;"
            class="filter-select"
            prepend-inner-icon="ri-shield-user-line"
          />
          <VSelect
            v-model="filterStatut"
            :items="[
              { title: 'Tous', value: 'all' },
              { title: 'Actifs', value: 'actif' },
              { title: 'Inactifs', value: 'inactif' },
            ]"
            label="Statut"
            item-title="title"
            item-value="value"
            density="compact"
            hide-details
            variant="outlined"
            style="width: 120px;"
            class="filter-select"
            prepend-inner-icon="ri-toggle-line"
          />
          <VBtn color="primary" prepend-icon="ri-add-line" @click="openCreate">
            Ajouter
          </VBtn>
        </div>

        <VDivider />

        <VTable class="utilisateurs-table" :class="{ 'table-loading': loading }">
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
                Aucun utilisateur trouvé.
              </td>
            </tr>
            <tr v-else v-for="item in paginatedItems" :key="item.id" class="utilisateur-row">
              <td class="py-3 px-4">
                <div class="d-flex align-center gap-3">
                  <VAvatar
                    size="40"
                    color="primary"
                    variant="tonal"
                    class="utilisateur-avatar"
                  >
                    <span class="text-sm font-weight-medium">{{ userInitials(item) }}</span>
                  </VAvatar>
                  <div class="d-flex flex-column min-width-0">
                    <span class="font-weight-medium text-high-emphasis text-truncate">{{ userDisplayName(item) }}</span>
                    <small class="text-body-2 text-medium-emphasis text-truncate">{{ item.login }}</small>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-body-2 text-medium-emphasis">{{ item.email || '—' }}</td>
              <td class="py-3 px-4 text-body-2 text-medium-emphasis">{{ item.telephone ? item.telephone.replace(/\s/g, '') : '—' }}</td>
              <td class="py-3 px-4">
                <!-- <VChip size="small" variant="tonal" color="secondary" class="role-chip">
                </VChip> -->
                {{ roleMap[item.role_id] ?? item.role_id }}
              </td>
              <td class="py-3 px-4">
                <!-- <VChip
                  :color="item.actif ? 'success' : 'default'"
                  size="small"
                  variant="tonal"
                  class="statut-chip"
                >
                  
                </VChip> -->
                {{ item.actif ? 'actif' : 'inactif' }}
              </td>
              <td class="py-3 px-4 text-right">
                <VMenu location="bottom">
                  <template #activator="{ props }">
                    <VBtn v-bind="props" size="small">
                      Options
                      <VIcon icon="ri-settings-4-line" class="ml-1" size="22" />
                    </VBtn>
                  </template>

                  <VList density="compact" min-width="200">
                    <VListItem
                      prepend-icon="ri-store-2-line"
                      title="Affecter un PDV"
                      @click="openAffectations(item)"
                    />
                    <VListItem
                      prepend-icon="ri-lock-password-line"
                      title="Changer Password"
                      @click="openPassword(item)"
                    />
                    <VListItem
                      prepend-icon="ri-pencil-line"
                      title="Modifier utilisateur"
                      @click="openEdit(item)"
                    />
                    <VDivider class="my-1" />
                    <VListItem
                      prepend-icon="ri-delete-bin-line"
                      title="Désactiver utilisateur"
                      class="list-item-danger"
                      @click="openConfirmDelete(item)"
                    />
                  </VList>
                </VMenu>

                <!-- <VMenu location="bottom end" :close-on-content-click="true">
                  <template #activator="{ props: menuProps }">
                    <IconBtn
                      v-bind="menuProps"
                      size="small"
                      color="error"
                    >
                      <VIcon icon="ri-more-2-line" size="22" />
                    </IconBtn>
                  </template>
                  
                </VMenu> -->
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

    <UtilisateurFormModal
      v-model="formModalOpen"
      :entreprise-id="entrepriseId ?? 0"
      :utilisateur-id="editingId"
      @saved="onFormSaved"
      @cancel="onFormCancel"
    />

    <AffectationsPdvModal
      v-model="affectationsModalOpen"
      :utilisateur-id="affectationsUserId ?? 0"
      :entreprise-id="entrepriseId ?? 0"
      @close="onAffectationsClose"
    />

    <ChangerMotDePasseModal
      v-model="passwordModalOpen"
      :utilisateur="passwordUserId"
      @saved="onPasswordSaved"
    />
  </div>
</template>

<style scoped>
.utilisateurs-page {
  max-width: 100%;
}

.utilisateurs-card {
  border-radius: 12px;
  overflow: hidden;
}

.utilisateurs-table th {
  white-space: nowrap;
}

.utilisateur-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.utilisateur-avatar {
  flex-shrink: 0;
}

.utilisateur-avatar span {
  font-size: 0.875rem;
}

.role-chip,
.statut-chip {
  font-size: 0.8125rem;
}

.actions-menu-btn {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.actions-menu-btn:hover {
  color: rgb(var(--v-theme-on-surface));
}

.rows-select :deep(.v-field) {
  font-size: 0.875rem;
}

/* Menu actions : item Désactiver en rouge */
.list-item-danger :deep(.v-list-item-title),
.list-item-danger :deep(.v-icon) {
  color: rgb(var(--v-theme-error)) !important;
}
</style>
