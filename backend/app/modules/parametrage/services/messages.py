# app/modules/parametrage/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Paramétrage.
# Réutilisables dans tous les services ; évite la redondance et garantit
# des libellés cohérents pour l'API.
# -----------------------------------------------------------------------------


class Messages:
    """
    Constantes de messages. Utiliser .format() pour les paramètres (ex: code, id).
    """

    # --- Entreprise ---
    ENTREPRISE_NOT_FOUND = "Entreprise non trouvée."
    ENTREPRISE_PAYS_INVALIDE = "Le code pays doit être un code ISO 3166-1 alpha-3 (3 lettres)."
    ENTREPRISE_DEVISE_INVALIDE = "Le code devise doit être un code ISO 4217 (3 lettres)."
    ENTREPRISE_CODE_EXISTS = "Une entreprise avec le code « {code} » existe déjà."
    ENTREPRISE_NIU_EXISTS = "Une entreprise avec le NIU « {niu} » existe déjà."
    ENTREPRISE_NIU_ALREADY_USED = "Le NIU « {niu} » est déjà utilisé par une autre entreprise."
    ENTREPRISE_CODE_INVALID = "Le code entreprise ne peut pas être vide."

    # --- Devise ---
    DEVISE_NOT_FOUND = "Devise non trouvée."
    DEVISE_CODE_VIDE = "Le code devise ne peut pas être vide."
    DEVISE_CODE_EXISTS = "La devise « {code} » existe déjà."

    # --- Taux de change ---
    TAUX_CHANGE_NOT_FOUND = "Taux de change non trouvé."
    TAUX_CHANGE_SAME_DEVISE = "Les devises source et cible doivent être différentes."
    TAUX_CHANGE_INVALID = "Le taux doit être strictement positif."

    # --- Point de vente ---
    POINT_VENTE_NOT_FOUND = "Point de vente non trouvé."
    POINT_VENTE_CODE_VIDE = "Le code du point de vente ne peut pas être vide."
    POINT_VENTE_CODE_EXISTS = "Un point de vente avec le code « {code} » existe déjà pour cette entreprise."
    POINT_VENTE_CODE_ALREADY_USED = "Ce code est déjà utilisé pour un autre point de vente."

    # --- Rôle ---
    ROLE_NOT_FOUND = "Rôle non trouvé."
    ROLE_CODE_EXISTS = "Un rôle avec le code « {code} » existe déjà."
    ROLE_CODE_ALREADY_USED = "Ce code est déjà utilisé pour un autre rôle."

    # --- Permission ---
    PERMISSION_NOT_FOUND = "Permission non trouvée."
    PERMISSION_MODULE_ACTION_EXISTS = "La permission « {module}.{action} » existe déjà."
    PERMISSION_ROLE_ALREADY = "Cette permission est déjà affectée à ce rôle."
    PERMISSION_ROLE_NOT_FOUND = "Cette permission n'est pas affectée à ce rôle."

    # --- Utilisateur ---
    UTILISATEUR_NOT_FOUND = "Utilisateur non trouvé."
    UTILISATEUR_LOGIN_EXISTS = "Un utilisateur avec le login « {login} » existe déjà pour cette entreprise."
    UTILISATEUR_DESACTIVATED = "Compte utilisateur désactivé."
    UTILISATEUR_LOGIN_INVALID = "Le login ne peut pas être vide."

    # --- Affectation utilisateur / PDV ---
    AFFECTATION_NOT_FOUND = "Affectation non trouvée."
    AFFECTATION_ALREADY_EXISTS = "Cet utilisateur est déjà affecté à ce point de vente."

    # --- Génériques (réutilisables) ---
    RESOURCE_NOT_FOUND = "Ressource non trouvée."
    CONFLIT_UNICITE = "Une ressource avec ces critères existe déjà."
    DONNEES_INVALIDES = "Les données fournies sont invalides."

