# app/modules/comptabilite
# -----------------------------------------------------------------------------
# Module Comptabilité : plan comptable (comptes), journaux, périodes comptables,
# écritures et lignes d'écriture. Conforme OHADA/CEMAC.
#
# Extension du monde réel, adaptée à TOUTES les structures (taille) et TOUS les
# secteurs (commerce, industrie, services) :
#
# - Taille : PME (plan simplifié, peu de journaux) ou grand groupe (plan complet,
#   nombreux journaux, périodes par exercice). Plan comptable, journaux et
#   périodes par entreprise ; période optionnelle sur écriture ; traçabilité
#   (piece_jointe_ref, created_by_id).
# - Secteur : comptes par entreprise (type_compte, sens_normal), journaux
#   classiques (Ventes, Achats, Banque, Caisse, OD), écritures équilibrées.
# - Isolation multi-tenant : listes par ValidatedEntrepriseId ; GET/PATCH/POST
#   vérifient que la ressource appartient à l'entreprise de l'utilisateur.
# -----------------------------------------------------------------------------

