# app/modules/comptabilite/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Comptabilité.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres."""

    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    COMPTE_COMPTABLE_NOT_FOUND = "Le compte comptable indiqué n'existe pas."
    JOURNAL_COMPTABLE_NOT_FOUND = "Le journal comptable indiqué n'existe pas."
    PERIODE_COMPTABLE_NOT_FOUND = "La période comptable indiquée n'existe pas."
    ECRITURE_COMPTABLE_NOT_FOUND = "L'écriture comptable indiquée n'existe pas."

    COMPTE_NUMERO_VIDE = "Le numéro du compte ne peut pas être vide."
    COMPTE_NUMERO_EXISTS = "Un compte avec le numéro « {numero} » existe déjà pour cette entreprise."
    JOURNAL_CODE_VIDE = "Le code du journal ne peut pas être vide."
    JOURNAL_CODE_EXISTS = "Un journal avec le code « {code} » existe déjà pour cette entreprise."
    SENS_COMPTE_INVALIDE = "Le sens normal doit être : debit ou credit (reçu : « {valeur} »)."
    PERIODE_DATES_INCOHERENTES = "La date de fin doit être postérieure à la date de début."
    PERIODE_CLOTUREE = "Impossible d'ajouter une écriture : la période est clôturée."
    PERIODE_DATE_HORS_PERIODE = "La date d'écriture doit être dans l'intervalle de la période."
    ECRITURE_LIGNES_MIN = "Une écriture doit comporter au moins deux lignes."
    ECRITURE_NON_EQUILIBREE = "L'écriture n'est pas équilibrée : total débit doit être égal au total crédit."
    ECRITURE_NUMERO_PIECE_VIDE = "Le numéro de pièce ne peut pas être vide."
    ECRITURE_MONTANT_ZERO = "Une écriture doit avoir un montant total (débit/crédit) strictement positif."