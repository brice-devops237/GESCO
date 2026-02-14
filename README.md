# Gesco

**Système de gestion commerciale** – API backend pour le marché camerounais (multi-entreprises, devis, commandes, facturation, achats). Conforme au droit camerounais (CGI, DGI, NIU) et aux normes internationales (ISO 3166, ISO 4217).

---

## Fonctionnalités

- **Authentification** : login JWT (entreprise + login + mot de passe)
- **Paramétrage** : entreprises, devises (XAF, EUR, USD), points de vente, rôles, permissions, utilisateurs, affectations
- **Catalogue** : familles, produits, variantes, conditionnements, taux de TVA, canaux de vente, prix
- **Partenaires** : types de tiers, clients/fournisseurs (tiers), contacts, NIU
- **Commercial** : états document, devis, commandes, factures (facture/avoir/proforma/duplicata), bons de livraison
- **Achats** : commandes fournisseurs, réceptions, factures fournisseurs

---

## Stack technique

- **Python 3.12** · **FastAPI** · **SQLAlchemy 2** (async) · **PostgreSQL** (asyncpg)
- **Pydantic** (validation, config) · **JWT** (python-jose) · **bcrypt** (mots de passe)
- **Alembic** (migrations)

---

## Prérequis

- Python 3.12+
- PostgreSQL 14+
- (Optionnel) Redis pour le cache

---

## Installation

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd Gesco

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux / macOS

# Installer les dépendances
pip install -r requirements.txt
```

---

## Configuration

Créer un fichier **`.env`** à la racine du projet (voir `.env.example` si fourni). Variables obligatoires :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL PostgreSQL **asynchrone** (asyncpg) | `postgresql+asyncpg://user:pass@localhost:5432/gesco` |
| `DATABASE_URL_SYNC` | URL PostgreSQL **synchrone** (Alembic) | `postgresql://user:pass@localhost:5432/gesco` |
| `SECRET_KEY` | Clé secrète JWT (min 32 caractères) | une chaîne longue et aléatoire |

Variables optionnelles (valeurs par défaut) :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `API_V1_PREFIX` | `/api/v1` | Préfixe des routes API |
| `HOST` | `0.0.0.0` | Adresse d'écoute |
| `PORT` | `8000` | Port du serveur |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Durée de validité du token JWT |
| `CORS_ORIGINS` | `*` | Origines CORS (séparées par des virgules) |
| `TIMEZONE` | `Africa/Douala` | Fuseau horaire |
| `DEFAULT_CURRENCY_CODE` | `XAF` | Devise par défaut |

---

## Lancer l'application

```bash
# Développement (rechargement automatique)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- **API** : `http://localhost:8000`
- **Documentation Swagger** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`
- **Santé** : `http://localhost:8000/health` (sans authentification)

---

## API – Authentification

1. **POST** `/api/v1/auth/login`  
   Corps : `{ "entreprise_id": 1, "login": "...", "password": "..." }`  
   Réponse : `{ "access_token": "...", "token_type": "bearer" }`

2. Utiliser le token dans les requêtes :  
   **Header** : `Authorization: Bearer <access_token>`

Toutes les autres routes (paramétrage, catalogue, partenaires, commercial, achats) nécessitent ce header.

---

## Structure du projet

```
Gesco/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration (pydantic-settings)
│   ├── core/                # DB, exceptions, sécurité, service base
│   ├── shared/              # Réglementations, schémas communs, utils
│   └── modules/
│       ├── auth/            # Login JWT
│       ├── parametrage/     # Entreprises, devises, PDV, rôles, utilisateurs
│       ├── catalogue/       # Produits, familles, TVA, canaux, prix
│       ├── partenaires/     # Tiers, contacts
│       ├── commercial/     # Devis, commandes, factures, BL
│       └── achats/         # Commandes fournisseurs, réceptions, factures fournisseurs
├── requirements.txt
├── .env                     # (à créer, non versionné)
├── .gitignore
└── README.md
```

Chaque module métier suit une structure **Clean Architecture** : `models`, `schemas`, `repositories`, `services`, `router`.

---

## Conformité

- **Cameroun** : CGI (régimes fiscaux, TVA), DGI (NIU), CEMAC (XAF)
- **International** : codes pays ISO 3166-1 alpha-3, devises ISO 4217, montants en `Decimal`, bonnes pratiques facturation (HT/TVA/TTC)

Référentiel partagé : `app/shared/regulations.py`.

---

## Migrations (Alembic)

```bash
# Créer une migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head
```

---

## Tests

```bash
pytest
pytest --cov=app
```

---

## Licence

Projet propriétaire – usage interne.
