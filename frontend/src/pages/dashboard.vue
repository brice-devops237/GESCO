<script setup lang="ts">
import { getDashboard } from '@/api/rapports'
import type { SyntheseDashboard } from '@/api/types/rapports'
import { useAuthStore } from '@/stores/auth'
import { getApiErrorMessage } from '@/utils/apiErrors'

const authStore = useAuthStore()
const entrepriseId = computed(() => authStore.userInfo?.entreprise_id ?? null)
const dashboard = ref<SyntheseDashboard | null>(null)
const dashboardLoading = ref(false)
const dashboardError = ref<string | null>(null)

async function loadDashboard() {
  const eid = entrepriseId.value
  if (eid == null) { dashboard.value = null; return }
  dashboardLoading.value = true
  dashboardError.value = null
  try {
    dashboard.value = await getDashboard({ entreprise_id: eid })
  } catch (err) {
    dashboardError.value = getApiErrorMessage(err) ?? 'Erreur chargement indicateurs'
    dashboard.value = null
  } finally {
    dashboardLoading.value = false
  }
}

onMounted(() => loadDashboard())
watch(entrepriseId, () => loadDashboard())

function formatMontant(val: string | undefined): string {
  if (val == null || val === '') return '0'
  const n = Number(val)
  if (Number.isNaN(n)) return val
  return new Intl.NumberFormat('fr-FR', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(n)
}

const quickLinks = [
  { title: 'Entreprises', to: '/parametrage/entreprises', icon: 'ri-building-line', color: 'primary', description: 'Gérer les entreprises' },
  { title: 'Devises', to: '/parametrage/devises', icon: 'ri-money-dollar-circle-line', color: 'success', description: 'Référentiel devises' },
  { title: 'Taux de change', to: '/parametrage/taux-change', icon: 'ri-exchange-line', color: 'info', description: 'Taux entre devises' },
  { title: 'Points de vente', to: '/parametrage/points-vente', icon: 'ri-store-2-line', color: 'warning', description: 'PDV par entreprise' },
  { title: 'Rôles', to: '/parametrage/roles', icon: 'ri-user-shared-line', color: 'secondary', description: 'Rôles par entreprise' },
  { title: 'Permissions', to: '/parametrage/permissions', icon: 'ri-lock-2-line', color: 'error', description: 'Référentiel permissions' },
  { title: 'Utilisateurs', to: '/parametrage/utilisateurs', icon: 'ri-team-line', color: 'primary', description: 'Utilisateurs et affectations PDV' },
  { title: 'Unités de mesure', to: '/catalogue/unites-mesure', icon: 'ri-ruler-line', color: 'success', description: 'Référentiel unités' },
  { title: 'Taux TVA', to: '/catalogue/taux-tva', icon: 'ri-percent-line', color: 'info', description: 'Taux de TVA' },
  { title: 'Familles produits', to: '/catalogue/familles-produits', icon: 'ri-folder-open-line', color: 'warning', description: 'Familles et sous-familles' },
  { title: 'Conditionnements', to: '/catalogue/conditionnements', icon: 'ri-inbox-line', color: 'secondary', description: 'Conditionnements par entreprise' },
  { title: 'Produits', to: '/catalogue/produits', icon: 'ri-product-hunt-line', color: 'primary', description: 'Catalogue produits' },
  { title: 'Canaux de vente', to: '/catalogue/canaux-vente', icon: 'ri-store-3-line', color: 'error', description: 'Canaux par entreprise' },
  { title: 'Types de tiers', to: '/partenaires/types-tiers', icon: 'ri-bookmark-line', color: 'primary', description: 'Client, fournisseur…' },
  { title: 'Tiers', to: '/partenaires/tiers', icon: 'ri-group-line', color: 'success', description: 'Clients et fournisseurs' },
  { title: 'Contacts', to: '/partenaires/contacts', icon: 'ri-contacts-book-line', color: 'info', description: 'Contacts des tiers' },
  { title: 'Dépôts', to: '/achats/depots', icon: 'ri-warehouse-line', color: 'warning', description: 'Entrepôts par entreprise' },
]
</script>

<template>
  <div class="dashboard-page">
    <div class="mb-6">
      <h4 class="text-h4 font-weight-medium mb-1">
        Tableau de bord
      </h4>
      <p class="text-body-1 text-medium-emphasis mb-0">
        Bienvenue sur Gesco. Accédez aux modules depuis le menu ou les raccourcis ci-dessous.
      </p>
    </div>

    <!-- Indicateurs synthèse (entreprise connectée) -->
    <VRow v-if="entrepriseId != null" class="mb-6">
      <VCol v-if="dashboardLoading" cols="12" class="d-flex justify-center py-4">
        <VProgressCircular indeterminate color="primary" size="32" />
      </VCol>
      <VCol v-else-if="dashboardError" cols="12">
        <VAlert type="warning" variant="tonal" density="compact" class="rounded-lg">
          {{ dashboardError }}
        </VAlert>
      </VCol>
      <template v-else-if="dashboard">
        <VCol cols="12" sm="6" md="3">
          <VCard variant="tonal" color="primary" class="dashboard-stat-card" rounded="lg">
            <VCardText class="d-flex align-center pa-4">
              <VAvatar color="primary" variant="flat" size="48" class="me-3">
                <VIcon icon="ri-money-euro-circle-line" size="28" />
              </VAvatar>
              <div>
                <span class="text-caption text-medium-emphasis d-block">Chiffre d'affaires</span>
                <span class="text-h6 font-weight-medium">{{ formatMontant(dashboard.ca_periode) }} XAF</span>
                <span v-if="dashboard.periode_label" class="text-caption d-block">{{ dashboard.periode_label }}</span>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="6" md="3">
          <VCard variant="tonal" color="success" class="dashboard-stat-card" rounded="lg">
            <VCardText class="d-flex align-center pa-4">
              <VAvatar color="success" variant="flat" size="48" class="me-3">
                <VIcon icon="ri-file-list-3-line" size="28" />
              </VAvatar>
              <div>
                <span class="text-caption text-medium-emphasis d-block">Factures</span>
                <span class="text-h6 font-weight-medium">{{ dashboard.nb_factures ?? 0 }}</span>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="6" md="3">
          <VCard variant="tonal" color="info" class="dashboard-stat-card" rounded="lg">
            <VCardText class="d-flex align-center pa-4">
              <VAvatar color="info" variant="flat" size="48" class="me-3">
                <VIcon icon="ri-shopping-cart-line" size="28" />
              </VAvatar>
              <div>
                <span class="text-caption text-medium-emphasis d-block">Commandes</span>
                <span class="text-h6 font-weight-medium">{{ dashboard.nb_commandes ?? 0 }}</span>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="6" md="3">
          <VCard variant="tonal" color="warning" class="dashboard-stat-card" rounded="lg">
            <VCardText class="d-flex align-center pa-4">
              <VAvatar color="warning" variant="flat" size="48" class="me-3">
                <VIcon icon="ri-team-line" size="28" />
              </VAvatar>
              <div>
                <span class="text-caption text-medium-emphasis d-block">Employés actifs</span>
                <span class="text-h6 font-weight-medium">{{ dashboard.nb_employes_actifs ?? 0 }}</span>
              </div>
            </VCardText>
          </VCard>
        </VCol>
      </template>
    </VRow>

    <VRow class="quick-links-row">
      <VCol
        v-for="link in quickLinks"
        :key="link.to"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <VCard
          :to="link.to"
          class="dashboard-card fill-height"
          hover
          rounded="lg"
        >
          <VCardText class="d-flex align-center pa-5">
            <VAvatar
              size="48"
              rounded="lg"
              :color="link.color"
              variant="tonal"
              class="me-4 flex-shrink-0"
            >
              <VIcon
                :icon="link.icon"
                size="26"
              />
            </VAvatar>
            <div class="flex-grow-1 min-w-0">
              <span class="text-subtitle-1 font-weight-medium d-block">
                {{ link.title }}
              </span>
              <span class="text-caption text-medium-emphasis text-truncate d-block">
                {{ link.description }}
              </span>
            </div>
            <VIcon
              icon="ri-arrow-right-s-line"
              size="22"
              class="text-medium-emphasis flex-shrink-0"
            />
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </div>
</template>

<style scoped>
.dashboard-page {
  max-width: 100%;
}

.dashboard-card {
  border-radius: 12px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.dashboard-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.dashboard-stat-card {
  height: 100%;
}
</style>
