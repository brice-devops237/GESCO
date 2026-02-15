# app/modules/rapports/schemas.py
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ChiffreAffairesPeriode(BaseModel):
    """Chiffre d'affaires sur une période."""
    entreprise_id: int
    date_debut: date
    date_fin: date
    montant_total_ttc: Decimal = Field(default=Decimal("0"))
    nombre_factures: int = 0


class IndicateurStock(BaseModel):
    """Indicateurs stock (valeur, alertes)."""
    entreprise_id: int
    nombre_articles: int = 0
    valeur_totale: Decimal | None = None
    articles_en_rupture: int = 0


class SyntheseDashboard(BaseModel):
    """Synthèse pour tableau de bord."""
    entreprise_id: int
    periode_label: str | None = None
    ca_periode: Decimal = Field(default=Decimal("0"))
    nb_factures: int = 0
    nb_commandes: int = 0
    nb_employes_actifs: int = 0
