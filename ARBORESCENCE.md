# Arborescence du projet Gesco (backend FastAPI)

Structure par module, alignée sur la spécification système de gestion commerciale Cameroun.

---

```
Gesco/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py
│   │
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── common.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── numerotation.py
│   │       ├── calculs.py
│   │       └── audit.py
│   │
│   └── modules/
│       ├── __init__.py
│       │
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── service.py
│       │   └── router.py
│       │
│       ├── parametrage/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── entreprise.py
│       │   │   ├── devise.py
│       │   │   ├── taux_change.py
│       │   │   ├── point_vente.py
│       │   │   ├── utilisateur.py
│       │   │   ├── role.py
│       │   │   ├── permission.py
│       │   │   └── affectation_utilisateur_pdv.py
│       │   └── router.py
│       │
│       ├── catalogue/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── famille_produit.py
│       │   │   ├── unite_mesure.py
│       │   │   ├── conditionnement.py
│       │   │   ├── produit.py
│       │   │   ├── taux_tva.py
│       │   │   ├── produit_conditionnement.py
│       │   │   ├── canal_vente.py
│       │   │   ├── prix.py
│       │   │   └── variante.py
│       │   └── router.py
│       │
│       ├── partenaires/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── type_tiers.py
│       │   │   ├── tiers.py
│       │   │   └── contact.py
│       │   └── router.py
│       │
│       ├── commercial/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── etat_document.py
│       │   │   ├── devis.py
│       │   │   ├── commande.py
│       │   │   ├── facture.py
│       │   │   └── bon_livraison.py
│       │   └── router.py
│       │
│       ├── stock/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── depot.py
│       │   │   ├── stock.py
│       │   │   ├── type_mouvement_stock.py
│       │   │   ├── mouvement.py
│       │   │   ├── inventaire.py
│       │   │   └── alerte.py
│       │   └── router.py
│       │
│       ├── tresorerie/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── mode_paiement.py
│       │   │   ├── compte_tresorerie.py
│       │   │   ├── session_caisse.py
│       │   │   ├── reglement.py
│       │   │   ├── operation_caisse.py
│       │   │   └── echeance.py
│       │   └── router.py
│       │
│       ├── achats/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── commande_fournisseur.py
│       │   │   ├── reception.py
│       │   │   └── facture_fournisseur.py
│       │   └── router.py
│       │
│       ├── comptabilite/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── plan_comptable.py
│       │   │   ├── compte_comptable.py
│       │   │   ├── journal_comptable.py
│       │   │   ├── periode_comptable.py
│       │   │   ├── ecriture.py
│       │   │   └── modele_ecriture.py
│       │   └── router.py
│       │
│       ├── rh/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── schemas.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── employe.py
│       │   │   ├── objectif.py
│       │   │   ├── taux_commission.py
│       │   │   ├── commission.py
│       │   │   └── avance.py
│       │   └── router.py
│       │
│       └── systeme/
│           ├── __init__.py
│           ├── models.py
│           ├── schemas.py
│           ├── services/
│           │   ├── __init__.py
│           │   ├── audit.py
│           │   ├── cache_session.py
│           │   ├── synchronisation.py
│           │   ├── parametre_systeme.py
│           │   └── notification.py
│           └── router.py
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   └── test_factures.py
│   └── services/
│       └── __init__.py
│
├── scripts/
│   └── seed_data.py
│
├── .env.example
├── alembic.ini
├── pyproject.toml
├── README.md
└── ARBORESCENCE.md
```

---

## Correspondance exacte avec la spécification (Section 7.1 + Annexe A)

Référence : **SPECIFICATION_SYSTEME_GESTION_COMMERCIALE_CAMEROUN.md**, tableau « Couverture par module (Annexe A) ».

| Module app | Section annexe | Tables de la spec (une table = un fichier models/schemas + service dédié si besoin) |
|------------|----------------|--------------------------------------------------------------------------------------|
| **auth** | — | Authentification (login, token). Utilise les tables `utilisateurs`, `sessions` du module parametrage. |
| **parametrage** | A.1 | entreprises, devises, taux_change, points_de_vente, utilisateurs, roles, permissions, permissions_roles, sessions, affectations_utilisateur_point_de_vente |
| **catalogue** | A.2 | familles_produits, unites_mesure, conditionnements, produits, taux_tva, produits_conditionnements, canaux_vente, prix_produits, variantes_produits |
| **partenaires** | A.3 | types_tiers, tiers, contacts |
| **commercial** | A.4 | etats_document, devis, lignes_devis, commandes, lignes_commandes, factures, lignes_factures, bons_livraison, lignes_bons_livraison |
| **stock** | A.5 | depots, stocks, types_mouvement_stock, mouvements_stock, inventaires, lignes_inventaires, alertes_stock |
| **tresorerie** | A.6 | modes_paiement, comptes_tresorerie, sessions_caisse, reglements, lignes_reglements, operations_caisse, echeances |
| **achats** | A.7 | commandes_fournisseurs, lignes_commandes_fournisseurs, receptions, lignes_receptions, factures_fournisseurs |
| **comptabilite** | A.8 | plans_comptables, comptes_comptables, journaux_comptables, periodes_comptables, ecritures_comptables, lignes_ecritures_comptables, modeles_ecritures, lignes_modeles_ecritures |
| **rh** | A.9 | employes, objectifs_vendeurs, taux_commissions, commissions, avances_employes |
| **systeme** | A.10 | journal_audit, cache_travail_session, synchronisations, parametres_systeme, notifications |

**Reporting** (spec § 7.1) : pas de tables dédiées ; rapports = requêtes / vues sur les modules existants → pas de module `reporting` dans l’arborescence.

**Convention lignes** : les tables `lignes_*` (lignes_devis, lignes_commandes, lignes_factures, etc.) sont gérées dans le service du document parent (devis, commande, facture, etc.) ; pas de fichier service séparé par table de lignes.

---

## Confirmation : architecture adaptée et prête

L’architecture est **adaptée** et **prête à accueillir** le projet Gesco avec **clarté** et **optimalité**.

| Critère | État |
|--------|------|
| **Alignement spec** | Chaque module (A.1 à A.10) et chaque table de la spécification ont un emplacement dédié (models, schemas, services). |
| **Clarté** | Séparation nette : **core** (sécurité, DB, dépendances, exceptions), **api/v1** (versionnement), **shared** (schémas communs, numérotation, calculs, audit), **modules** (un domaine = un dossier avec models, schemas, services, router). |
| **Optimalité** | Un **router** et des **services** par module ; pas de duplication de rôles ; **shared** évite la duplication (numérotation, calculs, audit) ; API versionnée (v1) pour évolutions futures. |
| **Évolutivité** | Ajout d’un nouveau domaine = nouveau dossier sous `modules/` avec le même pattern. Couche **repository** possible plus tard si besoin (entre services et DB). |
| **Tests** | Structure `tests/api/` et `tests/services/` prête ; `conftest.py` pour fixtures partagées. |
| **Migrations** | Alembic en place (`alembic/`, `env.py`, `versions/`) pour le schéma de base de données. |

**Prochaine étape** : implémenter le code dans chaque fichier (main.py, config, core, routers, services, models, schemas) en restant fidèle à cette structure.
