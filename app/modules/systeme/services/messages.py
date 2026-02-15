# app/modules/systeme/services/messages.py
class Messages:
    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    UTILISATEUR_NOT_FOUND = "L'utilisateur indiqué n'existe pas."
    PARAMETRE_SYSTEME_NOT_FOUND = "Le paramètre système indiqué n'existe pas."
    JOURNAL_AUDIT_NOT_FOUND = "L'entrée du journal d'audit indiquée n'existe pas."
    NOTIFICATION_NOT_FOUND = "La notification indiquée n'existe pas."
    PARAMETRE_CATEGORIE_CLE_VIDE = "La catégorie et la clé ne peuvent pas être vides."
    PARAMETRE_EXISTS = "Un paramètre avec cette catégorie et clé existe déjà pour cette entreprise."
    NOTIFICATION_UTILISATEUR_FORBIDDEN = "Vous ne pouvez accéder qu'à vos propres notifications."
    # Format clé : XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (5 blocs de 5 caractères, lettres et chiffres majuscules)
    LICENCE_NOT_FOUND = "La licence logicielle indiquée n'existe pas."
    LICENCE_CLE_EXISTS = "Une licence avec cette clé existe déjà pour cette entreprise."
    LICENCE_DATE_FIN = "La date de fin doit être postérieure à la date de début."
    LICENCE_EXPIREE = "La licence a expiré (date de fin dépassée)."
    LICENCE_INACTIVE = "La licence est désactivée."
    LICENCE_TYPE_INVALIDE = "Type de licence invalide. Valeurs : trial, standard, premium."
    LICENCE_PROLONGATION_MAX_ATTEINT = "Nombre maximum de prolongations atteint ({max}) pour une licence {type}. Impossible de prolonger."
