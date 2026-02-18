# Priorités des modules Gesco

Les modules de l’API sont organisés par priorité métier et technique. L’ordre d’enregistrement des routeurs dans `app/main.py` et l’ordre des tags dans `/docs` respectent cette hiérarchie.

---

## P0 — Fondation (indispensables)

| Module        | Rôle |
|---------------|------|
| **auth**      | Authentification (login par entreprise, JWT). Sans lui, aucune ressource protégée n’est accessible. |
| **parametrage** | Entreprises, devises, taux de change, points de vente, rôles, permissions, utilisateurs, affectations PDV. Base de toute la multi-société et des accès. |

---

## P1 — Données de base (cœur métier)

| Module         | Rôle |
|----------------|------|
| **catalogue**  | Unités, TVA, familles, conditionnements, produits, canaux de vente, prix, variantes. Nécessaire pour vendre et acheter. |
| **partenaires**| Types de tiers, tiers (clients/fournisseurs), contacts. Partenaires commerciaux. |

---

## P2 — Opérations commerciales et logistique

| Module        | Rôle |
|---------------|------|
| **commercial**| Devis, commandes, factures, bons de livraison. Cycle de vente. |
| **achats**    | Dépôts, commandes fournisseurs, réceptions, factures fournisseurs. Cycle d’achat. |
| **stock**     | Niveaux de stock, mouvements, alertes. Gestion des entrées/sorties et inventaire. |

---

## P3 — Trésorerie et comptabilité

| Module          | Rôle |
|-----------------|------|
| **tresorerie**  | Modes de paiement, comptes trésorerie, règlements. Flux de trésorerie. |
| **comptabilite**| Plan comptable, journaux, périodes, écritures. Conformité OHADA/CEMAC. |

---

## P4 — Ressources humaines et paie

| Module | Rôle |
|--------|------|
| **rh** | Départements, postes, types de contrat, employés, congés, objectifs, commissions, avances. |
| **paie**| Périodes de paie, types d’éléments, bulletins de paie. |

---

## P5 — Support, rapports et actifs

| Module             | Rôle |
|--------------------|------|
| **systeme**        | Paramètres applicatifs, journal d’audit, notifications, licences logicielles. |
| **rapports**       | Chiffre d’affaires, tableau de bord. Synthèses et reporting. |
| **immobilisations**| Catégories, immobilisations, amortissements. Actifs non courants. |

---

## Ordre d’enregistrement (main.py)

Les routeurs sont enregistrés dans cet ordre pour garder une cohérence avec les priorités ci‑dessus :

1. auth  
2. parametrage  
3. catalogue  
4. partenaires  
5. commercial  
6. achats  
7. stock  
8. tresorerie  
9. comptabilite  
10. rh  
11. paie  
12. systeme  
13. rapports  
14. immobilisations  

---

## Utilisation

- **Développement** : traiter en priorité les modules P0 puis P1 pour avoir une base utilisable (connexion, paramétrage, catalogue, partenaires).
- **Déploiement / fonctionnalités** : activer ou documenter les modules par niveau (ex. version “light” = P0 à P2, version “complète” = tous).
- **Documentation** : dans `/docs`, les tags OpenAPI suivent le même ordre pour faciliter la navigation.
