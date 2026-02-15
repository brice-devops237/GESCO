# app/modules/systeme/services/licence_logicielle.py
from datetime import date, datetime
from calendar import monthrange
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.systeme.models import LicenceLogicielle
from app.modules.systeme.repositories import LicenceLogicielleRepository
from app.modules.systeme.schemas import LicenceLogicielleCreate, LicenceLogicielleUpdate
from app.modules.systeme.services.base import BaseSystemeService
from app.modules.systeme.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository

# Durées par type (mois) : trial 2, standard 6, premium 12
DUREE_PAR_TYPE = {"trial": 2, "standard": 6, "premium": 12}
# Prolongations max : trial 3, standard 3, premium illimité (None)
MAX_PROLONGATIONS_PAR_TYPE = {"trial": 3, "standard": 3, "premium": None}


def _ajouter_mois(d: date, mois: int) -> date:
    """Retourne d + mois (gère correctement les fins de mois)."""
    m = d.month - 1 + mois
    an = d.year + m // 12
    m = m % 12 + 1
    jour_max = monthrange(an, m)[1]
    jour = min(d.day, jour_max)
    return date(an, m, jour)


def _duree_mois(type_licence: str) -> int:
    """Retourne la durée en mois pour le type (trial=2, standard=6, premium=12)."""
    t = (type_licence or "").strip().lower()
    if t not in DUREE_PAR_TYPE:
        raise ValueError(Messages.LICENCE_TYPE_INVALIDE)
    return DUREE_PAR_TYPE[t]


def _peut_prolonger(type_licence: str, nombre_prolongations: int) -> tuple[bool, str]:
    """Retourne (autorisé, message). trial/standard max 3, premium illimité."""
    t = (type_licence or "").strip().lower()
    max_p = MAX_PROLONGATIONS_PAR_TYPE.get(t)
    if max_p is None:
        return True, ""
    if nombre_prolongations >= max_p:
        return False, Messages.LICENCE_PROLONGATION_MAX_ATTEINT.format(max=max_p, type=t)
    return True, ""


class LicenceLogicielleService(BaseSystemeService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = LicenceLogicielleRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> LicenceLogicielle | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> LicenceLogicielle:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.LICENCE_NOT_FOUND)
        return ent

    async def get_licence_valide_entreprise(self, entreprise_id: int) -> LicenceLogicielle | None:
        return await self._repo.find_licence_valide_entreprise(entreprise_id)

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        actif_only: bool = False,
        valide_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[LicenceLogicielle], int]:
        if entreprise_id is not None and await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            valide_only=valide_only,
            skip=skip,
            limit=limit,
        )

    async def verifier_validite(self, entreprise_id: int) -> tuple[bool, str, date | None]:
        """
        Vérifie si l'entreprise dispose d'une licence valide.
        Retourne (valide, message, date_fin).
        """
        licence = await self._repo.find_licence_valide_entreprise(entreprise_id)
        if licence is None:
            items, _ = await self._repo.find_all(
                entreprise_id=entreprise_id, actif_only=False, valide_only=False, limit=1
            )
            if items:
                l0 = items[0]
                if not l0.actif:
                    return False, Messages.LICENCE_INACTIVE, l0.date_fin
                if l0.date_fin < date.today():
                    return False, Messages.LICENCE_EXPIREE, l0.date_fin
            return False, Messages.LICENCE_NOT_FOUND, None
        return True, "Licence valide.", licence.date_fin

    async def create(self, data: LicenceLogicielleCreate) -> LicenceLogicielle:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        cle = (data.cle_licence or "").strip().upper()
        if not cle:
            self._raise_bad_request("La clé de licence ne peut pas être vide.")
        if await self._repo.find_by_entreprise_cle(data.entreprise_id, cle) is not None:
            self._raise_conflict(Messages.LICENCE_CLE_EXISTS)
        type_licence = (data.type_licence or "standard").strip().lower()
        duree_mois = _duree_mois(type_licence)
        date_fin = _ajouter_mois(data.date_debut, duree_mois)
        ent = LicenceLogicielle(
            entreprise_id=data.entreprise_id,
            cle_licence=cle,
            type_licence=type_licence,
            date_debut=data.date_debut,
            date_fin=date_fin,
            actif=True,
            nombre_prolongations=0,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: LicenceLogicielleUpdate) -> LicenceLogicielle:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "date_fin" in update_data and update_data["date_fin"] is not None:
            if update_data["date_fin"] <= ent.date_debut:
                self._raise_bad_request(Messages.LICENCE_DATE_FIN)
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def activer(self, id: int) -> LicenceLogicielle:
        """Marque la licence comme activée (date_activation = maintenant)."""
        ent = await self.get_or_404(id)
        if ent.date_activation is None:
            ent.date_activation = datetime.utcnow()
        return await self._repo.update(ent)

    async def prolonger(self, id: int) -> LicenceLogicielle:
        """
        Prolonge la licence : ajoute la durée du type (trial 2 mois, standard 6, premium 12)
        à la date_fin actuelle. Trial et standard : max 3 prolongations. Premium : illimité.
        """
        ent = await self.get_or_404(id)
        if not ent.actif:
            self._raise_bad_request(Messages.LICENCE_INACTIVE)
        autorise, msg = _peut_prolonger(ent.type_licence, ent.nombre_prolongations)
        if not autorise:
            self._raise_bad_request(msg)
        duree = _duree_mois(ent.type_licence)
        ent.date_fin = _ajouter_mois(ent.date_fin, duree)
        ent.nombre_prolongations = (ent.nombre_prolongations or 0) + 1
        return await self._repo.update(ent)

    def get_info_prolongations(self, type_licence: str, nombre_prolongations: int) -> dict:
        """Retourne les infos prolongations (restantes, durée ajoutée). Pour affichage."""
        t = (type_licence or "").strip().lower()
        duree = DUREE_PAR_TYPE.get(t, 12)
        max_p = MAX_PROLONGATIONS_PAR_TYPE.get(t)
        restantes = None if max_p is None else max(0, max_p - nombre_prolongations)
        return {
            "type_licence": t,
            "nombre_prolongations": nombre_prolongations,
            "prolongations_restantes": restantes,
            "duree_ajoutee_mois": duree,
        }
