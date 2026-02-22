<script setup lang="ts">
import ToastSnackbar from '@/components/ToastSnackbar.vue'
</script>

<template>
  <VApp>
    <RouterView />
    <ToastSnackbar />
  </VApp>
</template>
