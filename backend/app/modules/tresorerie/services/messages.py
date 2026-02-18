# app/modules/tresorerie/services/messages.py
# -----------------------------------------------------------------------------
# Messages d'erreur et de validation centralisés pour le module Trésorerie.
# -----------------------------------------------------------------------------


class Messages:
    """Constantes de messages. Utiliser .format() pour les paramètres."""

    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    DEVISE_NOT_FOUND = "La devise indiquée n'existe pas."
    TIERS_NOT_FOUND = "Le tiers (client/fournisseur) indiqué n'existe pas."
    FACTURE_NOT_FOUND = "La facture client indiquée n'existe pas."
    FACTURE_FOURNISSEUR_NOT_FOUND = "La facture fournisseur indiquée n'existe pas."
    MODE_PAIEMENT_NOT_FOUND = "Le mode de paiement indiqué n'existe pas."
    COMPTE_TRESORERIE_NOT_FOUND = "Le compte trésorerie indiqué n'existe pas."
    REGLEMENT_NOT_FOUND = "Règlement non trouvé."

    MODE_PAIEMENT_CODE_VIDE = "Le code du mode de paiement ne peut pas être vide."
    MODE_PAIEMENT_CODE_EXISTS = "Un mode de paiement avec le code « {code} » existe déjà pour cette entreprise."
    TYPE_COMPTE_INVALIDE = "Le type de compte doit être : caisse ou bancaire (reçu : « {valeur} »)."
    TYPE_REGLEMENT_INVALIDE = "Le type de règlement doit être : client ou fournisseur (reçu : « {valeur} »)."
    REGLEMENT_FACTURE_OBLIGATOIRE = "La facture client est obligatoire pour un règlement client."
    REGLEMENT_FACTURE_FOURNISSEUR_OBLIGATOIRE = "La facture fournisseur est obligatoire pour un règlement fournisseur."
    REGLEMENT_MONTANT_POSITIF = "Le montant du règlement doit être strictement positif."

