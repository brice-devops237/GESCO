# API Frontend Gesco

Types et client HTTP alignés sur **l’API OpenAPI 3.1.0 Gesco (v1.0.0)**.

- **`openapi.json`** – Référence minimale (info, version). La spec complète est exposée par le backend (ex. `/openapi.json` ou `/docs`).

## Structure

- **`client.ts`** – Client HTTP (`apiRequest`, `doRequest`), base URL `VITE_API_URL`, Bearer token.
- **`auth.ts`** – `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`.
- **`types.ts`** – Auth (LoginRequest, TokenResponse, RefreshRequest), erreurs (HTTPValidationError).
- **`types/`** – Schémas par domaine :
  - **parametrage** – Entreprises, Devises, Taux de change, Points de vente, Rôles, Permissions, Utilisateurs, Affectations utilisateur-PDV.
  - **catalogue** – Unités de mesure, Taux TVA, Familles produits, Conditionnements, Produits, Produits-Conditionnements, Canaux de vente, Prix produits, Variantes produit.
  - **partenaires** – Types de tiers, Tiers, Contacts.
  - **commercial** – États document, Devis, Commandes, Factures, Bons de livraison.
  - **achats** – Dépôts, Commandes fournisseurs, Réceptions, Factures fournisseurs.
  - **stock** – Stocks, Mouvements, Alertes, QuantiteStock.
  - **tresorerie** – Modes de paiement, Comptes trésorerie, Règlements.
  - **comptabilite** – Comptes, Journaux, Périodes, Écritures.
  - **rh** – Départements, Postes, Types contrat, Employés, Types congé, Demandes congé, Soldes congé, Objectifs, Taux commission, Commissions, Avances.
  - **paie** – Périodes paie, Types élément paie, Bulletins.
  - **rapports** – Chiffre d’affaires, Synthèse dashboard.
  - **immobilisations** – Catégories, Actifs, Lignes d’amortissement.
  - **systeme** – Paramètres, Journal d’audit, Notifications, Licences logicielles.

## Usage

- **Sans auth** : `apiRequest<T>(path, { method, body })`
- **Avec auth** : `authenticatedRequest<T>(path, { method, body })` (injecte le token et gère le refresh sur 401)

Les types (Create, Update, Response) sont exportés depuis `@/api` ou `@/api/types` pour être utilisés dans les vues et stores.
