<script lang="ts" setup>
import VerticalNavLink from '@layouts/components/VerticalNavLink.vue'
import VerticalNavGroup from '@layouts/components/VerticalNavGroup.vue'

// Paramétrage : structure → référentiels financiers → sécurité
const parametrageChildren = [
  { title: 'Entreprises', icon: 'ri-building-line', to: '/parametrage/entreprises' },
  { title: 'Points de vente', icon: 'ri-store-2-line', to: '/parametrage/points-vente' },
  { title: 'Devises', icon: 'ri-money-dollar-circle-line', to: '/parametrage/devises' },
  { title: 'Taux de change', icon: 'ri-exchange-line', to: '/parametrage/taux-change' },
  { title: 'Rôles', icon: 'ri-user-shared-line', to: '/parametrage/roles' },
  { title: 'Permissions', icon: 'ri-lock-2-line', to: '/parametrage/permissions' },
  { title: 'Utilisateurs', icon: 'ri-team-line', to: '/parametrage/utilisateurs' },
]

// Partenaires : types → tiers → contacts
const partenairesChildren = [
  { title: 'Types de tiers', icon: 'ri-bookmark-line', to: '/partenaires/types-tiers' },
  { title: 'Tiers', icon: 'ri-group-line', to: '/partenaires/tiers' },
  { title: 'Contacts', icon: 'ri-contacts-book-line', to: '/partenaires/contacts' },
]

// Catalogue : référentiels → produits → canaux
const catalogueChildren = [
  { title: 'Unités de mesure', icon: 'ri-ruler-line', to: '/catalogue/unites-mesure' },
  { title: 'Taux TVA', icon: 'ri-percent-line', to: '/catalogue/taux-tva' },
  { title: 'Familles produits', icon: 'ri-folder-open-line', to: '/catalogue/familles-produits' },
  { title: 'Conditionnements', icon: 'ri-inbox-line', to: '/catalogue/conditionnements' },
  { title: 'Produits', icon: 'ri-product-hunt-line', to: '/catalogue/produits' },
  { title: 'Canaux de vente', icon: 'ri-store-3-line', to: '/catalogue/canaux-vente' },
]

// Commercial : flux vente (devis → commande → livraison → facture)
const commercialChildren = [
  { title: 'Devis', icon: 'ri-file-list-3-line', to: '/commercial/devis' },
  { title: 'Commandes', icon: 'ri-shopping-cart-line', to: '/commercial/commandes' },
  { title: 'Bons de livraison', icon: 'ri-truck-line', to: '/commercial/bons-livraison' },
  { title: 'Factures', icon: 'ri-bill-line', to: '/commercial/factures' },
]

// Achats : flux achat (commandes → réceptions → factures), dépôts en premier
const achatsChildren = [
  { title: 'Dépôts', icon: 'ri-warehouse-line', to: '/achats/depots' },
  { title: 'Commandes fournisseurs', icon: 'ri-shopping-cart-2-line', to: '/achats/commandes-fournisseurs' },
  { title: 'Réceptions', icon: 'ri-truck-line', to: '/achats/receptions' },
  { title: 'Factures fournisseurs', icon: 'ri-bill-line', to: '/achats/factures-fournisseurs' },
]

// Stock
const stockChildren = [
  { title: 'Mouvements', icon: 'ri-arrow-left-right-line', to: '/stock/mouvements' },
  { title: 'Alertes', icon: 'ri-alarm-warning-line', to: '/stock/alertes' },
]

// Trésorerie : moyens → comptes → opérations
const tresorerieChildren = [
  { title: 'Modes de paiement', icon: 'ri-bank-card-line', to: '/tresorerie/modes-paiement' },
  { title: 'Comptes trésorerie', icon: 'ri-wallet-3-line', to: '/tresorerie/comptes' },
  { title: 'Règlements', icon: 'ri-money-dollar-circle-line', to: '/tresorerie/reglements' },
]

// Comptabilité : plan → journaux → périodes → écritures
const comptabiliteChildren = [
  { title: 'Comptes comptables', icon: 'ri-book-open-line', to: '/comptabilite/comptes' },
  { title: 'Journaux', icon: 'ri-file-list-2-line', to: '/comptabilite/journaux' },
  { title: 'Périodes', icon: 'ri-calendar-line', to: '/comptabilite/periodes' },
  { title: 'Écritures', icon: 'ri-file-edit-line', to: '/comptabilite/ecritures' },
]

// RH : structure → postes → employés
const rhChildren = [
  { title: 'Départements', icon: 'ri-building-4-line', to: '/rh/departements' },
  { title: 'Postes', icon: 'ri-briefcase-line', to: '/rh/postes' },
  { title: 'Employés', icon: 'ri-user-line', to: '/rh/employes' },
]

// Paie : paramétrage → bulletins
const paieChildren = [
  { title: 'Périodes', icon: 'ri-calendar-line', to: '/paie/periodes' },
  { title: "Types d'éléments", icon: 'ri-list-check-2', to: '/paie/types-element' },
  { title: 'Bulletins', icon: 'ri-file-text-line', to: '/paie/bulletins' },
]

// Immobilisations
const immobilisationsChildren = [
  { title: 'Catégories', icon: 'ri-folder-line', to: '/immobilisations/categories' },
  { title: 'Actifs', icon: 'ri-building-line', to: '/immobilisations/actifs' },
]
</script>

<template>
  <!-- Vue d'ensemble -->
  <VerticalNavLink
    :item="{
      title: 'Tableau de bord',
      icon: 'ri-dashboard-line',
      to: '/dashboard',
    }"
  />

  <!-- Fondations : structure et référentiels -->
  <VerticalNavGroup
    :item="{
      title: 'Paramétrage',
      icon: 'ri-settings-3-line',
    }"
  >
    <VerticalNavLink
      v-for="child in parametrageChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Interlocuteurs -->
  <VerticalNavGroup
    :item="{
      title: 'Partenaires',
      icon: 'ri-group-2-line',
    }"
  >
    <VerticalNavLink
      v-for="child in partenairesChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Offre produits -->
  <VerticalNavGroup
    :item="{
      title: 'Catalogue',
      icon: 'ri-archive-line',
    }"
  >
    <VerticalNavLink
      v-for="child in catalogueChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Cycle vente -->
  <VerticalNavGroup
    :item="{
      title: 'Commercial',
      icon: 'ri-file-list-3-line',
    }"
  >
    <VerticalNavLink
      v-for="child in commercialChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Cycle achat -->
  <VerticalNavGroup
    :item="{
      title: 'Achats',
      icon: 'ri-shopping-cart-2-line',
    }"
  >
    <VerticalNavLink
      v-for="child in achatsChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Inventaire -->
  <VerticalNavGroup
    :item="{
      title: 'Stock',
      icon: 'ri-box-3-line',
    }"
  >
    <VerticalNavLink
      v-for="child in stockChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Finance : trésorerie puis comptabilité -->
  <VerticalNavGroup
    :item="{
      title: 'Trésorerie',
      icon: 'ri-bank-line',
    }"
  >
    <VerticalNavLink
      v-for="child in tresorerieChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>
  <VerticalNavGroup
    :item="{
      title: 'Comptabilité',
      icon: 'ri-book-2-line',
    }"
  >
    <VerticalNavLink
      v-for="child in comptabiliteChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Ressources humaines et paie -->
  <VerticalNavGroup
    :item="{
      title: 'RH',
      icon: 'ri-user-star-line',
    }"
  >
    <VerticalNavLink
      v-for="child in rhChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>
  <VerticalNavGroup
    :item="{
      title: 'Paie',
      icon: 'ri-money-cny-circle-line',
    }"
  >
    <VerticalNavLink
      v-for="child in paieChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>

  <!-- Actifs -->
  <VerticalNavGroup
    :item="{
      title: 'Immobilisations',
      icon: 'ri-building-2-line',
    }"
  >
    <VerticalNavLink
      v-for="child in immobilisationsChildren"
      :key="child.to"
      :item="child"
    />
  </VerticalNavGroup>
</template>
