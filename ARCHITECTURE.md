# Architecture du projet Gesco (Clean Architecture)

## Principes

- **Séparation des couches** : Domain → Application → Infrastructure → Presentation.
- **Règle des dépendances** : les couches internes ne dépendent pas des couches externes.
- **Injection de dépendances** : les use cases dépendent d’abstractions (repositories), pas du détail technique (SQLAlchemy).

---

## Couches

### 1. Domain (`app/domain/`)

- **Rôle** : Entités métier et exceptions domaine (sans HTTP, sans DB).
- **Contenu** : `exceptions.py` (DomainNotFoundError, DomainConflictError, DomainValidationError).
- **Dépendances** : Aucune (couche la plus interne).

### 2. Application – Use Cases (`app/modules/*/services/`)

- **Rôle** : Orchestration métier, validation, messages. Pas d’accès SQL direct.
- **Contenu** : Classes de service (ex. `EntrepriseService`, `ProduitService`, `TiersService`, `DevisService`, `CommandeFournisseurService`) qui utilisent les **repositories** et les **messages**. Héritent de `BaseService` (core) ou de la base métier (Paramétrage/Catalogue/Partenaires/Commercial/Achats).
- **Dépendances** : Core (exceptions HTTP, BaseService), Repositories (accès données), Schemas (DTO entrée/sortie).

### 3. Infrastructure – Repositories (`app/modules/parametrage/repositories/`, `app/modules/catalogue/repositories/`, `app/modules/partenaires/repositories/`, `app/modules/commercial/repositories/`, `app/modules/achats/repositories/`)

- **Rôle** : Accès aux données (SQLAlchemy). Encapsulation des requêtes.
- **Contenu** : Une classe par agrégat (ex. `EntrepriseRepository`, `ProduitRepository`) avec `find_by_id`, `find_all`, `add`, `update`, etc.
- **Dépendances** : `app.core.database` (session), modèles ORM du module concerné.

### 4. Presentation – API (`app/main.py`, `app/modules/*/router.py`)

- **Rôle** : HTTP, routes, sérialisation (Pydantic), gestion des erreurs.
- **Contenu** : FastAPI app, routeurs, dépendances (`get_db`, `get_current_user`), gestionnaires d’exceptions (réponse JSON avec `detail` et `code`).
- **Dépendances** : Application (services), Core (config, security, exceptions).

### 5. Core (`app/core/`)

- **Rôle** : Technique partagé (DB, sécurité, config, exceptions HTTP, base des services).
- **Contenu** : `config.py`, `database.py`, `security.py`, `exceptions.py`, `dependencies.py`, `service_base.py` (BaseService : session DB + _raise_*).
- **Dépendances** : Aucun module métier (évite les imports circulaires).

### 6. Shared (`app/shared/`)

- **Rôle** : Utilitaires et schémas partagés (pagination, réponses génériques).
- **Contenu** : `schemas/common.py` (PaginationParams, PaginatedResponse, `build_paginated_response`), `utils/`.
- **Dépendances** : Aucun module métier.

---

## Flux typique (ex. créer une entreprise)

1. **Router** : `POST /parametrage/entreprises` → reçoit le body (schema), injecte `DbSession` et `CurrentUser`.
2. **Service** : `EntrepriseService(db).create(data)` → valide (code, NIU), utilise `EntrepriseRepository(db)` pour `exists_by_code`, `add`.
3. **Repository** : `EntrepriseRepository.add(entity)` → `session.add`, `flush`, `refresh`.
4. **Retour** : le service renvoie l’entité ; FastAPI sérialise avec `EntrepriseResponse`.

---

## Bonnes pratiques appliquées

- **Messages d’erreur** : centralisés dans `services/messages.py` (pas de chaînes en dur).
- **Exceptions** : `AppHTTPException` avec champ `code` pour le client ; gestionnaire global dans `main.py`.
- **Lifespan** : fermeture propre du pool DB au shutdown (`engine.dispose()`).
- **DI** : `DbSession` dans `core.dependencies` ; `CurrentUser` dans `parametrage.dependencies`. Tous les routeurs (auth, parametrage, catalogue) les réutilisent.
- **Auth** : Routes paramétrage et catalogue protégées par `CurrentUser` ; `get_current_user` utilise `UtilisateurRepository` (pas de SQL direct dans les dépendances).
- **Pas d’import circulaire** : core ne connaît pas les modules ; les services connaissent les repositories et les schémas, pas les routeurs.
