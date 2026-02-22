<script lang="ts" setup>
import DefaultLayoutWithVerticalNav from './components/DefaultLayoutWithVerticalNav.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

watch(
  () => authStore.isAuthenticated,
  (authenticated) => {
    if (!authenticated)
      router.replace({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  },
)
</script>

<template>
  <DefaultLayoutWithVerticalNav>
    <RouterView />
  </DefaultLayoutWithVerticalNav>
</template>

<style lang="scss">
// As we are using `layouts` plugin we need its styles to be imported
@use "@layouts/styles/default-layout";
</style>
