<script setup lang="ts">
  import { onMounted } from 'vue'
  import { useTheme } from 'vuetify'

  import logo from '@images/logo.svg?raw'
  import authV1MaskDark from '@images/pages/auth-v1-mask-dark.png'
  import authV1MaskLight from '@images/pages/auth-v1-mask-light.png'
  import authV1Tree2 from '@images/pages/auth-v1-tree-2.png'
  import authV1Tree from '@images/pages/auth-v1-tree.png'
  import { getLoginEntreprises } from '@/api/auth'
  import { useAuthStore } from '@/stores/auth'
  import { useToastStore } from '@/stores/toast'
  import { getApiErrorMessage } from '@/utils/apiErrors'

  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const toastStore = useToastStore()

  const entreprises = ref([])
  const loadingEntreprises = ref(false)

  const form = ref({
    entreprise_id: null,
    login: '',
    password: '',
    remember: false,
  })

  onMounted(async () => {
    loadingEntreprises.value = true
    try {
      entreprises.value = await getLoginEntreprises()
      if (entreprises.value.length === 1)
        form.value.entreprise_id = entreprises.value[0].id
    }
    catch (err) {
      const msg = getApiErrorMessage(err)
      toastStore.error(msg || 'Impossible de charger la liste des entreprises. Vérifiez que le backend est démarré (port 9111).')
    }
    finally {
      loadingEntreprises.value = false
    }
  })

  const vuetifyTheme = useTheme()

  const authThemeMask = computed(() => {
    return vuetifyTheme.global.name.value === 'light'
      ? authV1MaskLight
      : authV1MaskDark
  })

  const isPasswordVisible = ref(false)
  const loading = ref(false)

  async function onSubmit() {
    const entrepriseId = form.value.entreprise_id
    if (entrepriseId == null) {
      toastStore.error('Veuillez sélectionner une entreprise.')
      return
    }
    loading.value = true
    try {
      await authStore.login({
        entreprise_id: Number(entrepriseId),
        login: form.value.login.trim(),
        password: form.value.password,
        remember: form.value.remember,
      })
      toastStore.success('Connexion réussie.')
      const redirect = String(route.query.redirect || '/dashboard')
      await router.replace(redirect.startsWith('/') ? redirect : '/dashboard')
    }
    catch (err) {
      toastStore.error(getApiErrorMessage(err))
    }
    finally {
      loading.value = false
    }
  }
</script>

<template>
  <!-- eslint-disable vue/no-v-html -->
  <div class="auth-wrapper d-flex align-center justify-center pa-4">
    <VCard class="auth-card pa-4 pt-7" max-width="400">
      <VCardText class="pt-2 text-center">
        <h4 class="text-h4 mb-1">
          Bienvenue 👋
        </h4>
        <p class="mb-0">
          Connectez-vous à votre compte.
        </p>
      </VCardText>

      <VCardText>
        <VForm @submit.prevent="onSubmit">
          <VRow>
            <VCol cols="12">
              <VAutocomplete v-model="form.entreprise_id" :items="entreprises" item-title="raison_sociale"
                item-value="id" label="Entreprise" placeholder="Choisir une entreprise" :loading="loadingEntreprises"
                clearable prepend-inner-icon="ri-building-line" variant="outlined" density="comfortable" required />
            </VCol>

            <VCol cols="12">
              <VTextField v-model="form.login" label="Identifiant" placeholder="Votre identifiant"
                autocomplete="username" prepend-inner-icon="ri-user-line" variant="outlined" density="comfortable"
                required />
            </VCol>

            <VCol cols="12">
              <VTextField v-model="form.password" label="Mot de passe" placeholder="············"
                :type="isPasswordVisible ? 'text' : 'password'" autocomplete="current-password"
                prepend-inner-icon="ri-lock-line"
                :append-inner-icon="isPasswordVisible ? 'ri-eye-off-line' : 'ri-eye-line'" variant="outlined"
                density="comfortable" required @click:append-inner="isPasswordVisible = !isPasswordVisible" />

              <VBtn class="mt-4" block type="submit" :loading="loading">
                Connexion
              </VBtn>
            </VCol>
          </VRow>
        </VForm>
      </VCardText>
    </VCard>

    <VImg class="auth-footer-start-tree d-none d-md-block" :src="authV1Tree" :width="250" />

    <VImg :src="authV1Tree2" class="auth-footer-end-tree d-none d-md-block" :width="350" />

    <VImg class="auth-footer-mask d-none d-md-block" :src="authThemeMask" />
  </div>
</template>

<style lang="scss">
  @use "@core/scss/template/pages/page-auth";
</style>