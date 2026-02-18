# Modules et fonctionnalités Gesco — classement par ordre

Les modules sont listés par **ordre de priorité** (P0 → P5). Pour chaque module, les **fonctionnalités** (ressources) et leurs **opérations** sont listées dans l’ordre logique : liste → détail → création → mise à jour → suppression (et actions spécifiques).

Préfixe API : `/api/v1`.

---

## P0 — Fondation

### 1. Auth (`/auth`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Connexion** | POST `/auth/login` — Connexion (entreprise, login, mot de passe) → JWT + refresh token |
| **Rafraîchissement token** | POST `/auth/refresh` — Échanger un refresh_token contre de nouveaux tokens |

---

### 2. Paramétrage (`/parametrage`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Entreprises** | GET `/parametrage/entreprises` — Liste paginée ; GET `/parametrage/entreprises/{id}` — Détail ; POST `/parametrage/entreprises` — Création ; PATCH `/parametrage/entreprises/{id}` — Mise à jour ; DELETE `/parametrage/entreprises/{id}` — Soft delete |
| **Devises** | GET `/parametrage/devises` — Liste ; GET `/parametrage/devises/{id}` — Détail ; POST `/parametrage/devises` — Création ; PATCH `/parametrage/devises/{id}` — Mise à jour |
| **Taux de change** | GET `/parametrage/taux-change` — Liste (filtres devises) ; GET `/parametrage/taux-change/{id}` — Détail ; POST `/parametrage/taux-change` — Création |
| **Points de vente** | GET `/parametrage/entreprises/{id}/points-vente` — Liste par entreprise ; GET `/parametrage/points-vente/{id}` — Détail ; POST `/parametrage/points-vente` — Création ; PATCH `/parametrage/points-vente/{id}` — Mise à jour |
| **Rôles** | GET `/parametrage/roles` — Liste ; GET `/parametrage/roles/{id}` — Détail ; POST `/parametrage/roles` — Création ; PATCH `/parametrage/roles/{id}` — Mise à jour |
| **Permissions** | GET `/parametrage/permissions` — Liste ; GET `/parametrage/permissions/{id}` — Détail ; POST `/parametrage/permissions` — Création ; POST `/parametrage/permissions-roles` — Associer permission à un rôle ; DELETE `/parametrage/permissions-roles/{role_id}/{permission_id}` — Retirer permission d’un rôle |
| **Utilisateurs** | GET `/parametrage/entreprises/{id}/utilisateurs` — Liste par entreprise ; GET `/parametrage/utilisateurs/{id}` — Détail ; POST `/parametrage/utilisateurs` — Création ; PATCH `/parametrage/utilisateurs/{id}` — Mise à jour |
| **Affectations utilisateur–PDV** | GET `/parametrage/utilisateurs/{id}/affectations-pdv` — Liste par utilisateur ; GET `/parametrage/points-vente/{id}/affectations` — Liste par point de vente ; POST `/parametrage/affectations-utilisateur-pdv` — Création ; PATCH `/parametrage/affectations-utilisateur-pdv/{id}` — Mise à jour ; DELETE `/parametrage/affectations-utilisateur-pdv/{id}` — Suppression |

---

## P1 — Données de base

### 3. Catalogue (`/catalogue`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Unités de mesure** | GET `/catalogue/unites-mesure` — Liste ; GET `/catalogue/unites-mesure/{id}` — Détail ; POST `/catalogue/unites-mesure` — Création ; PATCH `/catalogue/unites-mesure/{id}` — Mise à jour |
| **Taux TVA** | GET `/catalogue/taux-tva` — Liste ; GET `/catalogue/taux-tva/{id}` — Détail ; POST `/catalogue/taux-tva` — Création ; PATCH `/catalogue/taux-tva/{id}` — Mise à jour |
| **Familles de produits** | GET `/catalogue/familles-produits` — Liste ; GET `/catalogue/familles-produits/{id}` — Détail ; POST `/catalogue/familles-produits` — Création ; PATCH `/catalogue/familles-produits/{id}` — Mise à jour ; DELETE `/catalogue/familles-produits/{id}` — Soft delete |
| **Conditionnements** | GET `/catalogue/conditionnements` — Liste ; GET `/catalogue/conditionnements/{id}` — Détail ; POST `/catalogue/conditionnements` — Création ; PATCH `/catalogue/conditionnements/{id}` — Mise à jour |
| **Produits** | GET `/catalogue/produits` — Liste ; GET `/catalogue/produits/{id}` — Détail ; POST `/catalogue/produits` — Création ; PATCH `/catalogue/produits/{id}` — Mise à jour ; DELETE `/catalogue/produits/{id}` — Soft delete ; GET `/catalogue/produits/{id}/conditionnements` — Conditionnements du produit ; GET `/catalogue/produits/{id}/prix` — Prix du produit ; GET `/catalogue/produits/{id}/variantes` — Variantes du produit |
| **Produits–Conditionnements** | GET `/catalogue/produits-conditionnements/{id}` — Détail ; POST `/catalogue/produits-conditionnements` — Création ; PATCH `/catalogue/produits-conditionnements/{id}` — Mise à jour ; DELETE `/catalogue/produits-conditionnements/{id}` — Suppression |
| **Canaux de vente** | GET `/catalogue/canaux-vente` — Liste ; GET `/catalogue/canaux-vente/{id}` — Détail ; POST `/catalogue/canaux-vente` — Création ; PATCH `/catalogue/canaux-vente/{id}` — Mise à jour |
| **Prix produits** | GET `/catalogue/prix-produits` — Liste ; GET `/catalogue/prix-produits/{id}` — Détail ; POST `/catalogue/prix-produits` — Création ; PATCH `/catalogue/prix-produits/{id}` — Mise à jour ; DELETE `/catalogue/prix-produits/{id}` — Suppression |
| **Variantes produit** | GET `/catalogue/variantes-produits/{id}` — Détail ; POST `/catalogue/variantes-produits` — Création ; PATCH `/catalogue/variantes-produits/{id}` — Mise à jour ; DELETE `/catalogue/variantes-produits/{id}` — Suppression |

---

### 4. Partenaires (`/partenaires`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Types de tiers** | GET `/partenaires/types-tiers` — Liste ; GET `/partenaires/types-tiers/{id}` — Détail ; POST `/partenaires/types-tiers` — Création ; PATCH `/partenaires/types-tiers/{id}` — Mise à jour |
| **Tiers** | GET `/partenaires/tiers` — Liste ; GET `/partenaires/tiers/{id}` — Détail ; POST `/partenaires/tiers` — Création ; PATCH `/partenaires/tiers/{id}` — Mise à jour ; DELETE `/partenaires/tiers/{id}` — Soft delete ; GET `/partenaires/tiers/{id}/contacts` — Liste des contacts du tiers |
| **Contacts** | POST `/partenaires/contacts` — Création ; GET `/partenaires/contacts/{id}` — Détail ; PATCH `/partenaires/contacts/{id}` — Mise à jour ; DELETE `/partenaires/contacts/{id}` — Suppression |

---

## P2 — Opérations commerciales et logistique

### 5. Commercial (`/commercial`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **États document** | GET `/commercial/etats-document` — Liste ; GET `/commercial/etats-document/{id}` — Détail ; POST `/commercial/etats-document` — Création ; PATCH `/commercial/etats-document/{id}` — Mise à jour |
| **Devis** | GET `/commercial/devis` — Liste ; GET `/commercial/devis/{id}` — Détail ; POST `/commercial/devis` — Création ; PATCH `/commercial/devis/{id}` — Mise à jour |
| **Commandes** | GET `/commercial/commandes` — Liste ; GET `/commercial/commandes/{id}` — Détail ; POST `/commercial/commandes` — Création ; PATCH `/commercial/commandes/{id}` — Mise à jour |
| **Factures** | GET `/commercial/factures` — Liste ; GET `/commercial/factures/{id}` — Détail ; POST `/commercial/factures` — Création ; PATCH `/commercial/factures/{id}` — Mise à jour |
| **Bons de livraison** | GET `/commercial/bons-livraison` — Liste ; GET `/commercial/bons-livraison/{id}` — Détail ; POST `/commercial/bons-livraison` — Création ; PATCH `/commercial/bons-livraison/{id}` — Mise à jour |

---

### 6. Achats (`/achats`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Dépôts** | GET `/achats/depots` — Liste ; GET `/achats/depots/{id}` — Détail ; POST `/achats/depots` — Création ; PATCH `/achats/depots/{id}` — Mise à jour |
| **Commandes fournisseurs** | GET `/achats/commandes-fournisseurs` — Liste ; GET `/achats/commandes-fournisseurs/{id}` — Détail ; POST `/achats/commandes-fournisseurs` — Création ; PATCH `/achats/commandes-fournisseurs/{id}` — Mise à jour ; GET `/achats/commandes-fournisseurs/{id}/receptions` — Réceptions liées |
| **Réceptions** | POST `/achats/receptions` — Création ; GET `/achats/receptions/{id}` — Détail ; PATCH `/achats/receptions/{id}` — Mise à jour |
| **Factures fournisseurs** | GET `/achats/factures-fournisseurs` — Liste ; GET `/achats/factures-fournisseurs/{id}` — Détail ; POST `/achats/factures-fournisseurs` — Création ; PATCH `/achats/factures-fournisseurs/{id}` — Mise à jour |

---

### 7. Stock (`/stock`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Stocks** | GET `/stock/depots/{depot_id}/stocks` — Liste par dépôt ; GET `/stock/depots/{depot_id}/stocks/{stock_id}` — Détail ; GET `/stock/depots/{depot_id}/produits/{produit_id}/quantite` — Quantité disponible ; GET `/stock/produits/{produit_id}/stocks` — Liste par produit |
| **Mouvements de stock** | GET `/stock/mouvements` — Liste ; GET `/stock/mouvements/{id}` — Détail ; POST `/stock/mouvements` — Création (entrée, sortie, transfert, inventaire) |
| **Alertes stock** | GET `/stock/alertes` — Liste des alertes (seuils min/max) |

---

## P3 — Trésorerie et comptabilité

### 8. Trésorerie (`/tresorerie`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Modes de paiement** | GET `/tresorerie/modes-paiement` — Liste ; GET `/tresorerie/modes-paiement/{id}` — Détail ; POST `/tresorerie/modes-paiement` — Création ; PATCH `/tresorerie/modes-paiement/{id}` — Mise à jour |
| **Comptes trésorerie** | GET `/tresorerie/comptes` — Liste ; GET `/tresorerie/comptes/{id}` — Détail ; POST `/tresorerie/comptes` — Création ; PATCH `/tresorerie/comptes/{id}` — Mise à jour |
| **Règlements** | GET `/tresorerie/reglements` — Liste ; GET `/tresorerie/reglements/{id}` — Détail ; POST `/tresorerie/reglements` — Création |

---

### 9. Comptabilité (`/comptabilite`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Comptes comptables** | GET `/comptabilite/comptes` — Liste ; GET `/comptabilite/comptes/{id}` — Détail ; POST `/comptabilite/comptes` — Création ; PATCH `/comptabilite/comptes/{id}` — Mise à jour |
| **Journaux comptables** | GET `/comptabilite/journaux` — Liste ; GET `/comptabilite/journaux/{id}` — Détail ; POST `/comptabilite/journaux` — Création ; PATCH `/comptabilite/journaux/{id}` — Mise à jour |
| **Périodes comptables** | GET `/comptabilite/periodes` — Liste ; GET `/comptabilite/periodes/{id}` — Détail ; POST `/comptabilite/periodes` — Création ; PATCH `/comptabilite/periodes/{id}` — Mise à jour |
| **Écritures comptables** | GET `/comptabilite/ecritures` — Liste ; GET `/comptabilite/ecritures/{id}` — Détail (avec lignes) ; POST `/comptabilite/ecritures` — Création |

---

## P4 — RH et paie

### 10. RH (`/rh`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Départements** | GET `/rh/departements` — Liste ; GET `/rh/departements/{id}` — Détail ; POST `/rh/departements` — Création ; PATCH `/rh/departements/{id}` — Mise à jour |
| **Postes** | GET `/rh/postes` — Liste ; GET `/rh/postes/{id}` — Détail ; POST `/rh/postes` — Création ; PATCH `/rh/postes/{id}` — Mise à jour |
| **Types de contrat** | GET `/rh/types-contrat` — Liste ; GET `/rh/types-contrat/{id}` — Détail ; POST `/rh/types-contrat` — Création ; PATCH `/rh/types-contrat/{id}` — Mise à jour |
| **Employés** | GET `/rh/employes` — Liste ; GET `/rh/employes/{id}` — Détail ; POST `/rh/employes` — Création ; PATCH `/rh/employes/{id}` — Mise à jour |
| **Types de congé** | GET `/rh/types-conge` — Liste ; GET `/rh/types-conge/{id}` — Détail ; POST `/rh/types-conge` — Création ; PATCH `/rh/types-conge/{id}` — Mise à jour |
| **Demandes de congé** | GET `/rh/demandes-conge` — Liste ; GET `/rh/demandes-conge/{id}` — Détail ; POST `/rh/demandes-conge` — Création ; PATCH `/rh/demandes-conge/{id}` — Mise à jour |
| **Soldes de congé** | GET `/rh/soldes-conge` — Liste ; GET `/rh/soldes-conge/{id}` — Détail ; POST `/rh/soldes-conge` — Création ; PATCH `/rh/soldes-conge/{id}` — Mise à jour |
| **Objectifs** | GET `/rh/objectifs` — Liste ; GET `/rh/objectifs/{id}` — Détail ; POST `/rh/objectifs` — Création ; PATCH `/rh/objectifs/{id}` — Mise à jour |
| **Taux de commission** | GET `/rh/taux-commissions` — Liste ; GET `/rh/taux-commissions/{id}` — Détail ; POST `/rh/taux-commissions` — Création ; PATCH `/rh/taux-commissions/{id}` — Mise à jour |
| **Commissions** | GET `/rh/commissions` — Liste ; GET `/rh/commissions/{id}` — Détail ; POST `/rh/commissions` — Création ; PATCH `/rh/commissions/{id}` — Mise à jour |
| **Avances** | GET `/rh/avances` — Liste ; GET `/rh/avances/{id}` — Détail ; POST `/rh/avances` — Création ; PATCH `/rh/avances/{id}` — Mise à jour |

---

### 11. Paie (`/paie`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Périodes de paie** | GET `/paie/periodes` — Liste ; GET `/paie/periodes/{id}` — Détail ; POST `/paie/periodes` — Création ; PATCH `/paie/periodes/{id}` — Mise à jour |
| **Types d’éléments de paie** | GET `/paie/types-element` — Liste ; GET `/paie/types-element/{id}` — Détail ; POST `/paie/types-element` — Création ; PATCH `/paie/types-element/{id}` — Mise à jour |
| **Bulletins de paie** | GET `/paie/bulletins` — Liste ; GET `/paie/bulletins/{id}` — Détail ; GET `/paie/bulletins/{id}/detail` — Détail avec lignes ; POST `/paie/bulletins` — Création ; PATCH `/paie/bulletins/{id}` — Mise à jour |

---

## P5 — Support, rapports et actifs

### 12. Système (`/systeme`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Paramètres système** | GET `/systeme/parametres` — Liste ; GET `/systeme/parametres/{id}` — Détail ; POST `/systeme/parametres` — Création ; PATCH `/systeme/parametres/{id}` — Mise à jour |
| **Journal d’audit** | GET `/systeme/audit` — Liste ; GET `/systeme/audit/{id}` — Détail ; POST `/systeme/audit` — Création d’une entrée |
| **Notifications** | GET `/systeme/notifications` — Liste ; GET `/systeme/notifications/{id}` — Détail ; POST `/systeme/notifications` — Création ; PATCH `/systeme/notifications/{id}` — Mise à jour ; POST `/systeme/notifications/{id}/marquer-lue` — Marquer comme lue |
| **Licences logicielles** | GET `/systeme/licences` — Liste ; GET `/systeme/licences/verifier` — Vérifier validité ; GET `/systeme/licences/{id}` — Détail ; POST `/systeme/licences` — Création ; PATCH `/systeme/licences/{id}` — Mise à jour ; POST `/systeme/licences/{id}/activer` — Activer ; POST `/systeme/licences/{id}/prolonger` — Prolonger ; GET `/systeme/licences/{id}/info-prolongations` — Infos prolongations |

---

### 13. Rapports (`/rapports`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Chiffre d’affaires** | GET `/rapports/chiffre-affaires` — CA sur une période (paramètres : entreprise, dates, etc.) |
| **Tableau de bord** | GET `/rapports/dashboard` — Synthèse (CA, factures, commandes, employés actifs, etc.) |

---

### 14. Immobilisations (`/immobilisations`)

| Fonctionnalité | Opérations (par ordre) |
|----------------|------------------------|
| **Catégories d’immobilisation** | GET `/immobilisations/categories` — Liste ; GET `/immobilisations/categories/{id}` — Détail ; POST `/immobilisations/categories` — Création ; PATCH `/immobilisations/categories/{id}` — Mise à jour |
| **Immobilisations (actifs)** | GET `/immobilisations/actifs` — Liste ; GET `/immobilisations/actifs/{id}` — Détail ; POST `/immobilisations/actifs` — Création ; PATCH `/immobilisations/actifs/{id}` — Mise à jour ; GET `/immobilisations/actifs/{id}/lignes-amortissement` — Lignes d’amortissement |

---

## Récapitulatif — Ordre des modules

| # | Priorité | Module | Préfixe |
|---|----------|--------|---------|
| 1 | P0 | Auth | `/auth` |
| 2 | P0 | Paramétrage | `/parametrage` |
| 3 | P1 | Catalogue | `/catalogue` |
| 4 | P1 | Partenaires | `/partenaires` |
| 5 | P2 | Commercial | `/commercial` |
| 6 | P2 | Achats | `/achats` |
| 7 | P2 | Stock | `/stock` |
| 8 | P3 | Trésorerie | `/tresorerie` |
| 9 | P3 | Comptabilité | `/comptabilite` |
| 10 | P4 | RH | `/rh` |
| 11 | P4 | Paie | `/paie` |
| 12 | P5 | Système | `/systeme` |
| 13 | P5 | Rapports | `/rapports` |
| 14 | P5 | Immobilisations | `/immobilisations` |

Voir aussi : `MODULES_PRIORITES.md` pour la justification des niveaux P0–P5.
