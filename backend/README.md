# Gesco

**Système de gestion intégré (ERP)** multi-entreprises pour le **Cameroun et la zone CEMAC**.

Ce dépôt contient le **backend API** (FastAPI, SQLAlchemy 2 async, JWT). Un frontend peut être hébergé dans un autre dépôt ou intégré ultérieurement.

## Structure

| Dossier     | Description |
|------------|-------------|
| **backend/** | API REST FastAPI : paramétrage, catalogue, partenaires, ventes, achats, stock, trésorerie, comptabilité, RH, paie, immobilisations, rapports. |
| **backend/scripts/** | Scripts utilitaires (seed données de démo, build Windows). |

## Démarrage rapide

1. Aller dans le backend : `cd backend`
2. Créer l’environnement virtuel : `python -m venv .venv` puis l’activer (`.venv\Scripts\activate` sous Windows).
3. Installer les dépendances : `pip install -r requirements.txt`
4. Créer un fichier `.env` à la racine de `backend` avec au minimum :  
   `SECRET_KEY=<clé-secrète-d-au-moins-32-caractères>`
5. Appliquer les migrations : `alembic upgrade head`
6. Lancer l’API : `uvicorn app.main:app --reload --host 127.0.0.1 --port 9111`

- **API** : [http://127.0.0.1:9111](http://127.0.0.1:9111)  
- **Documentation** : [http://127.0.0.1:9111/docs](http://127.0.0.1:9111/docs)  
- **Santé** : [http://127.0.0.1:9111/health](http://127.0.0.1:9111/health) et [http://127.0.0.1:9111/health/ready](http://127.0.0.1:9111/health/ready)

## Documentation détaillée

Voir **[backend/README.md](backend/README.md)** pour la configuration, les modules, l’authentification (login + refresh token), les migrations et les tests.

## Licence

Projet propriétaire – usage interne.
