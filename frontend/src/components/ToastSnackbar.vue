<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import type { ToastType } from '@/stores/toast'

const toastStore = useToastStore()

const snackbarColor = computed(() => {
  const map: Record<ToastType, string> = {
    success: 'success',
    error: 'error',
    info: 'info',
    warning: 'warning',
  }
  return map[toastStore.type] ?? 'info'
})

function onClose() {
  toastStore.hide()
}
</script>

<template>
  <VSnackbar
    :model-value="toastStore.visible"
    :color="snackbarColor"
    :timeout="toastStore.timeout"
    location="top right"
    multi-line
    @update:model-value="(v: boolean) => !v && onClose()"
  >
    {{ toastStore.message }}
    <template #actions>
      <VBtn
        icon
        variant="text"
        size="small"
        color="white"
        @click="onClose"
      >
        <VIcon icon="ri-close-line" />
      </VBtn>
    </template>
  </VSnackbar>
</template>
