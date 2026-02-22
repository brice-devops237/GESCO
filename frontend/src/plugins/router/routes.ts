export const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/',
    component: () => import('@/layouts/default.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/pages/dashboard.vue'),
      },
      {
        path: 'parametrage/entreprises',
        name: 'parametrage-entreprises',
        component: () => import('@/pages/parametrage/entreprises/index.vue'),
      },
      {
        path: 'parametrage/devises',
        name: 'parametrage-devises',
        component: () => import('@/pages/parametrage/devises/index.vue'),
      },
      {
        path: 'parametrage/taux-change',
        name: 'parametrage-taux-change',
        component: () => import('@/pages/parametrage/taux-change/index.vue'),
      },
      {
        path: 'parametrage/points-vente',
        name: 'parametrage-points-vente',
        component: () => import('@/pages/parametrage/points-vente/index.vue'),
      },
      {
        path: 'parametrage/roles',
        name: 'parametrage-roles',
        component: () => import('@/pages/parametrage/roles/index.vue'),
      },
      {
        path: 'parametrage/permissions',
        name: 'parametrage-permissions',
        component: () => import('@/pages/parametrage/permissions/index.vue'),
      },
      {
        path: 'parametrage/utilisateurs',
        name: 'parametrage-utilisateurs',
        component: () => import('@/pages/parametrage/utilisateurs/index.vue'),
      },
      {
        path: 'catalogue/unites-mesure',
        name: 'catalogue-unites-mesure',
        component: () => import('@/pages/catalogue/unites-mesure/index.vue'),
      },
      {
        path: 'catalogue/taux-tva',
        name: 'catalogue-taux-tva',
        component: () => import('@/pages/catalogue/taux-tva/index.vue'),
      },
      {
        path: 'catalogue/familles-produits',
        name: 'catalogue-familles-produits',
        component: () => import('@/pages/catalogue/familles-produits/index.vue'),
      },
      {
        path: 'catalogue/conditionnements',
        name: 'catalogue-conditionnements',
        component: () => import('@/pages/catalogue/conditionnements/index.vue'),
      },
      {
        path: 'catalogue/produits',
        name: 'catalogue-produits',
        component: () => import('@/pages/catalogue/produits/index.vue'),
      },
      {
        path: 'catalogue/canaux-vente',
        name: 'catalogue-canaux-vente',
        component: () => import('@/pages/catalogue/canaux-vente/index.vue'),
      },
      {
        path: 'partenaires/types-tiers',
        name: 'partenaires-types-tiers',
        component: () => import('@/pages/partenaires/types-tiers/index.vue'),
      },
      {
        path: 'partenaires/tiers',
        name: 'partenaires-tiers',
        component: () => import('@/pages/partenaires/tiers/index.vue'),
      },
      {
        path: 'partenaires/contacts',
        name: 'partenaires-contacts',
        component: () => import('@/pages/partenaires/contacts/index.vue'),
      },
      {
        path: 'achats/depots',
        name: 'achats-depots',
        component: () => import('@/pages/achats/depots/index.vue'),
      },
      {
        path: 'achats/commandes-fournisseurs',
        name: 'achats-commandes-fournisseurs',
        component: () => import('@/pages/achats/commandes-fournisseurs/index.vue'),
      },
      {
        path: 'achats/receptions',
        name: 'achats-receptions',
        component: () => import('@/pages/achats/receptions/index.vue'),
      },
      {
        path: 'achats/factures-fournisseurs',
        name: 'achats-factures-fournisseurs',
        component: () => import('@/pages/achats/factures-fournisseurs/index.vue'),
      },
      {
        path: 'tresorerie/modes-paiement',
        name: 'tresorerie-modes-paiement',
        component: () => import('@/pages/tresorerie/modes-paiement/index.vue'),
      },
      {
        path: 'tresorerie/comptes',
        name: 'tresorerie-comptes',
        component: () => import('@/pages/tresorerie/comptes/index.vue'),
      },
      {
        path: 'tresorerie/reglements',
        name: 'tresorerie-reglements',
        component: () => import('@/pages/tresorerie/reglements/index.vue'),
      },
      {
        path: 'comptabilite/comptes',
        name: 'comptabilite-comptes',
        component: () => import('@/pages/comptabilite/comptes/index.vue'),
      },
      {
        path: 'comptabilite/journaux',
        name: 'comptabilite-journaux',
        component: () => import('@/pages/comptabilite/journaux/index.vue'),
      },
      {
        path: 'comptabilite/periodes',
        name: 'comptabilite-periodes',
        component: () => import('@/pages/comptabilite/periodes/index.vue'),
      },
      {
        path: 'comptabilite/ecritures',
        name: 'comptabilite-ecritures',
        component: () => import('@/pages/comptabilite/ecritures/index.vue'),
      },
      {
        path: 'rh/departements',
        name: 'rh-departements',
        component: () => import('@/pages/rh/departements/index.vue'),
      },
      {
        path: 'rh/postes',
        name: 'rh-postes',
        component: () => import('@/pages/rh/postes/index.vue'),
      },
      {
        path: 'rh/employes',
        name: 'rh-employes',
        component: () => import('@/pages/rh/employes/index.vue'),
      },
      {
        path: 'paie/periodes',
        name: 'paie-periodes',
        component: () => import('@/pages/paie/periodes/index.vue'),
      },
      {
        path: 'paie/types-element',
        name: 'paie-types-element',
        component: () => import('@/pages/paie/types-element/index.vue'),
      },
      {
        path: 'paie/bulletins',
        name: 'paie-bulletins',
        component: () => import('@/pages/paie/bulletins/index.vue'),
      },
      {
        path: 'commercial/devis',
        name: 'commercial-devis',
        component: () => import('@/pages/commercial/devis/index.vue'),
      },
      {
        path: 'commercial/commandes',
        name: 'commercial-commandes',
        component: () => import('@/pages/commercial/commandes/index.vue'),
      },
      {
        path: 'commercial/factures',
        name: 'commercial-factures',
        component: () => import('@/pages/commercial/factures/index.vue'),
      },
      {
        path: 'commercial/bons-livraison',
        name: 'commercial-bons-livraison',
        component: () => import('@/pages/commercial/bons-livraison/index.vue'),
      },
      {
        path: 'stock/mouvements',
        name: 'stock-mouvements',
        component: () => import('@/pages/stock/mouvements/index.vue'),
      },
      {
        path: 'stock/alertes',
        name: 'stock-alertes',
        component: () => import('@/pages/stock/alertes/index.vue'),
      },
      {
        path: 'immobilisations/categories',
        name: 'immobilisations-categories',
        component: () => import('@/pages/immobilisations/categories/index.vue'),
      },
      {
        path: 'immobilisations/actifs',
        name: 'immobilisations-actifs',
        component: () => import('@/pages/immobilisations/actifs/index.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('@/layouts/blank.vue'),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/pages/login.vue'),
        meta: { unauthenticatedOnly: true },
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: () => import('@/pages/[...error].vue'),
        meta: { layout: 'blank' },
      },
    ],
  },
]
