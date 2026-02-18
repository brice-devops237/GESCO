# app/modules/achats
# -----------------------------------------------------------------------------
# Module Achats : dépôts, commandes fournisseurs, réceptions, factures fournisseurs.
#
# Extension du monde réel, adapté à TOUTES les structures (taille) et TOUS les
# secteurs (commerce, industrie, services, import, etc.) :
#
# - Taille : PME (un dépôt ou aucun, depot_id optionnel sur commande ; facture
#   sans commande = achat direct) ; grands groupes (multi-dépôts, multi-sites,
#   workflow complet commande → réception → facture). Aucune hypothèse sur la
#   taille ; champs optionnels (délais, date livraison, n° BL) pour simplicité.
# - Secteur : industrie (réceptions par dépôt, BL), commerce (achats directs,
#   factures/avoirs), services (prestations fournisseurs, proforma). Types
#   facture (facture / avoir / proforma) et statuts paiement couvrent tous usages.
# - Multi-devises (devise_id sur commande et facture) : international, import.
# - Workflow : états par entreprise (etats_document), réceptions (brouillon →
#   validée). Isolation multi-tenant stricte sur toutes les routes (entreprise).
# - Dépôt : pays (ISO 3166-1 alpha-3), code_postal (logistique, douane).
# -----------------------------------------------------------------------------

