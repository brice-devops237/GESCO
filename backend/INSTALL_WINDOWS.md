# Installation et exécutable Windows – Gesco

Ce guide décrit comment construire un **exécutable Windows** (.exe) pour le serveur API Gesco et, optionnellement, le configurer pour un **démarrage automatique** (à l’ouverture de session ou au démarrage du PC).

## Prérequis

- Python 3.12 installé sur la machine de build
- Projet cloné, environnement virtuel activé, dépendances installées

## Build de l’exécutable

1. Installer les dépendances de build :
   ```powershell
   pip install -r requirements-build.txt
   ```

2. Lancer le script de build (ou PyInstaller directement) :
   ```powershell
   .\scripts\build_windows.ps1
   ```
   ou :
   ```powershell
   pyinstaller gesco.spec
   ```

3. Le résultat se trouve dans **`dist\GescoServeur\`** : le dossier contient `GescoServeur.exe` et les bibliothèques nécessaires. Copier ce dossier où vous le souhaitez sur la machine cible.

## Configuration sur la machine cible

1. Créer un fichier **`.env`** à côté de `GescoServeur.exe` avec au minimum :
   - `SECRET_KEY=<clé-secrète-min-32-caractères>`
   - Optionnel : `DATABASE_URL`, `PORT`, etc. (voir `backend/.env.example`).

2. Pour une première utilisation avec SQLite : la base sera créée au premier lancement. Pour utiliser une base existante, définir `DATABASE_URL` dans `.env`.

3. Lancer **`GescoServeur.exe`**. L’API sera accessible sur le port configuré (par défaut 9111 si défini dans la config).

## Démarrage automatique

- **À l’ouverture de session** : exécuter le script d’installation du démarrage automatique (à l’ouverture de session) :
  ```powershell
  .\scripts\install_demarrage_auto.ps1
  ```

- **Au démarrage du PC** (avant ouverture de session) : exécuter le même script avec l’option prévue pour le démarrage machine (souvent avec droits administrateur), par exemple :
  ```powershell
  .\scripts\install_demarrage_auto.ps1 -AuDemarrage
  ```
  (adapter selon le contenu réel du script dans le projet.)

Après configuration, le serveur Gesco démarrera automatiquement selon le mode choisi.

## Dépannage

- **Erreur « Module not found »** : vérifier que `requirements-build.txt` et `gesco.spec` incluent toutes les dépendances nécessaires (y compris `aiosqlite` pour SQLite).
- **Port déjà utilisé** : définir une autre valeur dans `.env` (ex. `PORT=9112`).
- **Base de données** : en SQLite par défaut, le fichier est créé dans le répertoire de l’exécutable (ou selon `DATABASE_URL`). Vérifier les droits d’écriture du dossier.
