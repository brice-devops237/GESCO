# app/modules/commercial
# -----------------------------------------------------------------------------
# Module Commercial : états document, devis, commandes, factures, bons de livraison.
#
# Extension du monde réel (cycle devis → commande → facture / BL), adaptée à
# TOUTES les structures (taille) et TOUS les secteurs (commerce, industrie, services) :
#
# - Taille : PME mono-PDV (point_de_vente_id optionnel sur devis) ou multi-sites
#   (PDV obligatoire sur commande/facture/BL). Devis et commande optionnellement
#   liés ; facture et BL avec ou sans commande. Workflow par états (EtatDocument).
# - Secteur : types facture CGI (facture, avoir, proforma, duplicata), mentions
#   légales (CGI/OHADA), multi-devise, conditions générales, référence client.
# - Isolation multi-tenant : listes par ValidatedEntrepriseId ; GET/PATCH/POST
#   vérifient que la ressource appartient à l'entreprise de l'utilisateur.
# -----------------------------------------------------------------------------

