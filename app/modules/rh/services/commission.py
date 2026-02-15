# app/modules/rh/services/commission.py
# -----------------------------------------------------------------------------
# Service métier : commissions (versées ou à verser).
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import Commission
from app.modules.rh.repositories import CommissionRepository
from app.modules.rh.schemas import CommissionCreate, CommissionUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.repositories import EmployeRepository


class CommissionService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CommissionRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)

    async def get_by_id(self, id: int) -> Commission | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Commission:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.COMMISSION_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        payee: bool | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Commission], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            payee=payee,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: CommissionCreate) -> Commission:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        if data.date_fin < data.date_debut:
            self._raise_bad_request(Messages.COMMISSION_DATES)
        ent = Commission(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            taux_commission_id=data.taux_commission_id,
            date_debut=data.date_debut,
            date_fin=data.date_fin,
            montant=data.montant,
            libelle=data.libelle.strip() if data.libelle else None,
            payee=data.payee,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CommissionUpdate) -> Commission:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)
