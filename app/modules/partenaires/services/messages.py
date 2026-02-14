# app/modules/partenaires/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Partenaires.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres (ex: code, id)."""

    # --- Type de tiers ---
    TYPE_TIERS_NOT_FOUND = "Type de tiers non trouvé."
    TYPE_TIERS_CODE_VIDE = "Le code du type de tiers ne peut pas être vide."
    TYPE_TIERS_CODE_EXISTS = "Un type de tiers avec le code « {code} » existe déjà."

    # --- Tiers ---
    TIERS_NOT_FOUND = "Tiers non trouvé."
    TIERS_CODE_VIDE = "Le code du tiers ne peut pas être vide."
    TIERS_CODE_EXISTS = "Un tiers avec le code « {code} » existe déjà pour cette entreprise."
    TIERS_ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    TIERS_TYPE_TIERS_NOT_FOUND = "Le type de tiers indiqué n'existe pas."
    TIERS_CANAL_VENTE_NOT_FOUND = "Le canal de vente indiqué n'existe pas."

    # --- Contact ---
    CONTACT_NOT_FOUND = "Contact non trouvé."
    CONTACT_TIERS_NOT_FOUND = "Le tiers indiqué n'existe pas."
    CONTACT_NOM_VIDE = "Le nom du contact ne peut pas être vide."

    # --- Génériques ---
    DONNEES_INVALIDES = "Les données fournies sont invalides."
