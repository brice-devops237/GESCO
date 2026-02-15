# app/modules/rapports/services
from app.modules.rapports.services.dashboard import (
    get_chiffre_affaires,
    get_synthese_dashboard,
)

__all__ = ["get_chiffre_affaires", "get_synthese_dashboard"]
