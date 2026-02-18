"""Module Paramétrage : entreprises, PDV, utilisateurs, rôles, devises, affectations.

Isolation multi-tenant : listes scoped par ValidatedEntrepriseId ; GET/PATCH/DELETE/POST
vérifient entreprise. Devises, taux de change, permissions : référentiels globaux.
"""

