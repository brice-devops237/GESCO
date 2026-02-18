# app/shared/regulations.py
# -----------------------------------------------------------------------------
# Référentiel réglementaire : Cameroun (CGI, DGI, CEMAC) et normes internationales
# (ISO 3166, ISO 4217, OHADA, bonnes pratiques facturation).
# Utilisé pour documenter et valider les règles de gestion dans les modules.
# -----------------------------------------------------------------------------

from typing import Final

# --- Cameroun / CEMAC --------------------------------------------------------

# Code pays ISO 3166-1 alpha-3 (Cameroun)
PAYS_DEFAULT_CMR: Final[str] = "CMR"

# Devise légale CEMAC (Zone Franc CFA – BEAC)
DEVISE_DEFAULT_XAF: Final[str] = "XAF"

# NIU (Numéro d'Identification Unique) – DGI Cameroun, obligatoire pour les
# opérations à caractère économique depuis le 1er janvier 2021 (Loi de finances).
# Format : alphanumérique, longueur max recommandée 20 caractères.
NIU_MAX_LENGTH: Final[int] = 20

# RCCM (Registre du Commerce et du Crédit Mobilier) – OHADA, identification
# des sociétés dans les États membres (Cameroun, Sénégal, Côte d'Ivoire, etc.).
# CNPS (Caisse Nationale de Prévoyance Sociale) – Cameroun, numéro employeur/cotisation.
# Boîte postale : très utilisée en Afrique francophone pour l'adresse postale.

# TVA Cameroun – Code Général des Impôts (taux en vigueur).
# Standard : 19,25 % ; réduit : 10 % (et 9,75 % selon périodes) ; 0 % (exonérations).
# Loi de finances 2026 : taux normal 17,5 %, réduit 10 %.
TVA_TAUX_COURANTS_CMR: Final[tuple[float, ...]] = (0.0, 9.75, 10.0, 17.5, 19.25)

# Conservation des pièces comptables : OHADA / droit camerounais (souvent 10 ans).
# À respecter pour factures, devis, commandes, pièces justificatives.
CONSERVATION_DOCUMENTS_ANNEES: Final[int] = 10

# --- International ----------------------------------------------------------

# Codes pays : ISO 3166-1 alpha-3 (3 lettres).
# Codes devises : ISO 4217 (XAF, EUR, USD, etc.).

# Montants : toujours en Decimal (pas de float) pour conformité comptable et
# éviter les erreurs d'arrondi (directive UE, OHADA, bonnes pratiques).

# Facturation (CGI Cameroun / OHADA / bonnes pratiques) : mentions utiles
# (identification vendeur/acheteur, numéro, date, désignation, quantités,
# prix unitaire, taux TVA, montants HT, TVA, TTC, conditions de paiement).


def is_pays_code_valide(code: str) -> bool:
    """Vérifie que le code pays est sur 3 caractères (ISO 3166-1 alpha-3)."""
    return isinstance(code, str) and len(code) == 3 and code.isalpha()


def is_devise_code_valide(code: str) -> bool:
    """Vérifie que le code devise est sur 3 caractères (ISO 4217)."""
    return isinstance(code, str) and len(code) == 3 and code.isalpha()

