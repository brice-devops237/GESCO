# app/modules/immobilisations/services/immobilisation.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.immobilisations.models import Immobilisation
from app.modules.immobilisations.repositories import (
    CategorieImmobilisationRepository,
    ImmobilisationRepository,
    LigneAmortissementRepository,
)
from app.modules.immobilisations.schemas import ImmobilisationCreate, ImmobilisationUpdate
from app.modules.immobilisations.services.base import BaseImmobilisationsService
from app.modules.immobilisations.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class ImmobilisationService(BaseImmobilisationsService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ImmobilisationRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._categorie_repo = CategorieImmobilisationRepository(db)
        self._ligne_amort_repo = LigneAmortissementRepository(db)

    async def get_by_id(self, id: int) -> Immobilisation | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Immobilisation:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.IMMOBILISATION_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        categorie_id: int | None = None,
        actif_only: bool = False,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[Immobilisation], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            categorie_id=categorie_id,
            actif_only=actif_only,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: ImmobilisationCreate) -> Immobilisation:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._categorie_repo.find_by_id(data.categorie_id) is None:
            self._raise_not_found(Messages.CATEGORIE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request("Le code ne peut pas être vide.")
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.IMMOBILISATION_CODE_EXISTS.format(code=code))
        ent = Immobilisation(
            entreprise_id=data.entreprise_id,
            categorie_id=data.categorie_id,
            compte_comptable_id=data.compte_comptable_id,
            compte_amortissement_id=data.compte_amortissement_id,
            code=code,
            designation=data.designation.strip(),
            date_acquisition=data.date_acquisition,
            valeur_acquisition=data.valeur_acquisition,
            duree_amortissement_annees=data.duree_amortissement_annees,
            date_mise_en_service=data.date_mise_en_service,
            notes=data.notes.strip() if data.notes else None,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ImmobilisationUpdate) -> Immobilisation:
        ent = await self.get_or_404(id)
        for key, value in data.model_dump(exclude_unset=True).items():
            if isinstance(value, str):
                value = value.strip() or None
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def get_lignes_amortissement(
        self,
        immobilisation_id: int,
        *,
        skip: int = 0,
        limit: int = 200,
    ):
        """Liste des lignes d'amortissement d'une immobilisation (lecture seule)."""
        await self.get_or_404(immobilisation_id)
        return await self._ligne_amort_repo.find_by_immobilisation(
            immobilisation_id, skip=skip, limit=limit
        )
