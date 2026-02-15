# app/modules/immobilisations/services/categorie_immobilisation.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.immobilisations.models import CategorieImmobilisation
from app.modules.immobilisations.repositories import CategorieImmobilisationRepository
from app.modules.immobilisations.schemas import (
    CategorieImmobilisationCreate,
    CategorieImmobilisationUpdate,
)
from app.modules.immobilisations.services.base import BaseImmobilisationsService
from app.modules.immobilisations.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class CategorieImmobilisationService(BaseImmobilisationsService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CategorieImmobilisationRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def get_by_id(self, id: int) -> CategorieImmobilisation | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> CategorieImmobilisation:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.CATEGORIE_NOT_FOUND)
        return ent

    async def get_all(self, entreprise_id: int, skip: int = 0, limit: int = 100) -> tuple[list[CategorieImmobilisation], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(entreprise_id, skip=skip, limit=limit)

    async def create(self, data: CategorieImmobilisationCreate) -> CategorieImmobilisation:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request("Le code ne peut pas être vide.")
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.CATEGORIE_CODE_EXISTS.format(code=code))
        ent = CategorieImmobilisation(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle.strip(),
            duree_amortissement_annees=data.duree_amortissement_annees,
            taux_amortissement=data.taux_amortissement,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CategorieImmobilisationUpdate) -> CategorieImmobilisation:
        ent = await self.get_or_404(id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
