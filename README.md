# Gesco

**Système de gestion commerciale** – API backend multi-entreprises pour le marché camerounais. Couvre le cycle complet : paramétrage, catalogue, partenaires (clients/fournisseurs), ventes (devis, commandes, factures, bons de livraison) et achats (commandes fournisseurs, réceptions, factures fournisseurs). Conforme au droit camerounais (CGI, DGI, NIU, CEMAC) et aux normes internationales (ISO 3166, ISO 4217).

---

## Sommaire

- [Présentation](#présentation)
- [Fonctionnalités détaillées](#fonctionnalités-détaillées)
- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Modules et API](#modules-et-api)
- [Configuration](#configuration)
- [Installation et lancement](#installation-et-lancement)
- [Authentification](#authentification)
- [Conformité réglementaire](#conformité-réglementaire)
- [Structure du projet](#structure-du-projet)
- [Migrations et tests](#migrations-et-tests)

---

## Présentation

Gesco est une **API REST** construite avec **FastAPI** et **SQLAlchemy** (asynchrone). Elle sert de backend à une application de gestion commerciale destinée au contexte camerounais : multi-entreprises (multi-tenant), multi points de vente, devises (XAF prioritaire), régimes fiscaux (CGI), identification des contribuables (NIU DGI). L’architecture est modulaire (Auth, Paramétrage, Catalogue, Partenaires, Commercial, Achats), avec une couche **services** (règles métier, validations, messages d’erreur centralisés) et une couche **repositories** (accès données). Les réponses d’erreur sont normalisées (404, 400, 409, 401, 500) avec un format JSON cohérent.

---

## Fonctionnalités détaillées

| Domaine | Description |
|--------|-------------|
| **Authentification** | Login par entreprise + login + mot de passe ; renvoi d’un token JWT (Bearer). Vérification utilisateur actif et hash bcrypt. |
| **Paramétrage** | Entreprises (NIU, régime fiscal, pays, devise principale), devises (ISO 4217), taux de change, points de vente (par entreprise), rôles, permissions (module/action), liaison permissions–rôles, utilisateurs (par entreprise, rôle, PDV), affectations utilisateur ↔ point de vente. Soft delete entreprise. |
| **Catalogue** | Unités de mesure, taux de TVA (CGI), familles de produits (hiérarchie), conditionnements, produits (famille, unités, TVA, seuils alerte), variantes produit, liaisons produit–conditionnement, canaux de vente (par entreprise), prix produits (canal / PDV, périodes). |
| **Partenaires** | Types de tiers (client, fournisseur, etc.), tiers – clients/fournisseurs (code, NIU, canal, limite crédit, délai paiement, mobile money, etc.), contacts (par tiers). Soft delete tiers. |
| **Commercial** | États document (par type : devis, commande, facture, BL), devis (client, montants HT/TVA/TTC, devise), commandes (lien devis optionnel), factures (types : facture, avoir, proforma, duplicata ; montants, échéance), bons de livraison (lien commande/facture). |
| **Achats** | Commandes fournisseurs (fournisseur, dépôt optionnel, état, devise), réceptions (par commande, dépôt, état : brouillon/validée/annulée), factures fournisseurs (statut paiement : non_paye/partiel/paye, montant restant dû). |

---

## Stack technique

- **Langage** : Python 3.12  
- **Framework** : FastAPI  
- **ORM** : SQLAlchemy 2 (mode asynchrone)  
- **Base de données** : PostgreSQL (pilote async : asyncpg ; synchrone : psycopg2 pour Alembic)  
- **Validation & config** : Pydantic, pydantic-settings, python-dotenv  
- **Authentification** : JWT (python-jose), passlib/bcrypt pour les mots de passe  
- **Migrations** : Alembic  
- **Tests** : pytest, pytest-asyncio, pytest-cov  
- **Client HTTP** : httpx  

---

## Architecture

Le projet suit une **Clean Architecture** simplifiée :

- **Présentation** : `main.py` (FastAPI, CORS, gestionnaires d’exceptions, enregistrement des routeurs), routes dans chaque module (`router.py`).
- **Application (use cases)** : services dans `modules/<module>/services/` – classes par agrégat (ex. `EntrepriseService`, `FactureService`), validations métier, messages d’erreur centralisés (`messages.py`), base commune par module (`base.py` héritant de `BaseService`).
- **Domaine** : modèles ORM dans `modules/<module>/models.py`, enums (régime fiscal, type facture, statuts, etc.).
- **Infrastructure** : accès aux données dans `modules/<module>/repositories/` – une classe repository par agrégat (find_by_id, find_all, add, update, exists_*, etc.).

Chaque module métier (Paramétrage, Catalogue, Partenaires, Commercial, Achats) expose :  
**models** → **schemas** (Create/Update/Response) → **repositories** → **services** → **router**.  
Les routes sont protégées par **CurrentUser** (JWT) sauf `/auth/login` et `/health`. La session base de données est injectée via **DbSession**.

---

## Modules et API

Toutes les routes sont préfixées par **`/api/v1`** (configurable). Résumé par préfixe :

### Authentification (`/api/v1/auth`)

| Méthode | Route | Description |
|--------|-------|-------------|
| POST | `/login` | Connexion (entreprise_id, login, password) → `access_token` |

---

### Paramétrage (`/api/v1/parametrage`)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/entreprises` | Liste entreprises (pagination, actif_only, search) |
| GET | `/entreprises/{id}` | Détail entreprise |
| POST | `/entreprises` | Création |
| PATCH | `/entreprises/{id}` | Mise à jour partielle |
| DELETE | `/entreprises/{id}` | Soft delete |
| GET | `/devises` | Liste devises |
| GET | `/devises/{id}` | Détail devise |
| POST | `/devises` | Création |
| PATCH | `/devises/{id}` | Mise à jour |
| GET | `/taux-change` | Liste taux de change (filtres devises) |
| GET | `/taux-change/{id}` | Détail |
| POST | `/taux-change` | Création |
| GET | `/entreprises/{id}/points-vente` | Points de vente d’une entreprise |
| GET | `/points-vente/{id}` | Détail point de vente |
| POST | `/points-vente` | Création |
| PATCH | `/points-vente/{id}` | Mise à jour |
| GET | `/roles` | Liste rôles (filtre entreprise optionnel) |
| GET | `/roles/{id}` | Détail rôle |
| POST | `/roles` | Création |
| PATCH | `/roles/{id}` | Mise à jour |
| GET | `/permissions` | Liste permissions (filtre module) |
| GET | `/permissions/{id}` | Détail |
| POST | `/permissions` | Création |
| POST | `/permissions-roles` | Associer permission à un rôle |
| DELETE | `/permissions-roles/{role_id}/{permission_id}` | Retirer permission d’un rôle |
| GET | `/entreprises/{id}/utilisateurs` | Utilisateurs d’une entreprise |
| GET | `/utilisateurs/{id}` | Détail utilisateur |
| POST | `/utilisateurs` | Création (mot de passe hashé) |
| PATCH | `/utilisateurs/{id}` | Mise à jour |
| GET | `/utilisateurs/{id}/affectations-pdv` | Affectations PDV d’un utilisateur |
| GET | `/points-vente/{id}/affectations` | Affectations d’un point de vente |
| POST | `/affectations-utilisateur-pdv` | Créer affectation |
| PATCH | `/affectations-utilisateur-pdv/{id}` | Mise à jour |
| DELETE | `/affectations-utilisateur-pdv/{id}` | Suppression |

**Entités** : Entreprise (NIU, régime fiscal, pays ISO, devise), Devise, TauxChange, PointDeVente, Role, Permission, PermissionRole, Utilisateur, AffectationUtilisateurPdv.

---

### Catalogue (`/api/v1/catalogue`)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST | `/unites-mesure`, `/unites-mesure/{id}` | CRUD unités de mesure |
| GET/POST | `/taux-tva`, `/taux-tva/{id}` | CRUD taux TVA |
| GET/POST | `/familles-produits`, `/familles-produits/{id}` | CRUD familles (parent optionnel) |
| GET/POST | `/conditionnements`, `/conditionnements/{id}` | CRUD conditionnements |
| GET/POST | `/produits`, `/produits/{id}` | CRUD produits |
| GET/POST | `/produits/{id}/variantes`, `/variantes/{id}` | Variantes par produit |
| GET/POST | `/produits/{id}/conditionnements`, `/produits-conditionnements/{id}` | Liaisons produit–conditionnement |
| GET/POST | `/canaux-vente`, `/canaux-vente/{id}` | CRUD canaux de vente |
| GET/POST | `/prix`, `/prix/{id}` | CRUD prix produits (canal/PDV, dates) |

**Entités** : UniteMesure, TauxTva, FamilleProduit, Conditionnement, Produit, VarianteProduit, ProduitConditionnement, CanalVente, PrixProduit.

---

### Partenaires (`/api/v1/partenaires`)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/types-tiers`, `/types-tiers/{id}` | CRUD types de tiers |
| GET | `/tiers` | Liste tiers (filtres entreprise, type, actif, search) |
| GET | `/tiers/{tiers_id}/contacts` | Contacts d’un tiers |
| GET/POST/PATCH/DELETE | `/tiers/{id}` | CRUD tiers (soft delete) |
| GET/POST/PATCH/DELETE | `/contacts`, `/contacts/{id}` | CRUD contacts |

**Entités** : TypeTiers, Tiers (NIU, pays ISO, canal_vente, limite crédit, etc.), Contact.

---

### Commercial (`/api/v1/commercial`)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET/POST/PATCH | `/etats-document`, `/etats-document/{id}` | CRUD états document |
| GET/POST/PATCH | `/devis`, `/devis/{id}` | CRUD devis |
| GET/POST/PATCH | `/commandes`, `/commandes/{id}` | CRUD commandes |
| GET/POST/PATCH | `/factures`, `/factures/{id}` | CRUD factures (type : facture/avoir/proforma/duplicata) |
| GET/POST/PATCH | `/bons-livraison`, `/bons-livraison/{id}` | CRUD bons de livraison |

**Entités** : EtatDocument, Devis, Commande, Facture (type_facture, montants HT/TVA/TTC), BonLivraison.

---

### Achats (`/api/v1/achats`)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/commandes-fournisseurs` | Liste (filtres entreprise, fournisseur) |
| GET | `/commandes-fournisseurs/{commande_id}/receptions` | Réceptions d’une commande |
| GET/POST/PATCH | `/commandes-fournisseurs`, `/commandes-fournisseurs/{id}` | CRUD commandes fournisseurs |
| GET/POST/PATCH | `/receptions`, `/receptions/{id}` | CRUD réceptions |
| GET/POST/PATCH | `/factures-fournisseurs`, `/factures-fournisseurs/{id}` | CRUD factures fournisseurs |

**Entités** : Depot (minimal, FK), CommandeFournisseur, Reception (etat : brouillon/validee/annulee), FactureFournisseur (statut_paiement : non_paye/partiel/paye).

---

### Santé (hors préfixe API)

| Méthode | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Santé de l’API (sans auth, sans DB) |

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
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

Créer le fichier **`.env`** avec au minimum `DATABASE_URL`, `DATABASE_URL_SYNC`, `SECRET_KEY`.

```bash
# Développement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **API** : `http://localhost:8000`  
- **Swagger** : `http://localhost:8000/docs`  
- **ReDoc** : `http://localhost:8000/redoc`  
- **Santé** : `http://localhost:8000/health`  

---

## Authentification

1. **POST** `/api/v1/auth/login`  
   Corps JSON : `{ "entreprise_id": 1, "login": "utilisateur", "password": "motdepasse" }`  
   Réponse : `{ "access_token": "<jwt>", "token_type": "bearer" }`

2. Pour toute autre route (paramétrage, catalogue, partenaires, commercial, achats), envoyer le token dans le header :  
   **Authorization: Bearer &lt;access_token&gt;**

En cas d’utilisateur inactif ou de mot de passe incorrect, l’API renvoie **401 Unauthorized** avec un message explicite.

---

## Conformité réglementaire

- **Cameroun** : Régimes fiscaux (CGI) : informel, libératoire, forfait, réel simplifié, réel normal. NIU (DGI) pour entreprises et tiers. TVA (taux courants 0, 9.75, 10, 19.25 % ; Loi 2026 : 17.5 %). Devise légale CEMAC (XAF). Conservation des pièces (ordre de grandeur 10 ans, OHADA / usage).
- **International** : Codes pays ISO 3166-1 alpha-3 (ex. CMR). Codes devises ISO 4217 (XAF, EUR, USD). Montants en **Decimal**. Facturation : structure permettant les mentions utiles (identification, numéro, date, HT/TVA/TTC, conditions de paiement).

Le référentiel partagé (constantes et helpers) est dans **`app/shared/regulations.py`** (ex. `PAYS_DEFAULT_CMR`, `DEVISE_DEFAULT_XAF`, `NIU_MAX_LENGTH`, `is_pays_code_valide`, `is_devise_code_valide`). Les validations métier (pays 3 lettres, devise 3 lettres, types facture, états réception/statut paiement) sont appliquées dans les services.

---

## Structure du projet

```
Gesco/
├── app/
│   ├── main.py                 # Point d'entrée FastAPI, CORS, exceptions, routeurs
│   ├── config.py               # Settings (pydantic-settings, .env)
│   ├── core/
│   │   ├── database.py         # Moteur async, session, Base SQLAlchemy
│   │   ├── dependencies.py     # DbSession (injection session)
│   │   ├── exceptions.py       # AppHTTPException, NotFound, Conflict, BadRequest, Unauthorized, Forbidden
│   │   ├── security.py         # JWT (create/decode), bcrypt (hash/verify)
│   │   └── service_base.py     # BaseService (_raise_*, _validate_enum)
│   ├── shared/
│   │   ├── regulations.py      # Référentiel Cameroun / international (pays, devise, NIU, TVA)
│   │   ├── schemas/
│   │   │   └── common.py       # Pagination, PaginatedResponse
│   │   └── utils/              # Calculs, audit, numérotation
│   └── modules/
│       ├── auth/
│       │   ├── router.py       # POST /login
│       │   ├── service.py     # Logique login (JWT, vérif mot de passe)
│       │   └── schemas.py     # LoginRequest, TokenResponse
│       ├── parametrage/
│       │   ├── models.py      # Entreprise, Devise, TauxChange, PointDeVente, Role, Permission, Utilisateur, Affectation...
│       │   ├── schemas.py     # Create/Update/Response par entité
│       │   ├── repositories/  # *Repository par agrégat
│       │   ├── services/      # *Service (entreprise, devise, point_vente, role, permission, utilisateur, affectation, taux_change)
│       │   ├── router.py      # Routes /parametrage/*
│       │   ├── dependencies.py # get_current_user (JWT → Utilisateur), CurrentUser
│       │   └── messages.py    # Messages d'erreur centralisés
│       ├── catalogue/
│       │   ├── models.py      # UniteMesure, TauxTva, FamilleProduit, Conditionnement, Produit, Variante, ProduitConditionnement, CanalVente, PrixProduit
│       │   ├── schemas.py
│       │   ├── repositories/
│       │   ├── services/
│       │   ├── router.py      # Routes /catalogue/*
│       │   └── messages.py
│       ├── partenaires/
│       │   ├── models.py      # TypeTiers, Tiers, Contact
│       │   ├── schemas.py
│       │   ├── repositories/
│       │   ├── services/
│       │   ├── router.py      # Routes /partenaires/*
│       │   └── messages.py
│       ├── commercial/
│       │   ├── models.py      # EtatDocument, Devis, Commande, Facture (TypeFacture), BonLivraison
│       │   ├── schemas.py
│       │   ├── repositories/
│       │   ├── services/
│       │   ├── router.py      # Routes /commercial/*
│       │   └── messages.py
│       └── achats/
│           ├── models.py      # Depot, CommandeFournisseur, Reception (StatutReception), FactureFournisseur (StatutPaiement)
│           ├── schemas.py
│           ├── repositories/
│           ├── services/
│           ├── router.py      # Routes /achats/*
│           └── messages.py
├── requirements.txt
├── .env                        # À créer (non versionné)
├── .gitignore
└── README.md
```

Dans chaque module métier, **repositories** et **services** sont organisés par entité (un fichier par agrégat) ; les **services** exposent en général `get_by_id`, `get_or_404`, `get_all` ou équivalent, `create`, `update`, et éventuellement `delete` / `delete_soft`. Les messages d’erreur (404, 400, 409) sont centralisés dans **messages.py** et utilisés via la base de service (`_raise_not_found`, `_raise_bad_request`, `_raise_conflict`).

---

## Migrations et tests

**Alembic** (URL synchrone) :

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
