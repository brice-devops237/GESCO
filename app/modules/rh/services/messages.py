# app/modules/rh/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module RH.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres."""

    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    DEVISE_NOT_FOUND = "La devise indiquée n'existe pas."
    DEPARTEMENT_NOT_FOUND = "Le département indiqué n'existe pas."
    POSTE_NOT_FOUND = "Le poste indiqué n'existe pas."
    TYPE_CONTRAT_NOT_FOUND = "Le type de contrat indiqué n'existe pas."
    EMPLOYE_NOT_FOUND = "L'employé indiqué n'existe pas."
    TYPE_CONGE_NOT_FOUND = "Le type de congé indiqué n'existe pas."
    DEMANDE_CONGE_NOT_FOUND = "La demande de congé indiquée n'existe pas."
    SOLDE_CONGE_NOT_FOUND = "Le solde de congé indiqué n'existe pas."
    OBJECTIF_NOT_FOUND = "L'objectif indiqué n'existe pas."
    TAUX_COMMISSION_NOT_FOUND = "Le taux de commission indiqué n'existe pas."
    COMMISSION_NOT_FOUND = "La commission indiquée n'existe pas."
    AVANCE_NOT_FOUND = "L'avance indiquée n'existe pas."

    DEPARTEMENT_CODE_VIDE = "Le code du département ne peut pas être vide."
    DEPARTEMENT_CODE_EXISTS = "Un département avec le code « {code} » existe déjà pour cette entreprise."
    POSTE_CODE_VIDE = "Le code du poste ne peut pas être vide."
    POSTE_CODE_EXISTS = "Un poste avec le code « {code} » existe déjà pour cette entreprise."
    TYPE_CONTRAT_CODE_VIDE = "Le code du type de contrat ne peut pas être vide."
    TYPE_CONTRAT_CODE_EXISTS = "Un type de contrat avec le code « {code} » existe déjà pour cette entreprise."
    EMPLOYE_MATRICULE_VIDE = "Le matricule ne peut pas être vide."
    EMPLOYE_MATRICULE_EXISTS = "Un employé avec le matricule « {matricule} » existe déjà pour cette entreprise."
    TYPE_CONGE_CODE_VIDE = "Le code du type de congé ne peut pas être vide."
    TYPE_CONGE_CODE_EXISTS = "Un type de congé avec le code « {code} » existe déjà pour cette entreprise."
    SOLDE_CONGE_EXISTS = "Un solde existe déjà pour cet employé, ce type de congé et cette année."
    TAUX_COMMISSION_CODE_VIDE = "Le code du taux de commission ne peut pas être vide."
    TAUX_COMMISSION_CODE_EXISTS = "Un taux de commission avec le code « {code} » existe déjà pour cette entreprise."

    DEMANDE_CONGE_DATES = "La date de fin doit être postérieure ou égale à la date de début."
    DEMANDE_CONGE_JOURS = "Le nombre de jours doit être cohérent avec les dates."
    DEMANDE_CONGE_STATUT_INVALIDE = "Statut invalide. Valeurs attendues : brouillon, en_attente, approuve, refuse."
    OBJECTIF_DATES = "La date de fin doit être postérieure ou égale à la date de début."
    COMMISSION_DATES = "La date de fin doit être postérieure ou égale à la date de début."
