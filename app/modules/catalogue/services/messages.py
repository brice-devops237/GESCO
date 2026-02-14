# app/modules/catalogue/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Catalogue.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres (ex: code, id)."""

    # --- Unité de mesure ---
    UNITE_MESURE_NOT_FOUND = "Unité de mesure non trouvée."
    UNITE_MESURE_CODE_VIDE = "Le code de l'unité de mesure ne peut pas être vide."
    UNITE_MESURE_CODE_EXISTS = "Une unité de mesure avec le code « {code} » existe déjà."

    # --- Taux TVA ---
    TAUX_TVA_NOT_FOUND = "Taux de TVA non trouvé."
    TAUX_TVA_CODE_VIDE = "Le code du taux de TVA ne peut pas être vide."
    TAUX_TVA_CODE_EXISTS = "Un taux de TVA avec le code « {code} » existe déjà."

    # --- Famille produit ---
    FAMILLE_PRODUIT_NOT_FOUND = "Famille de produits non trouvée."
    FAMILLE_PRODUIT_CODE_VIDE = "Le code de la famille ne peut pas être vide."
    FAMILLE_PRODUIT_CODE_EXISTS = "Une famille avec le code « {code} » existe déjà pour cette entreprise."
    FAMILLE_PARENT_NOT_FOUND = "La famille parente indiquée n'existe pas ou n'appartient pas à l'entreprise."

    # --- Conditionnement ---
    CONDITIONNEMENT_NOT_FOUND = "Conditionnement non trouvé."
    CONDITIONNEMENT_CODE_VIDE = "Le code du conditionnement ne peut pas être vide."
    CONDITIONNEMENT_CODE_EXISTS = "Un conditionnement avec le code « {code} » existe déjà pour cette entreprise."
    CONDITIONNEMENT_UNITE_NOT_FOUND = "L'unité de mesure indiquée n'existe pas."

    # --- Produit ---
    PRODUIT_NOT_FOUND = "Produit non trouvé."
    PRODUIT_CODE_VIDE = "Le code du produit ne peut pas être vide."
    PRODUIT_CODE_EXISTS = "Un produit avec le code « {code} » existe déjà pour cette entreprise."
    PRODUIT_FAMILLE_NOT_FOUND = "La famille de produits indiquée n'existe pas ou n'appartient pas à l'entreprise."
    PRODUIT_UNITE_VENTE_NOT_FOUND = "L'unité de vente indiquée n'existe pas."
    PRODUIT_UNITE_ACHAT_NOT_FOUND = "L'unité d'achat indiquée n'existe pas."
    PRODUIT_TAUX_TVA_NOT_FOUND = "Le taux de TVA indiqué n'existe pas."

    # --- Produit-Conditionnement ---
    PRODUIT_CONDITIONNEMENT_NOT_FOUND = "Liaison produit-conditionnement non trouvée."
    PRODUIT_CONDITIONNEMENT_EXISTS = "Ce produit est déjà associé à ce conditionnement."
    PRODUIT_CONDITIONNEMENT_PRODUIT_NOT_FOUND = "Le produit indiqué n'existe pas."
    PRODUIT_CONDITIONNEMENT_CONDITIONNEMENT_NOT_FOUND = "Le conditionnement indiqué n'existe pas."

    # --- Canal de vente ---
    CANAL_VENTE_NOT_FOUND = "Canal de vente non trouvé."
    CANAL_VENTE_CODE_VIDE = "Le code du canal de vente ne peut pas être vide."
    CANAL_VENTE_CODE_EXISTS = "Un canal de vente avec le code « {code} » existe déjà pour cette entreprise."

    # --- Prix produit ---
    PRIX_PRODUIT_NOT_FOUND = "Prix produit non trouvé."
    PRIX_PRODUIT_PRODUIT_NOT_FOUND = "Le produit indiqué n'existe pas."
    PRIX_PRODUIT_CANAL_NOT_FOUND = "Le canal de vente indiqué n'existe pas."
    PRIX_PRODUIT_PDV_NOT_FOUND = "Le point de vente indiqué n'existe pas."
    PRIX_PRODUIT_DATES_INVALIDES = "La date de fin doit être postérieure à la date de début."

    # --- Variante produit ---
    VARIANTE_NOT_FOUND = "Variante de produit non trouvée."
    VARIANTE_CODE_VIDE = "Le code de la variante ne peut pas être vide."
    VARIANTE_CODE_EXISTS = "Une variante avec le code « {code} » existe déjà pour ce produit."
    VARIANTE_PRODUIT_NOT_FOUND = "Le produit indiqué n'existe pas."

    # --- Entreprise (référence cross-module) ---
    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."

    # --- Génériques ---
    DONNEES_INVALIDES = "Les données fournies sont invalides."
