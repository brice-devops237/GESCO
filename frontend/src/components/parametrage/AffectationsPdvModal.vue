<script setup lang="ts">
import {
  listAffectationsByUtilisateur,
  createAffectationPdv,
  deleteAffectationPdv,
  listPointsVente,
} from '@/api/parametrage'
import type {
  AffectationUtilisateurPdvResponse,
  PointDeVenteResponse,
} from '@/api/types/parametrage'
import { useToastStore } from '@/stores/toast'
import { getApiErrorMessage } from '@/utils/apiErrors'
import Swal from 'sweetalert2'

const props = defineProps<{
  utilisateurId: number
  entrepriseId: number
}>()

const visible = defineModel<boolean>({ default: false })
const emit = defineEmits<{ close: [] }>()

const toastStore = useToastStore()
const affectations = ref<AffectationUtilisateurPdvResponse[]>([])
const pointsVente = ref<PointDeVenteResponse[]>([])
const loading = ref(false)
const adding = ref(false)
const selectedPdvId = ref<number | null>(null)

const pointsList = computed(() => Array.isArray(pointsVente.value) ? pointsVente.value : [])

const pdvOptions = computed(() => {
  const assignedIds = affectations.value.map(a => a.point_de_vente_id)
  return pointsList.value
    .filter(p => !assignedIds.includes(p.id))
    .map(p => ({ title: `${p.code} - ${p.libelle}`, value: p.id }))
})

const pdvLabel = (pointDeVenteId: number) =>
  pointsList.value.find(p => p.id === pointDeVenteId)?.libelle ?? String(pointDeVenteId)

async function load() {
  if (!props.utilisateurId) return
  loading.value = true
  try {
    const [aff, pdvRes] = await Promise.all([
      listAffectationsByUtilisateur(props.utilisateurId),
      listPointsVente(props.entrepriseId, { limit: 100 }),
    ])
    affectations.value = aff
    pointsVente.value = pdvRes.items ?? []
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors du chargement.')
  } finally {
    loading.value = false
  }
}

watch(visible, (open) => {
  if (open) {
    load()
    selectedPdvId.value = null
  }
})

async function onAdd() {
  if (!selectedPdvId.value) return
  const pdv = pointsList.value.find(p => p.id === selectedPdvId.value)
  const pdvName = pdv ? `${pdv.code} - ${pdv.libelle}` : String(selectedPdvId.value)
  const result = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: `Souhaitez vous réellement ajouter le point de vente <br><strong>« ${pdvName} »</strong><br> aux affectations de cet utilisateur ?`,
    showCancelButton: true,
    confirmButtonText: 'Ajouter',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-primary))',
    cancelButtonColor: 'rgb(var(--v-theme-error))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  adding.value = true
  try {
    await createAffectationPdv({
      utilisateur_id: props.utilisateurId,
      point_de_vente_id: selectedPdvId.value,
      est_principal: affectations.value.length === 0,
    })
    toastStore.success('Affectation ajoutée.')
    selectedPdvId.value = null
    await load()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de l\'ajout.')
  } finally {
    adding.value = false
  }
}

function onClose() {
  visible.value = false
  emit('close')
}

async function openConfirmDelete(row: AffectationUtilisateurPdvResponse) {
  const label = pdvLabel(row.point_de_vente_id)
  const result = await Swal.fire({
    title: 'Êtes vous sûres?',
    html: `Souhaitez vous réellement retirer le point de vente <br><strong>« ${label} »</strong><br> des affectations de cet utilisateur ?`,
    showCancelButton: true,
    confirmButtonText: 'Retirer',
    cancelButtonText: 'Annuler',
    confirmButtonColor: 'rgb(var(--v-theme-error))',
    cancelButtonColor: 'rgb(var(--v-theme-primary))',
    customClass: { container: 'swal-above-modal' },
    allowOutsideClick: false,
    allowEscapeKey: false,
  })
  if (!result.isConfirmed) return
  try {
    await deleteAffectationPdv(row.id)
    toastStore.success('Affectation supprimée.')
    await load()
  } catch (err) {
    toastStore.error(getApiErrorMessage(err) ?? 'Erreur lors de la suppression.')
  }
}
</script>

<template>
  <VDialog
    :model-value="visible"
    max-width="560"
    persistent
    content-class="affect-pdv-modal-dialog"
    transition="dialog-transition"
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    <VCard class="affect-pdv-modal-card overflow-hidden">
      <div class="affect-pdv-modal-header">
        <div class="affect-pdv-modal-header-content">
          <div class="affect-pdv-modal-icon-wrap">
            <VIcon icon="ri-store-2-line" size="50" />
          </div>
          <div class="affect-pdv-modal-title-wrap">
            <h2 class="affect-pdv-modal-title">Affectations points de vente</h2>
            <p class="affect-pdv-modal-subtitle">
              Gérer les points de vente accessibles pour cet utilisateur.
            </p>
          </div>
        </div>
        <VBtn icon variant="text"  size="small" class="affect-pdv-modal-close" @click="onClose">
          <VIcon icon="ri-close-line" size="22" color="secondary" />
        </VBtn>
      </div>

      <div v-if="loading" class="affect-pdv-modal-loading">
        <VProgressCircular indeterminate color="primary" size="48" />
        <span class="text-body-2 mt-2">Chargement…</span>
      </div>

      <VCardText v-else class="affect-pdv-modal-body">
        <div class="d-flex align-center gap-2 mt-2 mb-4 flex-wrap">
          <VAutocomplete
            v-model="selectedPdvId"
            :items="pdvOptions"
            item-title="title"
            item-value="value"
            placeholder="Ajouter un point de vente…"
            density="compact"
            hide-details
            variant="outlined"
            class="affect-pdv-select"
            style="min-width: 260px; max-width: 100%;"
            prepend-inner-icon="ri-add-circle-line"
          />
          <VBtn
            color="primary"
            variant="flat"
            :disabled="!selectedPdvId || adding"
            :loading="adding"
            prepend-icon="ri-add-line"
            @click="onAdd"
          >
            Ajouter
          </VBtn>
        </div>

        <div v-if="affectations.length > 0" class="affect-pdv-table-wrap">
          <VTable class="affect-pdv-table" density="comfortable">
            <thead>
              <tr>
                <th class="text-left text-body-2 font-weight-bold">Point de vente</th>
                <th class="text-left text-body-2 font-weight-bold" style="width: 100px;">Principal</th>
                <th class="text-right text-body-2 font-weight-bold" style="width: 80px;">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in affectations" :key="a.id" class="affect-pdv-row">
                <td class="text-body-2">{{ pdvLabel(a.point_de_vente_id) }}</td>
                <td>
                  <VChip v-if="a.est_principal" size="small" color="primary" variant="tonal">
                    Oui
                  </VChip>
                  <span v-else class="text-medium-emphasis text-body-2">—</span>
                </td>
                <td class="text-right">
                  <VTooltip location="top" open-delay="400">
                    <template #activator="{ props: tooltipProps }">
                      <VBtn
                        v-bind="tooltipProps"
                        icon
                        variant="text"
                        size="small"
                        color="error"
                        density="comfortable"
                        @click="openConfirmDelete(a)"
                      >
                        <VIcon icon="ri-delete-bin-line" size="20" />
                      </VBtn>
                    </template>
                    <span>Retirer</span>
                  </VTooltip>
                </td>
              </tr>
            </tbody>
          </VTable>
        </div>
        <p v-else class="text-body-2 text-medium-emphasis py-4">
          Aucune affectation. Ajoutez un point de vente ci-dessus.
        </p>
      </VCardText>
    </VCard>
  </VDialog>
</template>

<style scoped>
.affect-pdv-modal-dialog :deep(.v-overlay__content) {
  align-items: center;
  justify-content: center;
}

.affect-pdv-modal-card {
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.08);
  position: relative;
}

.affect-pdv-modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 24px 20px;
}

.affect-pdv-modal-header-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.affect-pdv-modal-icon-wrap {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.affect-pdv-modal-title-wrap {
  min-width: 0;
}

.affect-pdv-modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.affect-pdv-modal-subtitle {
  font-size: 0.8125rem;
  opacity: 0.9;
  margin: 4px 0 0;
  line-height: 1.4;
}

.affect-pdv-modal-close {
  color: rgba(255, 255, 255, 0.9) !important;
  flex-shrink: 0;
}

.affect-pdv-modal-close:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
}

.affect-pdv-modal-loading {
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.affect-pdv-modal-body {
  padding: 24px 24px 28px;
}

.affect-pdv-select :deep(.v-field) {
  border-radius: 10px;
}

.affect-pdv-table-wrap {
  overflow: hidden;
}

.affect-pdv-table {
  font-size: 0.875rem;
  border-collapse: collapse;
}

.affect-pdv-table :deep(thead th) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.affect-pdv-row:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}
</style>
