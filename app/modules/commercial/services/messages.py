# app/modules/commercial/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Commercial.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres (ex: numero)."""

    # --- Références cross-module ---
    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    POINT_VENTE_NOT_FOUND = "Le point de vente indiqué n'existe pas."
    CLIENT_NOT_FOUND = "Le client (tiers) indiqué n'existe pas."
    ETAT_DOCUMENT_NOT_FOUND = "L'état de document indiqué n'existe pas."
    ETAT_DOCUMENT_CODE_VIDE = "Le code de l'état document ne peut pas être vide."
    ETAT_DOCUMENT_TYPE_CODE_EXISTS = "Un état « {type_document}.{code} » existe déjà."
    DEVISE_NOT_FOUND = "La devise indiquée n'existe pas."

    # --- Devis ---
    DEVIS_NOT_FOUND = "Devis non trouvé."
    DEVIS_NUMERO_EXISTS = "Un devis avec le numéro « {numero} » existe déjà pour cette entreprise."

    # --- Commande ---
    COMMANDE_NOT_FOUND = "Commande non trouvée."
    COMMANDE_NUMERO_EXISTS = "Une commande avec le numéro « {numero} » existe déjà pour cette entreprise."

    # --- Facture ---
    FACTURE_NOT_FOUND = "Facture non trouvée."
    FACTURE_NUMERO_EXISTS = "Une facture avec le numéro « {numero} » existe déjà pour cette entreprise."
    FACTURE_NUMERO_VIDE = "Le numéro de facture ne peut pas être vide."
    FACTURE_TYPE_INVALIDE = "Le type de facture doit être : facture, avoir, proforma ou duplicata (reçu : « {valeur} »)."

    # --- Bon de livraison ---
    BON_LIVRAISON_NOT_FOUND = "Bon de livraison non trouvé."
    BON_LIVRAISON_NUMERO_EXISTS = "Un bon de livraison avec le numéro « {numero} » existe déjà pour cette entreprise."

    # --- Génériques ---
    DONNEES_INVALIDES = "Les données fournies sont invalides."
