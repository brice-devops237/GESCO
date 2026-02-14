# app/modules/achats/services/base.py
# app/modules/achats/services/base.py
# -----------------------------------------------------------------------------
# Base des services métier Achats (hérite _validate_enum et _raise_* du core).
# -----------------------------------------------------------------------------

from app.core.service_base import BaseService


class BaseAchatsService(BaseService):
    """Base des services métier Achats."""
    pass
