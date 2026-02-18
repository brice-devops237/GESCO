# app/modules/systeme/services/parametre_systeme.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.systeme.models import ParametreSysteme
from app.modules.systeme.repositories import ParametreSystemeRepository
from app.modules.systeme.schemas import ParametreSystemeCreate, ParametreSystemeUpdate
from app.modules.systeme.services.base import BaseSystemeService
from app.modules.systeme.services.messages import Messages


class ParametreSystemeService(BaseSystemeService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ParametreSystemeRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> ParametreSysteme | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> ParametreSysteme:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.PARAMETRE_SYSTEME_NOT_FOUND)
        return ent

    async def get_by_entreprise_categorie_cle(
        self, entreprise_id: int, categorie: str, cle: str
    ) -> ParametreSysteme | None:
        return await self._repo.find_by_entreprise_categorie_cle(
            entreprise_id, (categorie or "").strip(), (cle or "").strip()
        )

    async def get_all(
        self,
        entreprise_id: int,
        *,
        categorie: str | None = None,
        skip: int = 0,
        limit: int = 500,
    ) -> tuple[list[ParametreSysteme], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            categorie=categorie.strip() if categorie else None,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: ParametreSystemeCreate) -> ParametreSysteme:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        cat = (data.categorie or "").strip()
        cle = (data.cle or "").strip()
        if not cat or not cle:
            self._raise_bad_request(Messages.PARAMETRE_CATEGORIE_CLE_VIDE)
        if await self._repo.exists_by_entreprise_categorie_cle(data.entreprise_id, cat, cle):
            self._raise_conflict(Messages.PARAMETRE_EXISTS)
        ent = ParametreSysteme(
            entreprise_id=data.entreprise_id,
            categorie=cat,
            cle=cle,
            valeur=data.valeur.strip() if data.valeur else None,
            description=data.description.strip() if data.description else None,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ParametreSystemeUpdate) -> ParametreSysteme:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)

