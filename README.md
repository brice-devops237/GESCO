# Gesco

**Système de gestion intégré (ERP)** – API backend multi-entreprises conçue pour le marché camerounais et la zone CEMAC. Gesco couvre l’ensemble du cycle de gestion : paramétrage, catalogue, partenaires (clients/fournisseurs), ventes (devis, commandes, factures, bons de livraison), achats (commandes fournisseurs, réceptions, factures fournisseurs), **stock**, **trésorerie** (modes de paiement, comptes, règlements), **comptabilité** (plan comptable, journaux, périodes, écritures), **ressources humaines** (employés, départements, postes, congés, objectifs, commissions, avances), **paie** (périodes, bulletins, types d’éléments), **immobilisations** (catégories et actifs), **système** (paramètres, audit, notifications, licence) et **rapports** (tableaux de bord, chiffre d’affaires). Conforme au droit camerounais (CGI, DGI, NIU, CEMAC) et aux normes internationales (ISO 3166, ISO 4217).

---

## Sommaire

- [Vue d’ensemble](#vue-densemble)
- [Fonctionnalités par domaine](#fonctionnalités-par-domaine)
- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Modules et API](#modules-et-api)
- [Documentation détaillée des modules](#documentation-détaillée-des-modules)
- [Configuration](#configuration)
- [Installation et lancement](#installation-et-lancement)
- [Authentification](#authentification)
- [Conformité réglementaire](#conformité-réglementaire)
- [Structure du projet](#structure-du-projet)
- [Migrations et tests](#migrations-et-tests)
- [Licence](#licence)

---

## Vue d’ensemble

**Gesco** est une **API REST** construite avec **FastAPI** et **SQLAlchemy 2** (mode asynchrone). Elle sert de backend à une application de gestion d’entreprise (type ERP) destinée au contexte camerounais et CEMAC :

- **Multi-entreprises (multi-tenant)** : plusieurs sociétés sur une même instance.
- **Multi points de vente** : gestion des PDV par entreprise.
- **Devises** : XAF prioritaire (FCFA), avec support multi-devises et taux de change.
- **Régimes fiscaux** : conformité CGI (informel, libératoire, forfait, réel simplifié, réel normal).
- **Identification** : NIU (DGI) pour entreprises et tiers.

L’architecture est **modulaire** : chaque domaine métier (Auth, Paramétrage, Catalogue, Partenaires, Commercial, Achats, Stock, Trésorerie, Comptabilité, RH, Paie, Immobilisations, Système, Rapports) dispose d’une couche **repositories** (accès aux données), d’une couche **services** (règles métier, validations, messages d’erreur centralisés dans `messages.py`) et d’un **router** FastAPI. Les réponses d’erreur sont normalisées (404, 400, 409, 401, 500) avec un format JSON cohérent.

---

## Fonctionnalités par domaine

| Domaine | Description |
|--------|-------------|
| **Authentification** | Connexion par entreprise + login + mot de passe ; renvoi d’un token JWT (Bearer). Vérification utilisateur actif et hash bcrypt. |
| **Paramétrage** | Entreprises (NIU, régime fiscal, pays, devise principale), devises (ISO 4217), taux de change, points de vente (par entreprise), rôles, permissions (module/action), liaison permissions–rôles, utilisateurs (par entreprise, rôle, PDV), affectations utilisateur ↔ point de vente. Soft delete entreprise. |
| **Catalogue** | Unités de mesure, taux de TVA (CGI), familles de produits (hiérarchie), conditionnements, produits (famille, unités, TVA, seuils alerte), variantes produit, liaisons produit–conditionnement, canaux de vente (par entreprise), prix produits (canal / PDV, périodes). |
| **Partenaires** | Types de tiers (client, fournisseur, etc.), tiers – clients/fournisseurs (code, NIU, canal, limite crédit, délai paiement, mobile money, etc.), contacts (par tiers). Soft delete tiers. |
| **Commercial** | États document (par type : devis, commande, facture, BL), devis (client, montants HT/TVA/TTC, devise), commandes (lien devis optionnel), factures (types : facture, avoir, proforma, duplicata ; montants, échéance), bons de livraison (lien commande/facture). |
| **Achats** | Commandes fournisseurs (fournisseur, dépôt optionnel, état, devise), réceptions (par commande, dépôt, état : brouillon/validée/annulée), factures fournisseurs (statut paiement : non_paye/partiel/paye, montant restant dû). |
| **Stock** | Stocks par dépôt et par produit (optionnellement par variante), mouvements de stock (entrées/sorties), alertes de stock (seuils min/max). |
| **Trésorerie** | Modes de paiement (par entreprise), comptes de trésorerie, règlements (liaison factures, montants, dates). |
| **Comptabilité** | Plan comptable (comptes par entreprise), journaux comptables, périodes comptables (ouverture/clôture), écritures comptables et lignes (débit/crédit, compte, journal, période). |
| **Ressources humaines** | Départements, postes (par département), types de contrat, employés (poste, département, type de contrat), types de congé, demandes de congé, soldes de congé, objectifs, taux de commission, commissions, avances. |
| **Paie** | Périodes de paie (ouverture/clôture), types d’éléments de paie (salaire de base, primes, retenues, etc.), bulletins de paie et lignes (par employé, période, éléments). |
| **Immobilisations** | Catégories d’immobilisations (par entreprise), actifs immobilisés (désignation, catégorie, valeur, date d’acquisition, amortissement, etc.). |
| **Système** | Paramètres système (clé/valeur par entreprise, catégorie), journal d’audit (traçabilité des actions), notifications, gestion de licence logicielle. |
| **Rapports** | Chiffre d’affaires sur période (somme factures TTC), tableau de bord (synthèse : CA, nombre de factures, commandes, employés actifs, avec filtres dates optionnels). |

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| **Langage** | Python 3.12 |
| **Framework API** | FastAPI |
| **ORM** | SQLAlchemy 2 (asynchrone) |
| **Base de données** | PostgreSQL (async : asyncpg ; synchrone : psycopg2 pour Alembic) |
| **Validation & config** | Pydantic, pydantic-settings, python-dotenv |
| **Authentification** | JWT (python-jose), passlib/bcrypt pour les mots de passe |
| **Migrations** | Alembic |
| **Tests** | pytest, pytest-asyncio, pytest-cov |
| **Client HTTP** | httpx |

---

## Architecture

Le projet suit une **Clean Architecture** simplifiée en couches :

| Couche | Rôle | Emplacement |
|--------|------|-------------|
| **Présentation** | Points d’entrée HTTP, CORS, gestion des exceptions, enregistrement des routeurs | `app/main.py`, `app/modules/<module>/router.py` |
| **Application (use cases)** | Règles métier, validations, orchestration | `app/modules/<module>/services/` (une classe service par agrégat, `base.py`, `messages.py`) |
| **Domaine** | Modèles métier et enums | `app/modules/<module>/models.py` |
| **Infrastructure** | Accès aux données (persistance) | `app/modules/<module>/repositories/` (une classe repository par agrégat) |

Flux type par module : **models** → **schemas** (Create / Update / Response) → **repositories** → **services** → **router**.  
Les routes sont protégées par **CurrentUser** (JWT) sauf `/auth/login` et `/health`. La session base de données est injectée via **DbSession**.  
Chaque module métier peut s’appuyer sur un **BaseService** (`app/core/service_base.py`) pour les helpers d’erreur (`_raise_not_found`, `_raise_bad_request`, `_raise_conflict`, `_validate_enum`).

---

## Modules et API

Toutes les routes sont préfixées par **`/api/v1`** (configurable via `API_V1_PREFIX`).

### Authentification – `/api/v1/auth`

| Méthode | Route | Description |
|--------|-------|-------------|
| POST | `/login` | Connexion (entreprise_id, login, password) → `access_token` |

---

### Paramétrage – `/api/v1/parametrage`

Gestion des entreprises, devises, taux de change, points de vente, rôles, permissions, utilisateurs et affectations utilisateur–PDV.  
Exemples : `GET/POST/PATCH/DELETE /entreprises`, `/devises`, `/taux-change`, `/points-vente`, `/roles`, `/permissions`, `/utilisateurs`, `/affectations-utilisateur-pdv`, etc.

---

### Catalogue – `/api/v1/catalogue`

Unités de mesure, taux TVA, familles de produits, conditionnements, produits, variantes, liaisons produit–conditionnement, canaux de vente, prix produits.  
Exemples : `GET/POST/PATCH /unites-mesure`, `/taux-tva`, `/familles-produits`, `/produits`, `/canaux-vente`, `/prix`, etc.

---

### Partenaires – `/api/v1/partenaires`

Types de tiers, tiers (clients/fournisseurs), contacts.  
Exemples : `GET/POST/PATCH/DELETE /types-tiers`, `/tiers`, `/tiers/{id}/contacts`, `/contacts`.

---

### Commercial – `/api/v1/commercial`

États document, devis, commandes, factures (facture, avoir, proforma, duplicata), bons de livraison.  
Exemples : `GET/POST/PATCH /etats-document`, `/devis`, `/commandes`, `/factures`, `/bons-livraison`.

---

### Achats – `/api/v1/achats`

Commandes fournisseurs, réceptions, factures fournisseurs.  
Exemples : `GET/POST/PATCH /commandes-fournisseurs`, `/receptions`, `/factures-fournisseurs`.

---

### Stock – `/api/v1/stock`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/depots/{depot_id}/stocks` | Liste des stocks d’un dépôt |
| GET | `/depots/{depot_id}/stocks/{stock_id}` | Détail d’un stock |
| GET | `/depots/{depot_id}/produits/{produit_id}/quantite` | Quantité en stock (optionnel : variante) |
| GET/POST/PATCH | `/mouvements`, `/mouvements/{id}` | Mouvements de stock |
| GET | `/alertes` | Alertes de stock (seuils) |

---

### Trésorerie – `/api/v1/tresorerie`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/modes-paiement`, `/modes-paiement/{id}` | Modes de paiement |
| GET/POST/PATCH | `/comptes`, `/comptes/{id}` | Comptes de trésorerie |
| GET/POST/PATCH | `/reglements`, `/reglements/{id}` | Règlements |

---

### Comptabilité – `/api/v1/comptabilite`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/comptes`, `/comptes/{id}` | Comptes comptables (plan comptable) |
| GET/POST/PATCH | `/journaux`, `/journaux/{id}` | Journaux comptables |
| GET/POST/PATCH | `/periodes`, `/periodes/{id}` | Périodes comptables |
| GET/POST/PATCH | `/ecritures`, `/ecritures/{id}` | Écritures comptables (et lignes) |

---

### Ressources humaines – `/api/v1/rh`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/departements`, `/departements/{id}` | Départements |
| GET/POST/PATCH | `/postes`, `/postes/{id}` | Postes |
| GET/POST/PATCH | `/types-contrat`, `/types-contrat/{id}` | Types de contrat |
| GET/POST/PATCH | `/employes`, `/employes/{id}` | Employés |
| GET/POST/PATCH | `/types-conge`, `/types-conge/{id}` | Types de congé |
| GET/POST/PATCH | `/demandes-conge`, `/demandes-conge/{id}` | Demandes de congé |
| GET | `/soldes-conge` | Soldes de congé |
| GET/POST/PATCH | `/objectifs`, `/objectifs/{id}` | Objectifs |
| GET/POST/PATCH | `/taux-commission`, `/taux-commission/{id}` | Taux de commission |
| GET/POST/PATCH | `/commissions`, `/commissions/{id}` | Commissions |
| GET/POST/PATCH | `/avances`, `/avances/{id}` | Avances |

---

### Paie – `/api/v1/paie`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/periodes`, `/periodes/{id}` | Périodes de paie |
| GET/POST/PATCH | `/types-element`, `/types-element/{id}` | Types d’éléments de paie |
| GET/POST/PATCH | `/bulletins`, `/bulletins/{id}` | Bulletins de paie (et lignes) |

---

### Immobilisations – `/api/v1/immobilisations`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/categories`, `/categories/{id}` | Catégories d’immobilisations |
| GET/POST/PATCH | `/actifs`, `/actifs/{id}` | Actifs immobilisés |

---

### Système – `/api/v1/systeme`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/parametres`, `/parametres/{id}` | Paramètres système |
| GET/POST | `/audit`, `/audit/{id}` | Journal d’audit |
| GET/POST/PATCH | `/notifications`, `/notifications/{id}` | Notifications |
| GET/POST/PATCH | `/licence` | Licence logicielle |

---

### Rapports – `/api/v1/rapports`

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/chiffre-affaires` | Chiffre d’affaires sur une période (entreprise_id, date_debut, date_fin) |
| GET | `/dashboard` | Synthèse tableau de bord (CA, factures, commandes, employés actifs ; filtres dates optionnels) |

---

### Santé (hors préfixe API)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Santé de l’API (sans auth, sans DB) – pour load balancer et monitoring |

---

## Documentation détaillée des modules

Pour chaque module sont décrits : la **modélisation** (entités, attributs, relations, contraintes), puis les **opérations** (routes) avec les **scénarios nominaux**, **scénarios alternatifs** et **exceptions**.

---

### Module Authentification

**Vue d'ensemble**  
Le module Auth assure la connexion des utilisateurs par entreprise + login + mot de passe. Il s'appuie sur le module Paramétrage (Utilisateur) et sur `core.security` (JWT, bcrypt). Aucune entité persistée propre au module : uniquement des schémas d'entrée/sortie et un service de login.

**Modélisation**  
- **Schémas** : `LoginRequest` (entreprise_id, login, password), `TokenResponse` (access_token, token_type).  
- **Dépendance** : entité `Utilisateur` du module Paramétrage (id, entreprise_id, login, mot_de_passe_hash, actif).

**Opérations**

| Méthode | Route | Description |
|--------|-------|-------------|
| POST | `/auth/login` | Authentification et émission du token JWT |

**POST /auth/login**

- **Entrée** : `LoginRequest` (entreprise_id, login, password).
- **Scénario nominal** : L'utilisateur existe pour l'entreprise, est actif et le mot de passe correspond au hash stocké → génération du JWT (subject=user.id, extra_claims={entreprise_id}) → réponse 200 avec `TokenResponse` (access_token, token_type="bearer").
- **Scénarios alternatifs** : Aucun (en cas d'échec, on passe en exception).
- **Exceptions** :  
  - **401 Unauthorized** – Utilisateur non trouvé pour (entreprise_id, login) : message « Identifiants incorrects. ».  
  - **401 Unauthorized** – Utilisateur désactivé (`actif=False`) : message « Compte utilisateur désactivé. ».  
  - **401 Unauthorized** – Mot de passe incorrect : message « Identifiants incorrects. ».  
  - **422 Unprocessable Entity** – Données invalides (validation Pydantic : champs manquants, types incorrects, contraintes min_length, etc.).

---

### Module Paramétrage

**Vue d'ensemble**  
Paramétrage des entreprises, devises, taux de change, points de vente, rôles, permissions, utilisateurs et affectations utilisateur–PDV. Toutes les routes sont protégées par JWT (CurrentUser). Les messages d'erreur sont centralisés dans `parametrage.services.messages.Messages`.

**Modélisation (entités déduites des schémas et routes)**  
- **Entreprise** : id, code (unique), raison_sociale, sigle, niu (optionnel, DGI), regime_fiscal (CGI), mode_gestion, adresse, ville, region, pays (ISO 3166-1 alpha-3), telephone, email, site_web, devise_principale (ISO 4217), logo_url, actif, created_at, updated_at, deleted_at (soft delete). Contraintes : code unique, NIU unique si renseigné.  
- **Devise** : id, code (unique, 3 lettres), libelle, symbole, decimales, actif.  
- **TauxChange** : id, devise_from_id, devise_to_id, taux (>0), date_effet, created_at. Contrainte : devise_from ≠ devise_to.  
- **PointDeVente** : id, entreprise_id, code (unique par entreprise), libelle, type (TypePointDeVente), adresse, ville, telephone, est_depot, actif, created_at, updated_at.  
- **Role** : id, entreprise_id (nullable = rôle système), code (unique par entreprise), libelle.  
- **Permission** : id, module, action, libelle. Unicité (module, action).  
- **PermissionRole** : liaison rôle–permission (role_id, permission_id).  
- **Utilisateur** : id, entreprise_id, point_de_vente_id, role_id, login (unique par entreprise), mot_de_passe_hash, email, nom, prenom, telephone, actif, derniere_connexion_at, created_at, updated_at.  
- **AffectationUtilisateurPdv** : id, utilisateur_id, point_de_vente_id, est_principal. Unicité (utilisateur_id, point_de_vente_id).

**Opérations (résumé des routes et comportements)**

- **GET /parametrage/entreprises** : Liste paginée (skip, limit), filtres actif_only, search. **Nominal** : 200 + liste. **Exceptions** : 401 si non authentifié.  
- **GET /parametrage/entreprises/{id}** : **Nominal** : 200 + EntrepriseResponse. **Exceptions** : 404 (ENTREPRISE_NOT_FOUND).  
- **POST /parametrage/entreprises** : **Nominal** : 201 + entreprise créée. **Exceptions** : 400 si code ou NIU déjà existant (ENTREPRISE_CODE_EXISTS, ENTREPRISE_NIU_EXISTS), 400 si pays/devise invalide (ENTREPRISE_PAYS_INVALIDE, ENTREPRISE_DEVISE_INVALIDE).  
- **PATCH /parametrage/entreprises/{id}** : Mise à jour partielle. **Exceptions** : 404, 409 si conflit d'unicité.  
- **DELETE /parametrage/entreprises/{id}** : Soft delete. **Nominal** : 204. **Exceptions** : 404.  
- **Devises** : GET liste/détail, POST, PATCH. **Exceptions** : 404 (DEVISE_NOT_FOUND), 400/409 (DEVISE_CODE_VIDE, DEVISE_CODE_EXISTS).  
- **Taux de change** : GET liste (filtres devise_from_id, devise_to_id), GET/POST. **Exceptions** : 404 (TAUX_CHANGE_NOT_FOUND), 400 (TAUX_CHANGE_SAME_DEVISE, TAUX_CHANGE_INVALID).  
- **Points de vente** : GET par entreprise, GET/POST/PATCH par id. **Exceptions** : 404 (POINT_VENTE_NOT_FOUND), 409 (POINT_VENTE_CODE_EXISTS).  
- **Rôles, Permissions, Utilisateurs, Affectations** : CRUD avec 404 si non trouvé, 409 si unicité (ROLE_CODE_EXISTS, UTILISATEUR_LOGIN_EXISTS, AFFECTATION_ALREADY_EXISTS, etc.).

---

### Module Stock

**Vue d'ensemble**  
Gestion des niveaux de stock par dépôt × produit × variante (optionnelle), des mouvements (entrée, sortie, transfert, inventaire) et des alertes (sous seuil min / au-dessus seuil max). Dépend des modules Achats (Depot) et Catalogue (Produit, VarianteProduit). Messages dans `stock.services.messages.Messages`.

**Modélisation**

- **Enums** : `TypeMouvementStock` : entree, sortie, transfert, inventaire. `ReferenceTypeMouvement` : reception, bon_livraison, manuel, inventaire, transfert.
- **Stock** (table `stocks`) : id, depot_id (FK depots), produit_id (FK produits), variante_id (FK variantes_produits, nullable), quantite (Decimal 18,3, défaut 0), unite_id (FK unites_mesure), updated_at. **Contrainte d'unicité** : (depot_id, produit_id, variante_id).
- **MouvementStock** (table `mouvements_stock`) : id, type_mouvement, depot_id, depot_dest_id (nullable, pour transfert), produit_id, variante_id, quantite, date_mouvement, reference_type, reference_id, notes, created_by_id, created_at.

**Règles métier** : Le produit doit avoir `gerer_stock=True`. Pour une variante, `stock_separe` doit être True. Transfert : depot_dest_id obligatoire et ≠ depot_id. Sortie/transfert : quantité disponible suffisante. Inventaire : remplacement de la quantité par la valeur envoyée.

**Opérations**

| Méthode | Route | Scénario nominal | Exceptions |
|--------|-------|------------------|------------|
| GET | `/stock/depots/{depot_id}/stocks` | 200 + liste des stocks du dépôt (paginée) | 404 si dépôt inexistant (DEPOT_NOT_FOUND) |
| GET | `/stock/depots/{depot_id}/stocks/{stock_id}` | 200 + StockResponse | 404 si stock absent ou stock.depot_id ≠ depot_id (STOCK_NOT_FOUND) |
| GET | `/stock/depots/{depot_id}/produits/{produit_id}/quantite` | 200 + QuantiteStockResponse (quantite = 0 si pas de ligne) | 404 si dépôt ou produit inexistant |
| GET | `/stock/produits/{produit_id}/stocks` | 200 + liste stocks par produit | 404 (PRODUIT_NOT_FOUND) |
| GET | `/stock/mouvements` | 200 + liste mouvements (filtres : depot_id, produit_id, type_mouvement, date_from, date_to) | 400 si date_from/date_to format ISO invalide (DATE_MOUVEMENT_INVALIDE) |
| GET | `/stock/mouvements/{id}` | 200 + MouvementStockResponse | 404 (MOUVEMENT_NOT_FOUND) |
| POST | `/stock/mouvements` | Création mouvement + mise à jour des stocks → 201 + mouvement | 400 type_mouvement ou reference_type invalide ; 400 produit sans gerer_stock (PRODUIT_STOCK_NON_GERE) ; 400 variante sans stock séparé ; 400 transfert sans depot_dest ou même dépôt ; 400 quantité insuffisante (QUANTITE_INSUFFISANTE) ; 404 DEPOT_NOT_FOUND, PRODUIT_NOT_FOUND, VARIANTE_NOT_FOUND |
| GET | `/stock/alertes` | 200 + liste alertes (quantite &lt; seuil_alerte_min ou &gt; seuil_alerte_max), optionnellement filtrée par depot_id | — |

---

### Module Trésorerie

**Vue d'ensemble**  
Modes de paiement, comptes de trésorerie (caisse / bancaire), règlements (clients ou fournisseurs) liés aux factures. Dépend de Paramétrage, Partenaires (tiers), Commercial (factures), Achats (factures fournisseurs). Messages dans `tresorerie.services.messages.Messages`.

**Modélisation**

- **Enums** : `TypeCompteTresorerie` (caisse, bancaire), `TypeReglement` (client, fournisseur).
- **ModePaiement** : id, entreprise_id, code (unique par entreprise), libelle, actif.
- **CompteTresorerie** : id, entreprise_id, type_compte (caisse|bancaire), libelle (unique par entreprise), devise_id, actif.
- **Reglement** : id, entreprise_id, type_reglement (client|fournisseur), facture_id (nullable, client), facture_fournisseur_id (nullable, fournisseur), tiers_id, montant, date_reglement, mode_paiement_id, compte_tresorerie_id, reference, notes, created_by_id, created_at.

**Règles** : type_reglement=client ⇒ facture_id obligatoire ; type_reglement=fournisseur ⇒ facture_fournisseur_id obligatoire. Montant strictement positif.

**Opérations (résumé)**  
- **Modes de paiement** : GET liste (entreprise_id, actif_only), GET/POST/PATCH. **Exceptions** : 404 (MODE_PAIEMENT_NOT_FOUND), 400/409 (MODE_PAIEMENT_CODE_VIDE, MODE_PAIEMENT_CODE_EXISTS).  
- **Comptes trésorerie** : GET liste, GET/POST/PATCH. **Exceptions** : 404 (COMPTE_TRESORERIE_NOT_FOUND, DEVISE_NOT_FOUND), 400 (TYPE_COMPTE_INVALIDE).  
- **Règlements** : GET liste, GET/POST/PATCH. **Exceptions** : 404 (REGLEMENT_NOT_FOUND, TIERS_NOT_FOUND, FACTURE_NOT_FOUND, FACTURE_FOURNISSEUR_NOT_FOUND) ; 400 (TYPE_REGLEMENT_INVALIDE, REGLEMENT_FACTURE_OBLIGATOIRE, REGLEMENT_FACTURE_FOURNISSEUR_OBLIGATOIRE, REGLEMENT_MONTANT_POSITIF).

---

### Module Comptabilité

**Vue d'ensemble**  
Plan comptable (comptes), journaux, périodes comptables (clôture), écritures et lignes (débit/crédit). Conforme OHADA/CEMAC. Messages dans `comptabilite.services.messages.Messages`.

**Modélisation**

- **SensCompte** : debit, credit.
- **CompteComptable** : id, entreprise_id, numero (unique par entreprise), libelle, sens_normal (debit|credit), actif.
- **JournalComptable** : id, entreprise_id, code (unique par entreprise), libelle, actif.
- **PeriodeComptable** : id, entreprise_id, date_debut, date_fin, libelle, cloturee. Unicité (entreprise_id, date_debut).
- **EcritureComptable** : id, entreprise_id, journal_id, periode_id, date_ecriture, numero_piece, libelle, created_by_id, created_at.
- **LigneEcriture** : id, ecriture_id, compte_id, libelle_ligne, debit, credit (Decimal 18,2).

**Règles** : Écriture équilibrée (somme débit = somme crédit) ; au moins 2 lignes ; montant total > 0 ; date_ecriture dans la période ; période non clôturée pour créer/modifier une écriture. date_fin > date_debut pour une période.

**Opérations (résumé)**  
- **Comptes** : GET liste (entreprise_id, actif_only), GET/POST/PATCH. **Exceptions** : 404 (COMPTE_COMPTABLE_NOT_FOUND), 400/409 (COMPTE_NUMERO_VIDE, COMPTE_NUMERO_EXISTS, SENS_COMPTE_INVALIDE).  
- **Journaux** : GET liste, GET/POST/PATCH. **Exceptions** : 404 (JOURNAL_COMPTABLE_NOT_FOUND), 400/409 (JOURNAL_CODE_VIDE, JOURNAL_CODE_EXISTS).  
- **Périodes** : GET liste, GET/POST/PATCH. **Exceptions** : 404 (PERIODE_COMPTABLE_NOT_FOUND), 400 (PERIODE_DATES_INCOHERENTES).  
- **Écritures** : GET liste, GET/POST/PATCH. **Exceptions** : 404 (ECRITURE_COMPTABLE_NOT_FOUND) ; 400 (PERIODE_CLOTUREE, PERIODE_DATE_HORS_PERIODE, ECRITURE_LIGNES_MIN, ECRITURE_NON_EQUILIBREE, ECRITURE_NUMERO_PIECE_VIDE, ECRITURE_MONTANT_ZERO).

---

### Module Ressources humaines (RH)

**Vue d'ensemble**  
Structure (départements, postes, types de contrat), employés (CNPS, NIU, salaire, devise), congés (types, demandes, soldes), objectifs, taux de commission, commissions, avances. Conforme au contexte camerounais (Code du travail, CNPS, XAF). Messages dans `rh.services.messages.Messages`.

**Modélisation**

- **Departement** : id, entreprise_id, code (unique par entreprise), libelle, actif.
- **Poste** : id, entreprise_id, departement_id (nullable), code (unique par entreprise), libelle, actif.
- **TypeContrat** : id, entreprise_id, code (unique par entreprise), libelle, actif.
- **Employe** : id, entreprise_id, utilisateur_id (nullable), departement_id, poste_id, type_contrat_id, matricule (unique par entreprise), nom, prenom, date_naissance, lieu_naissance, genre, nationalite, niu, numero_cnps, email, telephone, adresse, date_embauche, salaire_base, devise_id, compte_bancaire, banque, actif.
- **TypeConge** : id, entreprise_id, code (unique), libelle, paye, actif.
- **DemandeConge** : id, employe_id, type_conge_id, date_debut, date_fin, nombre_jours, statut (brouillon, en_attente, approuve, refuse), motif, commentaire_refus, approuve_par_id, date_decision.
- **SoldeConge** : id, employe_id, type_conge_id, annee, droits_acquis, jours_pris. Unicité (entreprise_id, employe_id, type_conge_id, annee).
- **Objectif** : id, employe_id, libelle, date_debut, date_fin, montant_cible, atteint.
- **TauxCommission** : id, entreprise_id, code (unique), libelle, taux_pct, actif.
- **Commission** : id, employe_id, taux_commission_id, date_debut, date_fin, montant, libelle, payee.
- **Avance** : id, employe_id, date_avance, montant, motif, rembourse, created_by_id.

**Règles** : date_fin ≥ date_debut pour demandes de congé, objectifs et commissions. Statut demande congé : brouillon, en_attente, approuve, refuse.

**Opérations (résumé)**  
Toutes les ressources exposent GET liste (filtres entreprise_id, actif_only, etc.), GET/POST/PATCH. **Exceptions** : 404 pour toute ressource non trouvée (EMPLOYE_NOT_FOUND, DEPARTEMENT_NOT_FOUND, etc.) ; 400/409 pour conflits d'unicité (code/matricule existe déjà) et validations de dates ou statuts (DEMANDE_CONGE_DATES, DEMANDE_CONGE_JOURS, DEMANDE_CONGE_STATUT_INVALIDE, OBJECTIF_DATES, COMMISSION_DATES).

---

### Module Paie

**Vue d'ensemble**  
Périodes de paie (mois/année, clôture), types d'éléments de paie (gain / retenue), bulletins de paie et lignes. Contexte camerounais (CNPS, IR, XAF). Dépend de Paramétrage (entreprises) et RH (employes).

**Modélisation**

- **PeriodePaie** : id, entreprise_id, annee, mois (1–12), date_debut, date_fin, cloturee. Unicité (entreprise_id, annee, mois).
- **TypeElementPaie** : id, entreprise_id, code (unique), libelle, type (gain|retenue), ordre_affichage, actif.
- **BulletinPaie** : id, entreprise_id, employe_id, periode_paie_id, salaire_brut, total_gains, total_retenues, net_a_payer, statut (brouillon, valide, paye), date_paiement. Unicité (entreprise_id, employe_id, periode_paie_id).
- **LigneBulletinPaie** : id, bulletin_paie_id, type_element_paie_id, libelle, type (gain|retenue), montant, ordre.

**Opérations (résumé)**  
GET liste / GET détail / POST / PATCH pour periodes, types-element, bulletins. **Exceptions** : 404 si ressource inexistante ; 400/409 si unicité (ex. bulletin déjà existant pour employé + période) ou période clôturée.

---

### Module Immobilisations

**Vue d'ensemble**  
Catégories d'immobilisations (durée/taux d'amortissement) et actifs (valeur, date d'acquisition, comptes comptables optionnels). Dépend de Paramétrage (entreprises) et Comptabilité (comptes). Messages dans `immobilisations.services.messages.Messages`.

**Modélisation**

- **CategorieImmobilisation** : id, entreprise_id, code (unique par entreprise), libelle, duree_amortissement_annees, taux_amortissement (nullable).
- **Immobilisation** : id, entreprise_id, categorie_id, compte_comptable_id, compte_amortissement_id (nullable), code (unique par entreprise), designation, date_acquisition, valeur_acquisition, duree_amortissement_annees, date_mise_en_service, notes, actif.
- **LigneAmortissement** : id, immobilisation_id, annee, mois (nullable), montant_dotation, cumul_amortissement, valeur_nette, ecriture_comptable_id.

**Opérations (résumé)**  
- **Catégories** : GET liste (entreprise_id), GET/POST/PATCH. **Exceptions** : 404 (CATEGORIE_NOT_FOUND), 409 (CATEGORIE_CODE_EXISTS).  
- **Actifs** : GET liste (entreprise_id, categorie_id optionnel), GET/POST/PATCH. **Exceptions** : 404 (IMMOBILISATION_NOT_FOUND, CATEGORIE_NOT_FOUND), 409 (IMMOBILISATION_CODE_EXISTS).

---

### Module Système

**Vue d'ensemble**  
Paramètres applicatifs (clé/valeur par entreprise et catégorie), journal d'audit (traçabilité des actions), notifications (in-app), licences logicielles (validité, type, prolongations).

**Modélisation**

- **ParametreSysteme** : id, entreprise_id, categorie, cle, valeur, description. Unicité (entreprise_id, categorie, cle).
- **JournalAudit** : id, entreprise_id, utilisateur_id, action (create, update, delete, login, logout), module, entite_type, entite_id, details (JSONB), ip_address, user_agent, created_at.
- **Notification** : id, utilisateur_id, titre, message, lue, entite_type, entite_id, created_at.
- **LicenceLogicielle** : id, entreprise_id, cle_licence (format XXXXX-XXXXX-...), type_licence (standard, premium, trial), date_debut, date_fin, actif, nombre_prolongations, date_activation.

**Opérations (résumé)**  
GET/POST/PATCH pour parametres, GET/POST pour audit, GET/POST/PATCH pour notifications et licence. **Exceptions** : 404 si ressource inexistante ; 400 en cas de format ou règle métier invalide.

---

### Module Rapports

**Vue d'ensemble**  
Agrégation de données pour le chiffre d'affaires (période) et le tableau de bord (synthèse CA, nombre de factures, commandes, employés actifs). Dépend de Paramétrage (EntrepriseRepository), Commercial (FactureService, CommandeService), RH (EmployeService).

**Modélisation**  
Aucune entité propre : schémas de réponse uniquement (`ChiffreAffairesPeriode`, `SyntheseDashboard`).

**Opérations**

- **GET /rapports/chiffre-affaires**  
  - **Paramètres** : entreprise_id, date_debut, date_fin.  
  - **Scénario nominal** : Entreprise existante → somme des montant_ttc des factures dont date_facture ∈ [date_debut, date_fin] → 200 + ChiffreAffairesPeriode (entreprise_id, date_debut, date_fin, montant_total_ttc, nombre_factures).  
  - **Exceptions** : 404 si entreprise inexistante (« L'entreprise indiquée n'existe pas. »).

- **GET /rapports/dashboard**  
  - **Paramètres** : entreprise_id, date_debut (optionnel), date_fin (optionnel).  
  - **Scénario nominal** : Entreprise existante → agrégation factures (CA et nb sur la période si dates fournies), nombre total de commandes, nombre d'employés actifs → 200 + SyntheseDashboard (entreprise_id, periode_label, ca_periode, nb_factures, nb_commandes, nb_employes_actifs).  
  - **Exceptions** : 404 si entreprise inexistante.

---

### Module Catalogue

**Vue d'ensemble**  
Référentiels produits : unités de mesure, taux TVA, familles de produits (hiérarchie), conditionnements, produits (famille, unités, TVA, seuils alerte stock), variantes, liaisons produit–conditionnement, canaux de vente, prix (canal/PDV, périodes). Dépend de Paramétrage (entreprises).

**Modélisation (résumé)**  
Entités typiques : UniteMesure, TauxTva, FamilleProduit (parent_id optionnel), Conditionnement, Produit (famille_id, unite_vente_id, taux_tva_id, gerer_stock, seuil_alerte_min, seuil_alerte_max), VarianteProduit (produit_id, stock_separe), ProduitConditionnement, CanalVente, PrixProduit (canal/PDV, dates). Contraintes d'unicité et clés étrangères selon le schéma métier.

**Opérations (résumé)**  
CRUD sur chaque ressource (unites-mesure, taux-tva, familles-produits, conditionnements, produits, variantes, produits-conditionnements, canaux-vente, prix). **Scénarios nominaux** : 200/201 + corps de réponse. **Exceptions** : 404 si ressource non trouvée, 400/409 pour validations (code déjà existant, références invalides).

---

### Module Partenaires

**Vue d'ensemble**  
Types de tiers, tiers (clients/fournisseurs : code, NIU, canal, limite crédit, délai paiement, etc.), contacts. Soft delete sur les tiers.

**Modélisation (résumé)**  
TypeTiers ; Tiers (entreprise_id, type_tiers_id, code, niu, pays, canal_vente, limite_credit, délai_paiement, actif, deleted_at) ; Contact (tiers_id, ...). Contraintes d'unicité (ex. code par entreprise).

**Opérations (résumé)**  
CRUD types-tiers, tiers, contacts. **Nominal** : 200/201/204. **Exceptions** : 404 (tiers ou contact non trouvé), 409 (code/NIU déjà utilisé), 400 (données invalides).

---

### Module Commercial

**Vue d'ensemble**  
États de document (par type : devis, commande, facture, BL), devis, commandes, factures (facture, avoir, proforma, duplicata), bons de livraison. Montants HT/TVA/TTC, devise, échéances.

**Modélisation (résumé)**  
EtatDocument ; Devis (client_id, montants, devise_id) ; Commande (devis_id optionnel) ; Facture (type_facture, montant_ht, tva, montant_ttc, date_facture, echeance) ; BonLivraison (lien commande/facture). Relations avec Partenaires (tiers), Catalogue (lignes), Paramétrage (entreprise, devise).

**Opérations (résumé)**  
CRUD etats-document, devis, commandes, factures, bons-livraison. **Nominal** : 200/201. **Exceptions** : 404 (document ou référence non trouvé), 400 (montants incohérents, dates), 409 (numérotation, conflits).

---

### Module Achats

**Vue d'ensemble**  
Commandes fournisseurs (fournisseur, dépôt optionnel, état, devise), réceptions (par commande, dépôt, état : brouillon/validée/annulée), factures fournisseurs (statut paiement : non_paye/partiel/paye). Dépend de Partenaires (tiers), Catalogue, Paramétrage. Module Stock utilise les dépôts (Achats).

**Modélisation (résumé)**  
Depot (entreprise_id, libelle, ...) ; CommandeFournisseur (fournisseur_id, depot_id, état, devise_id) ; Reception (commande_id, depot_id, état) ; FactureFournisseur (statut_paiement, montant_restant_du). Contraintes et états selon le schéma métier.

**Opérations (résumé)**  
CRUD commandes-fournisseurs, receptions, factures-fournisseurs. **Nominal** : 200/201. **Exceptions** : 404 (commande, réception, facture ou fournisseur non trouvé), 400 (états incompatibles, montants), 409 (réception déjà validée, etc.).

---

## Configuration

Le fichier **`.env`** à la racine est chargé par **pydantic-settings**. Noms des variables en MAJUSCULES.

### Obligatoires

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | URL PostgreSQL **asynchrone** pour l’API (ex. `postgresql+asyncpg://user:pass@localhost:5432/gesco`) |
| `DATABASE_URL_SYNC` | URL PostgreSQL **synchrone** pour Alembic / scripts (ex. `postgresql://user:pass@localhost:5432/gesco`) |
| `SECRET_KEY` | Clé secrète JWT (au moins 32 caractères) |

### Optionnelles (valeurs par défaut)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `APP_NAME` | Gesco | Nom de l’application |
| `APP_ENV` | development | development / staging / production |
| `DEBUG` | True | Mode debug |
| `HOST` | 0.0.0.0 | Adresse d’écoute |
| `PORT` | 8000 | Port |
| `API_V1_PREFIX` | /api/v1 | Préfixe des routes API |
| `TIMEZONE` | Africa/Douala | Fuseau horaire |
| `FRONTEND_URL` | http://localhost:3000 | URL frontend (CORS, redirections) |
| `DATABASE_POOL_SIZE` | 5 | Taille du pool de connexions |
| `DATABASE_MAX_OVERFLOW` | 10 | Connexions supplémentaires |
| `DATABASE_ECHO` | False | Logger les requêtes SQL |
| `ALGORITHM` | HS256 | Algorithme JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | Durée de validité du token (minutes) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Durée token de rafraîchissement |
| `BCRYPT_ROUNDS` | 12 | Coût bcrypt |
| `RATE_LIMIT_PER_MINUTE` | 60 | Limite requêtes/minute par IP (0 = désactivé) |
| `CORS_ORIGINS` | * | Origines autorisées (virgules) |
| `CORS_ALLOW_CREDENTIALS` | True | Cookies / auth |
| `DEFAULT_PAGE_SIZE` | 20 | Éléments par page |
| `MAX_PAGE_SIZE` | 100 | Éléments max par page |
| `DEFAULT_LOCALE` | fr_FR | Locale |
| `DEFAULT_CURRENCY_CODE` | XAF | Devise par défaut |
| `DATE_FORMAT` | %d/%m/%Y | Format date |
| `DATETIME_FORMAT` | %d/%m/%Y %H:%M | Format date+heure |
| `MEDIA_ROOT` | ./media | Dossier uploads |
| `MAX_UPLOAD_SIZE` | 10485760 | Taille max fichier (octets, 10 Mo) |
| `REDIS_URL` | (vide) | URL Redis (vide = pas de Redis) |
| `LOG_LEVEL` | INFO | DEBUG / INFO / WARNING / ERROR |
| `LOG_FORMAT` | json | json / text |
| `LOG_FILE` | (vide) | Fichier de log (vide = console) |

---

## Installation et lancement

```bash
git clone <url-du-repo>
cd Gesco

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

Créer le fichier **`.env`** à la racine avec au minimum : `DATABASE_URL`, `DATABASE_URL_SYNC`, `SECRET_KEY`.

```bash
# Développement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **API** : `http://localhost:8000`  
- **Swagger (OpenAPI)** : `http://localhost:8000/docs`  
- **ReDoc** : `http://localhost:8000/redoc`  
- **Santé** : `http://localhost:8000/health`  

---

## Authentification

1. **POST** `/api/v1/auth/login`  
   Corps JSON : `{ "entreprise_id": 1, "login": "utilisateur", "password": "motdepasse" }`  
   Réponse : `{ "access_token": "<jwt>", "token_type": "bearer" }`

2. Pour toute autre route protégée, envoyer le token dans le header :  
   **Authorization: Bearer &lt;access_token&gt;**

En cas d’utilisateur inactif ou de mot de passe incorrect, l’API renvoie **401 Unauthorized** avec un message explicite.

---

## Conformité réglementaire

- **Cameroun / CEMAC** : Régimes fiscaux (CGI) : informel, libératoire, forfait, réel simplifié, réel normal. NIU (DGI) pour entreprises et tiers. TVA (taux courants 0, 9.75, 10, 19.25 % ; Loi 2026 : 17.5 %). Devise légale CEMAC (XAF). Conservation des pièces (ordre de grandeur 10 ans, OHADA / usage).
- **International** : Codes pays ISO 3166-1 alpha-3 (ex. CMR). Codes devises ISO 4217 (XAF, EUR, USD). Montants en **Decimal**. Facturation : structure permettant les mentions utiles (identification, numéro, date, HT/TVA/TTC, conditions de paiement).

Le référentiel partagé (constantes et helpers) est dans **`app/shared/regulations.py`** (ex. `PAYS_DEFAULT_CMR`, `DEVISE_DEFAULT_XAF`, `NIU_MAX_LENGTH`, `is_pays_code_valide`, `is_devise_code_valide`). Les validations métier sont appliquées dans les services des modules concernés.

---

## Structure du projet

```
Gesco/
├── app/
│   ├── main.py                    # Point d'entrée FastAPI, CORS, exceptions, lifespan, routeurs
│   ├── config.py                  # Settings (pydantic-settings, .env)
│   ├── core/
│   │   ├── database.py            # Moteur async, session, Base SQLAlchemy
│   │   ├── dependencies.py        # DbSession (injection session)
│   │   ├── exceptions.py         # AppHTTPException, NotFound, Conflict, BadRequest, Unauthorized, Forbidden
│   │   ├── security.py           # JWT (create/decode), bcrypt (hash/verify)
│   │   └── service_base.py       # BaseService (_raise_*, _validate_enum)
│   ├── shared/
│   │   ├── regulations.py        # Référentiel Cameroun / international (pays, devise, NIU, TVA)
│   │   ├── schemas/
│   │   │   └── common.py         # Pagination, PaginatedResponse
│   │   └── utils/                # Calculs, audit, numérotation
│   └── modules/
│       ├── auth/                 # Login JWT
│       ├── parametrage/          # Entreprises, devises, PDV, rôles, permissions, utilisateurs
│       ├── catalogue/            # Produits, familles, conditionnements, prix, canaux
│       ├── partenaires/          # Tiers, contacts
│       ├── commercial/           # Devis, commandes, factures, BL
│       ├── achats/               # Commandes fournisseurs, réceptions, factures fournisseurs
│       ├── stock/                # Stocks, mouvements, alertes
│       ├── tresorerie/           # Modes paiement, comptes, règlements
│       ├── comptabilite/         # Comptes, journaux, périodes, écritures
│       ├── rh/                   # Départements, postes, employés, congés, objectifs, commissions, avances
│       ├── paie/                 # Périodes paie, types élément, bulletins
│       ├── immobilisations/      # Catégories, actifs
│       ├── systeme/              # Paramètres, audit, notifications, licence
│       └── rapports/             # Chiffre d'affaires, dashboard
├── requirements.txt
├── .env                          # À créer (non versionné)
├── .gitignore
└── README.md
```

Dans chaque module métier : **models.py** (entités ORM), **schemas.py** (Create/Update/Response), **repositories/** (un fichier par agrégat), **services/** (un fichier par agrégat + **base.py**, **messages.py**), **router.py** (routes FastAPI). Les messages d’erreur (404, 400, 409) sont centralisés dans **messages.py** et utilisés via la base de service.

---

## Migrations et tests

**Alembic** (URL synchrone dans `.env`) :

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

**Tests** :

```bash
pytest
pytest --cov=app
```

---

## Licence

Projet propriétaire – usage interne.
