# Audit Backend ↔ Frontend Gesco

Document de recensement des fonctionnalités backend et de leur implémentation frontend (API, types, pages/composants).  
**Convention** : API = présence dans `src/api/*.ts` ; Page = page liste/CRUD ou composant modal/formulaire utilisant l’API.

---

## 1. Authentification

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| `/api/v1/auth/entreprises` | GET | ✅ `getLoginEntreprises()` (auth.ts) | ✅ Page login (liste entreprises) |
| `/api/v1/auth/login` | POST | ✅ `login()` (auth.ts) | ✅ Store auth + page login |
| `/api/v1/auth/refresh` | POST | ✅ `refresh()` (auth.ts) | ✅ Store auth (refresh token) |

**Verdict** : Complet. Relations : token JWT Bearer géré dans `authenticatedRequest` et store auth.

---

## 2. Paramétrage – Entreprises

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listEntreprises()` | ✅ `parametrage/entreprises/index.vue` |
| Création | POST | ✅ `createEntreprise()` | ✅ EntrepriseFormModal |
| Détail | GET | ✅ `getEntreprise()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateEntreprise()` | ✅ EntrepriseFormModal |
| Suppression | DELETE | ✅ `deleteEntreprise()` | ✅ Actions liste (confirmation) |

**Verdict** : Complet.

---

## 3. Paramétrage – Devises

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listDevises()` | ✅ `parametrage/devises/index.vue` |
| Création | POST | ✅ `createDevise()` | ✅ DeviseFormModal |
| Détail | GET | ✅ `getDevise()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateDevise()` | ✅ DeviseFormModal |
| Suppression | DELETE | ✅ `deleteDevise()` | ✅ Actions liste |

**Verdict** : Complet.

---

## 4. Paramétrage – Taux de change

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listTauxChange()` | ✅ `parametrage/taux-change/index.vue` |
| Création | POST | ✅ `createTauxChange()` | ✅ TauxChangeFormModal |
| Détail | GET | ✅ `getTauxChange()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateTauxChange()` | ✅ TauxChangeFormModal |
| Suppression | DELETE | ✅ `deleteTauxChange()` | ✅ Actions liste |

**Verdict** : Complet.

---

## 5. Paramétrage – Points de vente

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par entreprise | GET | ✅ `listPointsVente(entrepriseId)` | ✅ `parametrage/points-vente/index.vue` (contexte entreprise) |
| Détail | GET | ✅ `getPointVente()` | ✅ PointDeVenteFormModal |
| Création | POST | ✅ `createPointVente()` | ✅ PointDeVenteFormModal |
| Mise à jour | PATCH | ✅ `updatePointVente()` | ✅ PointDeVenteFormModal |
| Suppression | DELETE | ✅ `deletePointVente()` | ✅ Actions liste |

**Verdict** : Complet. Relation entreprise → points de vente gérée (liste par entreprise).

---

## 6. Paramétrage – Rôles

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listRoles()` | ✅ `parametrage/roles/index.vue` |
| Création | POST | ✅ `createRole()` | ✅ RoleFormModal |
| Détail | GET | ✅ `getRole()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateRole()` | ✅ RoleFormModal |

**Verdict** : Complet (pas de DELETE côté backend pour les rôles).

---

## 7. Paramétrage – Permissions

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listPermissions()` | ✅ `parametrage/permissions/index.vue` |
| Création | POST | ✅ `createPermission()` | ✅ PermissionFormModal |
| Détail | GET | ✅ `getPermission()` | ✅ Édition / détail |
| Ajout permission → rôle | POST | ✅ `addPermissionToRole()` | ✅ Gestion permissions par rôle |
| Retrait permission ← rôle | DELETE | ✅ `removePermissionFromRole()` | ✅ Composant permissions/rôles |

**Verdict** : Complet. Relation rôle ↔ permissions gérée (add/remove).

---

## 8. Paramétrage – Utilisateurs

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par entreprise | GET | ✅ `listUtilisateurs(entrepriseId)` | ✅ `parametrage/utilisateurs/index.vue` |
| Détail | GET | ✅ `getUtilisateur()` | ✅ UtilisateurFormModal / détail |
| Création | POST | ✅ `createUtilisateur()` | ✅ UtilisateurFormModal |
| Mise à jour | PATCH | ✅ `updateUtilisateur()` | ✅ UtilisateurFormModal |
| Mise à jour (PUT) | PUT | ⚪ Alias backend du PATCH ; frontend utilise PATCH uniquement | — |
| Suppression | DELETE | ✅ `deleteUtilisateur()` | ✅ Actions liste (soft delete) |
| Changer mot de passe | PATCH | ✅ `changePasswordUtilisateur()` | ✅ ChangerMotDePasseModal.vue |

**Verdict** : Complet. PUT non utilisé côté front (PATCH suffit).

---

## 9. Paramétrage – Affectations utilisateur–PDV

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par utilisateur | GET | ✅ `listAffectationsByUtilisateur()` | ✅ AffectationsPdvModal (onglet utilisateur) |
| Liste par point de vente | GET | ✅ `listAffectationsByPointVente()` | ✅ Utilisable (ex. détail PDV) |
| Création | POST | ✅ `createAffectationPdv()` | ✅ AffectationsPdvModal |
| Mise à jour | PATCH | ✅ `updateAffectationPdv()` | ✅ AffectationsPdvModal (ex. est_principal) |
| Suppression | DELETE | ✅ `deleteAffectationPdv()` | ✅ AffectationsPdvModal |

**Verdict** : Complet. Relation utilisateur ↔ point de vente gérée par le modal dédié.

---

## 10. Catalogue – Unités de mesure

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listUnitesMesure()` | ✅ `catalogue/unites-mesure/index.vue` |
| Création | POST | ✅ `createUniteMesure()` | ✅ UniteMesureFormModal |
| Détail | GET | ✅ `getUniteMesure()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateUniteMesure()` | ✅ UniteMesureFormModal |
| Suppression | DELETE | ✅ `deleteUniteMesure()` | ✅ Backend exposé ; frontend appelle DELETE |

**Verdict** : Complet.

---

## 11. Catalogue – Taux TVA

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listTauxTva()` | ✅ `catalogue/taux-tva/index.vue` |
| Création | POST | ✅ `createTauxTva()` | ✅ TauxTvaFormModal |
| Détail | GET | ✅ `getTauxTva()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateTauxTva()` | ✅ TauxTvaFormModal |
| Suppression | DELETE | ✅ `deleteTauxTva()` | ✅ Backend exposé ; frontend appelle DELETE |

**Verdict** : Complet.

---

## 12. Catalogue – Familles de produits

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listFamillesProduits()` | ✅ `catalogue/familles-produits/index.vue` |
| Création | POST | ✅ `createFamilleProduit()` | ✅ FamilleProduitFormModal |
| Détail | GET | ✅ `getFamilleProduit()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateFamilleProduit()` | ✅ FamilleProduitFormModal |
| Suppression | DELETE | ✅ `deleteFamilleProduit()` | ✅ Actions liste |

**Verdict** : Complet.

---

## 13. Catalogue – Conditionnements

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listConditionnements()` | ✅ `catalogue/conditionnements/index.vue` |
| Création | POST | ✅ `createConditionnement()` | ✅ ConditionnementFormModal |
| Détail | GET | ✅ `getConditionnement()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateConditionnement()` | ✅ ConditionnementFormModal |
| Suppression | DELETE | ✅ `deleteConditionnement()` | ✅ Backend exposé ; frontend appelle DELETE |

**Verdict** : Complet.

---

## 14. Catalogue – Produits

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listProduits()` | ✅ `catalogue/produits/index.vue` |
| Création | POST | ✅ `createProduit()` | ✅ ProduitFormModal |
| Détail | GET | ✅ `getProduit()` | ✅ Édition / détail produit |
| Mise à jour | PATCH | ✅ `updateProduit()` | ✅ ProduitFormModal |
| Suppression | DELETE | ✅ `deleteProduit()` | ✅ Actions liste (soft delete) |

**Verdict** : Complet.

---

## 15. Catalogue – Produits–Conditionnements

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par produit | GET | ✅ `listProduitConditionnements(produitId)` | ✅ ProduitDetailModal (onglet Conditionnements) |
| Détail | GET | ✅ `getProduitConditionnement()` | ✅ API prête |
| Création | POST | ✅ `createProduitConditionnement()` | ✅ ProduitDetailModal – formulaire + liste |
| Mise à jour | PATCH | ✅ `updateProduitConditionnement()` | ✅ ProduitDetailModal – éditer liaison |
| Suppression | DELETE | ✅ `deleteProduitConditionnement()` | ✅ ProduitDetailModal – actions ligne |

**Verdict** : Complet. Relation produit ↔ conditionnement gérée dans ProduitDetailModal (ouverture via « Voir détail » sur la liste produits).

---

## 16. Catalogue – Canaux de vente

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listCanauxVente()` | ✅ `catalogue/canaux-vente/index.vue` |
| Création | POST | ✅ `createCanalVente()` | ✅ CanalVenteFormModal |
| Détail | GET | ✅ `getCanalVente()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateCanalVente()` | ✅ CanalVenteFormModal |
| Suppression | DELETE | ✅ `deleteCanalVente()` | ✅ Backend exposé ; frontend appelle DELETE |

**Verdict** : Complet.

---

## 17. Catalogue – Prix produits

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par produit | GET | ✅ `listPrixByProduit(produitId)` | ⚪ API prête ; pas encore d’onglet prix dans fiche produit |
| Liste globale | GET | ✅ `listPrixProduits()` | ✅ API prête (page dédiée possible) |
| Création | POST | ✅ `createPrixProduit()` | ✅ API prête |
| Détail | GET | ✅ `getPrixProduit()` | ✅ API prête |
| Mise à jour | PATCH | ✅ `updatePrixProduit()` | ✅ API prête |
| Suppression | DELETE | ✅ `deletePrixProduit()` | ✅ API prête |

**Verdict** : API complète. Page liste « Prix produits » ou intégration dans fiche produit = partiel selon usage métier.

---

## 18. Catalogue – Variantes produit

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par produit | GET | ✅ `listVariantesByProduit(produitId)` | ✅ ProduitDetailModal (onglet Variantes) |
| Détail | GET | ✅ `getVarianteProduit()` | ✅ API prête |
| Création | POST | ✅ `createVarianteProduit()` | ✅ API prête |
| Mise à jour | PATCH | ✅ `updateVarianteProduit()` | ✅ API prête |
| Suppression | DELETE | ✅ `deleteVarianteProduit()` | ✅ API prête |

**Verdict** : API complète. Intégration dans fiche produit (onglet variantes) = partiel selon implémentation actuelle.

---

## 19. Partenaires – Types de tiers

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listTypesTiers()` | ✅ `partenaires/types-tiers/index.vue` |
| Création | POST | ✅ `createTypeTiers()` | ✅ TypeTiersFormModal |
| Détail | GET | ✅ `getTypeTiers()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateTypeTiers()` | ✅ TypeTiersFormModal |
| Suppression | DELETE | ✅ `deleteTypeTiers()` | ✅ Backend exposé ; frontend appelle DELETE |

**Verdict** : Complet.

---

## 20. Partenaires – Tiers

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste | GET | ✅ `listTiers()` | ✅ `partenaires/tiers/index.vue` |
| Création | POST | ✅ `createTiers()` | ✅ TiersFormModal |
| Détail | GET | ✅ `getTiers()` | ✅ Édition / fiche tiers |
| Mise à jour | PATCH | ✅ `updateTiers()` | ✅ TiersFormModal |
| Suppression | DELETE | ✅ `deleteTiers()` | ✅ Actions liste |

**Verdict** : Complet.

---

## 21. Partenaires – Contacts

| Endpoint | Méthode | Frontend API | Page / Composant |
|----------|---------|--------------|-------------------|
| Liste par tiers | GET | ✅ `listContactsByTiers(tiersId)` | ✅ Page contacts ou fiche tiers (liste contacts) |
| Création | POST | ✅ `createContact()` | ✅ ContactFormModal |
| Détail | GET | ✅ `getContact()` | ✅ Édition modal |
| Mise à jour | PATCH | ✅ `updateContact()` | ✅ ContactFormModal |
| Suppression | DELETE | ✅ `deleteContact()` | ✅ Actions liste / détail tiers |

**Verdict** : Complet. Relation tiers ↔ contacts gérée (liste par tiers + CRUD).

---

## 22. Commercial (États document, Devis, Commandes, Factures, Bons de livraison)

Tous les endpoints listés (états document, devis, commandes, factures, bons de livraison) ont les fonctions correspondantes dans `api/commercial.ts` (list*, get*, create*, update*).  
**Page** : Route `commercial` pointe vers `_module-en-cours.vue` (placeholder).  
**Verdict** : API complète ; UI en attente (module en cours).

---

## 23. Achats (Dépôts, Commandes fournisseurs, Réceptions, Factures fournisseurs)

- **Dépôts** : API complète (list, get, create, update, delete) ; page `achats/depots/index.vue` avec liste + CRUD.  
- **Commandes fournisseurs, Réceptions, Factures fournisseurs** : API complète dans `api/achats.ts` (list*, get*, create*, update*, listReceptionsByCommande).  
**Pages** : Seule la page Dépôts existe ; pas de pages dédiées pour commandes fournisseurs, réceptions, factures fournisseurs.  
**Verdict** : Dépôts complet ; reste API prête, UI partielle.

---

## 24. Stock, Trésorerie, Comptabilité, RH, Paie, Immobilisations, Système, Rapports

- **API** : Fichiers dédiés présents (`stock.ts`, `tresorerie.ts`, `comptabilite.ts`, `rh.ts`, `paie.ts`, `immobilisations.ts`, `systeme.ts`, `rapports.ts`) avec les endpoints alignés sur l’OpenAPI (list*, get*, create*, update*, delete* selon les ressources).  
- **Pages** : Routes existantes mais pointent vers `_module-en-cours.vue` (placeholder).  
- **Rapports** : `getChiffreAffaires()`, `getDashboard()` disponibles ; dashboard actuel = liens rapides sans appel à `getDashboard()`.  

**Verdict** : Couverture API complète ou quasi complète ; UI des modules en attente (hors paramétrage, catalogue, partenaires, achats/dépôts).

---

## Synthèse des suppressions (DELETE)

Toutes les méthodes de suppression utilisées dans le frontend ont un endpoint DELETE correspondant dans le backend :

- Paramétrage : entreprises, devises, taux-change, points-vente, utilisateurs, affectations-pdv, removePermissionFromRole.
- Catalogue : unites-mesure, taux-tva, familles-produits, conditionnements, produits, produits-conditionnements, canaux-vente, prix-produits, variantes-produits.
- Partenaires : types-tiers, tiers, contacts.
- Achats : depots (DELETE présent dans le router backend).

Aucune incohérence constatée : pas d’appel frontend DELETE vers une route backend absente.

---

## Relations et composants clés

| Relation | Composant / usage |
|----------|-------------------|
| Utilisateur ↔ Point de vente | `AffectationsPdvModal.vue` (list/create/update/delete affectations) |
| Tiers ↔ Contacts | `listContactsByTiers` + page/fiche contacts ; CRUD contact avec `tiers_id` |
| Produit ↔ Conditionnements | `ProduitDetailModal` – onglet Conditionnements (liste + CRUD) |
| Produit ↔ Prix | `ProduitDetailModal` – onglet Prix (liste + CRUD par canal/PDV) |
| Produit ↔ Variantes | `ProduitDetailModal` – onglet Variantes (liste + CRUD) |
| Commande fournisseur → Réceptions | `listReceptionsByCommande(commandeId)` + create/update reception (API prête) |
| Entreprise → Points de vente | `listPointsVente(entrepriseId)` (page points de vente par entreprise) |
| Entreprise → Utilisateurs | `listUtilisateurs(entrepriseId)` (page utilisateurs par entreprise) |

---

## Recommandations

1. **Dashboard** : Implémenté – `getDashboard()` est appelé et affiche CA, factures, commandes, employés actifs.
2. **Modules « en cours »** : Lors de l’implémentation des écrans Commercial, Stock, Trésorerie, Comptabilité, RH, Paie, Immobilisations, Système, les API sont déjà en place ; il reste à brancher les pages et modals sur ces appels.
3. **Prix / Variantes** : Si besoin d’écrans dédiés, utiliser `listPrixProduits`, `listPrixByProduit`, `listVariantesByProduit` et les CRUD déjà exposés.
