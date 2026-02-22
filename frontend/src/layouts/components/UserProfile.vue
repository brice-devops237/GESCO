<script setup lang="ts">
import avatar1 from '@images/avatars/avatar-1.png'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const userInfo = computed(() => authStore.userInfo)

const displayLabel = computed(() => {
  const { user_id, entreprise_id } = userInfo.value
  if (entreprise_id != null && user_id != null)
    return `Compte #${user_id} · Entreprise #${entreprise_id}`
  if (user_id != null)
    return `Compte #${user_id}`
  return 'Compte'
})

function onLogout() {
  authStore.logout()
  // La redirection vers /login est gérée par le watcher dans default.vue
}
</script>

<template>
  <VBadge
    dot
    location="bottom right"
    offset-x="3"
    offset-y="3"
    color="success"
    bordered
  >
    <VAvatar
      class="cursor-pointer"
      color="primary"
      variant="tonal"
    >
      <VImg :src="avatar1" />

      <VMenu
        activator="parent"
        width="260"
        location="bottom end"
        offset="14px"
      >
        <VList>
          <VListItem>
            <template #prepend>
              <VListItemAction start>
                <VBadge
                  dot
                  location="bottom right"
                  offset-x="3"
                  offset-y="3"
                  color="success"
                >
                  <VAvatar
                    color="primary"
                    variant="tonal"
                  >
                    <VImg :src="avatar1" />
                  </VAvatar>
                </VBadge>
              </VListItemAction>
            </template>
            <VListItemTitle class="font-weight-semibold">
              {{ displayLabel }}
            </VListItemTitle>
            <VListItemSubtitle>Session Gesco</VListItemSubtitle>
          </VListItem>
          <VDivider class="my-2" />

          <VListItem link>
            <template #prepend>
              <VIcon
                class="me-2"
                icon="ri-user-line"
                size="22"
              />
            </template>
            <VListItemTitle>Profil</VListItemTitle>
          </VListItem>

          <VListItem link>
            <template #prepend>
              <VIcon
                class="me-2"
                icon="ri-settings-4-line"
                size="22"
              />
            </template>
            <VListItemTitle>Paramètres</VListItemTitle>
          </VListItem>

          <VDivider class="my-2" />

          <VListItem
            role="button"
            @click="onLogout"
          >
            <template #prepend>
              <VIcon
                class="me-2"
                icon="ri-logout-box-r-line"
                size="22"
              />
            </template>
            <VListItemTitle>Déconnexion</VListItemTitle>
          </VListItem>
        </VList>
      </VMenu>
    </VAvatar>
  </VBadge>
</template>
