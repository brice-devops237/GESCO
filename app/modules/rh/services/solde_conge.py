# app/modules/rh/services/solde_conge.py
# -----------------------------------------------------------------------------
# Service métier : soldes de congé (droits acquis, pris, restants).
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import SoldeConge
from app.modules.rh.repositories import SoldeCongeRepository
from app.modules.rh.schemas import SoldeCongeCreate, SoldeCongeUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.repositories import EmployeRepository, TypeCongeRepository


class SoldeCongeService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = SoldeCongeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)
        self._type_conge_repo = TypeCongeRepository(db)

    async def get_by_id(self, id: int) -> SoldeConge | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> SoldeConge:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.SOLDE_CONGE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        annee: int | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[SoldeConge], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            annee=annee,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: SoldeCongeCreate) -> SoldeConge:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        if await self._type_conge_repo.find_by_id(data.type_conge_id) is None:
            self._raise_not_found(Messages.TYPE_CONGE_NOT_FOUND)
        existing = await self._repo.find_by_employe_type_annee(
            data.entreprise_id, data.employe_id, data.type_conge_id, data.annee
        )
        if existing is not None:
            self._raise_conflict(Messages.SOLDE_CONGE_EXISTS)
        ent = SoldeConge(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            type_conge_id=data.type_conge_id,
            annee=data.annee,
            droits_acquis=data.droits_acquis,
            jours_pris=data.jours_pris,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: SoldeCongeUpdate) -> SoldeConge:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
