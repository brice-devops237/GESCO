<script setup lang="ts">
export interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  color?: 'primary' | 'error' | 'warning'
  persistent?: boolean
}

const visible = defineModel<boolean>({ default: false })

const props = withDefaults(
  defineProps<ConfirmOptions>(),
  {
    confirmText: 'Confirmer',
    cancelText: 'Annuler',
    color: 'primary',
    persistent: true,
  },
)

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

function onConfirm() {
  emit('confirm')
  visible.value = false
}

function onCancel() {
  emit('cancel')
  visible.value = false
}
</script>

<template>
  <VDialog
    :model-value="visible"
    :persistent="persistent"
    max-width="420"
    content-class="text-center"
    @update:model-value="(v: boolean) => !v && onCancel()"
  >
    <VCard class="pa-6">
      <VCardTitle class="text-h6 font-weight-medium">
        {{ title }}
      </VCardTitle>
      <VCardText class="pt-2 pb-4 text-body-2 text-medium-emphasis">
        {{ message }}
      </VCardText>
      <VCardActions class="pt-0 justify-center gap-2">
        <VBtn
          variant="tonal"
          color="secondary"
          @click="onCancel"
        >
          {{ cancelText }}
        </VBtn>
        <VBtn
          :color="color"
          @click="onConfirm"
        >
          {{ confirmText }}
        </VBtn>
      </VCardActions>
    </VCard>
  </VDialog>
</template>
