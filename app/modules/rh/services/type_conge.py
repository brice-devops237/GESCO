# app/modules/rh/services/type_conge.py
# -----------------------------------------------------------------------------
# Service métier : types de congé (annuel, maladie, maternité, etc.).
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rh.models import TypeConge
from app.modules.rh.repositories import TypeCongeRepository
from app.modules.rh.schemas import TypeCongeCreate, TypeCongeUpdate
from app.modules.rh.services.base import BaseRHService
from app.modules.rh.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class TypeCongeService(BaseRHService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TypeCongeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> TypeConge | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> TypeConge:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.TYPE_CONGE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[TypeConge], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: TypeCongeCreate) -> TypeConge:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.TYPE_CONGE_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.TYPE_CONGE_CODE_EXISTS.format(code=code))
        ent = TypeConge(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            paye=data.paye,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: TypeCongeUpdate) -> TypeConge:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"] is not None:
            update_data["code"] = update_data["code"].strip()
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, update_data["code"], exclude_id=id):
                self._raise_conflict(Messages.TYPE_CONGE_CODE_EXISTS.format(code=update_data["code"]))
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
