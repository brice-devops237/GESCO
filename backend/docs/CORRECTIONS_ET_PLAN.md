# Corrections appliquées et plan – Incohérences Gesco

## Corrections effectuées

### 1. Module Immobilisations – Isolation multi-tenant (sécurité)

- **Listes** `/categories` et `/actifs` : `entreprise_id: int = Query(...)` remplacé par `ValidatedEntrepriseId` pour limiter l’accès à l’entreprise de l’utilisateur.
- **GET** catégorie, GET actif, GET lignes d’amortissement : vérification `ent.entreprise_id == current_user.entreprise_id` avant de renvoyer la ressource.
- **PATCH** catégorie, **PATCH** actif : même vérification avant mise à jour.
- **POST** catégorie, **POST** actif : vérification que `data.entreprise_id == current_user.entreprise_id`.

Fichier modifié : `app/modules/immobilisations/router.py`.

### 2. CI GitHub Actions – Répertoire de travail

- Ajout de `defaults.run.working-directory: backend` dans le job `lint` pour que toutes les commandes s’exécutent depuis `backend/` (où se trouvent `requirements.txt`, `app/`, `tests/`).

Fichier modifié : `.github/workflows/ci.yml`.

### 3. Commentaires et documentation

- **main.py** : commentaire « 14 routeurs » corrigé en « 15 routeurs ».
- **app/domain/__init__.py** : suppression des exports inutilisés (`DomainConflictError`, etc.) et ajout d’un commentaire expliquant que les exceptions domaine sont dans `app.domain.exceptions` et que le projet s’appuie sur `app.core.exceptions` pour l’API.
- **app/modules/comptabilite/services/__init__.py** : commentaire précisant que `plan_comptable.py` et `modele_ecriture.py` sont pour usage interne / évolution future (non exposés en API).

### 4. Configuration – Port par défaut

- **.env.example** : `PORT=8000` remplacé par `PORT=9111` pour être aligné avec `app/config.py`.

### 5. Scan global – Qualité de code (session « scanne chaque fichier »)

- **Espaces en fin de ligne** : suppression des espaces/tabs en fin de ligne dans **262 fichiers** (`app/` : 256, `tests/` : 6) via script Python (`line.rstrip()` par ligne, conservation du saut de ligne final).
- **app/core/database.py** : commentaire ajouté sur le `except Exception:` du générateur de session (rollback puis re-raise) pour clarifier l’intention.
- **Ruff** : en environnement local, `ruff check` / `ruff format` peuvent échouer avec `SyntaxError: source code string cannot contain null bytes` (sans fichier .py contenant d’octet nul détecté). À lancer dans un venv propre ou en CI pour le lint/format.

---

## Plan – Actions optionnelles (non faites)

| Priorité | Sujet | Action suggérée |
|----------|--------|------------------|
| Basse | Module Auth | Aligner la structure : passer de `auth/service.py` à `auth/services/` (ex. `login.py`) pour cohérence avec les autres modules. |
| Basse | Permissions | Seul le module Paramétrage utilise `RequirePermission`. Documenter la stratégie (permissions uniquement sur parametrage) ou étendre à d’autres modules si besoin. |
| Basse | Rapports | Documenter en en-tête du module ou en doc d’architecture que l’absence de `models`/`repositories` est volontaire (module d’agrégation). |

---

## Vérifications recommandées

1. **Lancer la CI** : push sur `main` ou `develop` (ou ouverture d’une PR) pour confirmer que le job `lint` passe avec `working-directory: backend`.
2. **Tests manuels** : appeler les endpoints Immobilisations avec un token d’un utilisateur et vérifier qu’un `entreprise_id` d’une autre entreprise est refusé (403).
3. **Démarrage** : `cd backend && python -c "from app.main import app; print('OK')"` et, si besoin, vérifier que le serveur écoute sur le port configuré (ex. 9111).
