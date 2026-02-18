# app/modules/stock/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Stock.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres."""

    DEPOT_NOT_FOUND = "Le dépôt indiqué n'existe pas."
    PRODUIT_NOT_FOUND = "Le produit indiqué n'existe pas."
    VARIANTE_NOT_FOUND = "La variante indiquée n'existe pas."
    STOCK_NOT_FOUND = "Stock non trouvé."
    MOUVEMENT_NOT_FOUND = "Mouvement de stock non trouvé."
    UNITE_NOT_FOUND = "L'unité de mesure indiquée n'existe pas."

    PRODUIT_STOCK_NON_GERE = "Le produit n'est pas configuré pour la gestion de stock (gerer_stock = false)."
    VARIANTE_STOCK_NON_SEPARE = "La variante n'a pas de stock séparé pour ce produit."
    QUANTITE_INSUFFISANTE = "Quantité en stock insuffisante (dépôt {depot_id}, produit {produit_id})."
    TYPE_MOUVEMENT_INVALIDE = "Le type de mouvement doit être : entree, sortie, transfert ou inventaire (reçu : « {valeur} »)."
    REFERENCE_TYPE_INVALIDE = "Le type de référence doit être : reception, bon_livraison, manuel, inventaire ou transfert (reçu : « {valeur} »)."
    TRANSFERT_DEPOT_DEST_OBLIGATOIRE = "Le dépôt destination est obligatoire pour un mouvement de type transfert."
    TRANSFERT_MEME_DEPOT = "Le dépôt destination doit être différent du dépôt origine."
    DATE_MOUVEMENT_INVALIDE = "La date (date_from ou date_to) doit être au format ISO (ex. 2025-01-15 ou 2025-01-15T00:00:00)."

