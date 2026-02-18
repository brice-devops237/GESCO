# app/modules/paie/services/type_element_paie.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.paie.models import TypeElementPaie
from app.modules.paie.repositories import TypeElementPaieRepository
from app.modules.paie.schemas import TypeElementPaieCreate, TypeElementPaieUpdate
from app.modules.paie.services.base import BasePaieService
from app.modules.paie.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class TypeElementPaieService(BasePaieService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TypeElementPaieRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> TypeElementPaie | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> TypeElementPaie:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.TYPE_ELEMENT_PAIE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        type_filter: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TypeElementPaie], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            type_filter=type_filter,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: TypeElementPaieCreate) -> TypeElementPaie:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request("Le code ne peut pas être vide.")
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.TYPE_ELEMENT_PAIE_CODE_EXISTS.format(code=code))
        if data.type not in ("gain", "retenue"):
            self._raise_bad_request(Messages.TYPE_GAIN_RETENUE)
        ent = TypeElementPaie(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            type=data.type,
            ordre_affichage=data.ordre_affichage,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: TypeElementPaieUpdate) -> TypeElementPaie:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "type" in update_data and update_data["type"] not in ("gain", "retenue"):
            self._raise_bad_request(Messages.TYPE_GAIN_RETENUE)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

