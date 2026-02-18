# app/modules/achats/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Achats.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres."""

    # --- Références cross-module ---
    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    FOURNISSEUR_NOT_FOUND = "Le fournisseur (tiers) indiqué n'existe pas."
    DEPOT_NOT_FOUND = "Le dépôt indiqué n'existe pas."
    ETAT_DOCUMENT_NOT_FOUND = "L'état de document indiqué n'existe pas."
    DEVISE_NOT_FOUND = "La devise indiquée n'existe pas."

    # --- Commande fournisseur ---
    COMMANDE_FOURNISSEUR_NOT_FOUND = "Commande fournisseur non trouvée."
    COMMANDE_FOURNISSEUR_NUMERO_EXISTS = "Une commande fournisseur avec le numéro « {numero} » existe déjà pour cette entreprise."
    COMMANDE_FOURNISSEUR_NUMERO_VIDE = "Le numéro de commande ne peut pas être vide."
    COMMANDE_FOURNISSEUR_DATES_INCOHERENTES = "La date de livraison prévue ne peut pas être antérieure à la date de commande."

    # --- Réception ---
    RECEPTION_NOT_FOUND = "Réception non trouvée."
    RECEPTION_NUMERO_VIDE = "Le numéro de réception ne peut pas être vide."
    RECEPTION_ETAT_INVALIDE = "L'état de la réception doit être : brouillon, validee ou annulee (reçu : « {valeur} »)."

    # --- Facture fournisseur ---
    FACTURE_FOURNISSEUR_NOT_FOUND = "Facture fournisseur non trouvée."
    FACTURE_FOURNISSEUR_NUMERO_VIDE = "Le numéro de facture fournisseur ne peut pas être vide."
    FACTURE_FOURNISSEUR_STATUT_INVALIDE = "Le statut de paiement doit être : non_paye, partiel ou paye (reçu : « {valeur} »)."
    FACTURE_FOURNISSEUR_TYPE_INVALIDE = "Le type de facture doit être : facture, avoir ou proforma (reçu : « {valeur} »)."
    FACTURE_FOURNISSEUR_MONTANT_RESTANT = "Le montant restant dû ne peut pas dépasser le montant TTC."

    # --- Dépôt ---
    DEPOT_NOT_FOUND_MSG = "Dépôt non trouvé."
    DEPOT_CODE_VIDE = "Le code du dépôt ne peut pas être vide."
    DEPOT_CODE_EXISTS = "Un dépôt avec le code « {code} » existe déjà pour cette entreprise."
    DEPOT_PAYS_INVALIDE = "Le code pays doit être au format ISO 3166-1 alpha-3 (3 lettres)."

    # --- Génériques ---
    DONNEES_INVALIDES = "Les données fournies sont invalides."

