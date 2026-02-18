# app/modules/paie/services/messages.py
class Messages:
    ENTREPRISE_NOT_FOUND = "L'entreprise indiquée n'existe pas."
    PERIODE_PAIE_NOT_FOUND = "La période de paie indiquée n'existe pas."
    PERIODE_PAIE_EXISTS = "Une période existe déjà pour cette entreprise, année et mois."
    PERIODE_PAIE_CLOTUREE = "La période est clôturée ; modification impossible."
    TYPE_ELEMENT_PAIE_NOT_FOUND = "Le type d'élément de paie indiqué n'existe pas."
    TYPE_ELEMENT_PAIE_CODE_EXISTS = "Un type d'élément avec le code « {code} » existe déjà."
    EMPLOYE_NOT_FOUND = "L'employé indiqué n'existe pas."
    BULLETIN_PAIE_NOT_FOUND = "Le bulletin de paie indiqué n'existe pas."
    BULLETIN_PAIE_EXISTS = "Un bulletin existe déjà pour cet employé et cette période."
    PERIODE_DATES = "La date de fin doit être postérieure à la date de début."
    TYPE_GAIN_RETENUE = "Le type doit être : gain ou retenue."
    STATUT_BULLETIN = "Le statut doit être : brouillon, valide ou paye."

