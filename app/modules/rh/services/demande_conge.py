# app/modules/rh/services/demande_conge.py
# -----------------------------------------------------------------------------
# Service métier : demandes de congé.
# -----------------------------------------------------------------------------
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.models import DemandeConge
from app.modules.rh.repositories import (
    DemandeCongeRepository,
    EmployeRepository,
    TypeCongeRepository,
)
from app.modules.rh.schemas import DemandeCongeCreate, DemandeCongeUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages

STATUTS_VALIDES = ("brouillon", "en_attente", "approuve", "refuse")


class DemandeCongeService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = DemandeCongeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)
        self._type_conge_repo = TypeCongeRepository(db)

    async def get_by_id(self, id: int) -> DemandeConge | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> DemandeConge:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.DEMANDE_CONGE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        statut: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[DemandeConge], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            statut=statut,
            skip=skip,
            limit=limit,
        )

    def _validate_statut(self, statut: str) -> None:
        if statut not in STATUTS_VALIDES:
            self._raise_bad_request(Messages.DEMANDE_CONGE_STATUT_INVALIDE)

    async def create(self, data: DemandeCongeCreate) -> DemandeConge:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        if await self._type_conge_repo.find_by_id(data.type_conge_id) is None:
            self._raise_not_found(Messages.TYPE_CONGE_NOT_FOUND)
        if data.date_fin < data.date_debut:
            self._raise_bad_request(Messages.DEMANDE_CONGE_DATES)
        if data.nombre_jours < 1:
            self._raise_bad_request(Messages.DEMANDE_CONGE_JOURS)
        self._validate_statut(data.statut)
        ent = DemandeConge(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            type_conge_id=data.type_conge_id,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            nombre_jours=data.nombre_jours,
            statut=data.statut,
            motif=data.motif.strip() if data.motif else None,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: DemandeCongeUpdate, user_id: int | None = None) -> DemandeConge:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "statut" in update_data and update_data["statut"] is not None:
            self._validate_statut(update_data["statut"])
            if update_data["statut"] in ("approuve", "refuse"):
                ent.approuve_par_id = user_id
                ent.date_decision = datetime.now(UTC)
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)
