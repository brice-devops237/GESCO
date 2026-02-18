# app/modules/catalogue
# -----------------------------------------------------------------------------
# Module Catalogue : unités de mesure, taux TVA, familles de produits,
# conditionnements, produits, variantes, canaux de vente, prix.
#
# Extension du monde réel, adapté à TOUTES les structures (taille) et TOUS les
# secteurs (commerce, industrie, services) :
#
# - Taille : PME (famille plate, peu de conditionnements/canaux) ou grand groupe
#   (hiérarchie familles, multi-conditionnements, prix par canal/PDV/période).
#   Référentiels partagés (UniteMesure, TauxTva) sans entreprise_id.
# - Secteur : types produit / service / composant ; code douanier, pays origine ;
#   conditionnements (type emballage, poids) ; TVA (nature normal/réduit/exonéré).
# - Isolation multi-tenant : listes par ValidatedEntrepriseId ; GET/PATCH/DELETE
#   et POST vérifient que la ressource appartient à l'entreprise de l'utilisateur.
# -----------------------------------------------------------------------------

