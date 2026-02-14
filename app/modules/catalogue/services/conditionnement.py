# app/modules/catalogue/services/conditionnement.py
# -----------------------------------------------------------------------------
# Use Case Conditionnement (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import Conditionnement
from app.modules.catalogue.repositories import ConditionnementRepository, UniteMesureRepository
from app.modules.catalogue.schemas import ConditionnementCreate, ConditionnementUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class ConditionnementService(BaseCatalogueService):
    """Service de gestion des conditionnements (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ConditionnementRepository(db)
        self._unite_repo = UniteMesureRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def _ensure_entreprise_exists(self, entreprise_id: int) -> None:
        ent = await self._entreprise_repo.find_by_id(entreprise_id)
        if ent is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

    async def get_by_id(self, id: int) -> Conditionnement | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Conditionnement:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.CONDITIONNEMENT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Conditionnement], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: ConditionnementCreate) -> Conditionnement:
        await self._ensure_entreprise_exists(data.entreprise_id)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.CONDITIONNEMENT_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.CONDITIONNEMENT_CODE_EXISTS.format(code=code))
        if await self._unite_repo.find_by_id(data.unite_id) is None:
            self._raise_bad_request(Messages.CONDITIONNEMENT_UNITE_NOT_FOUND)
        ent = Conditionnement(
            entreprise_id=data.entreprise_id,
            code=code,
            libelle=data.libelle,
            quantite_unites=data.quantite_unites,
            unite_id=data.unite_id,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ConditionnementUpdate) -> Conditionnement:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data:
            code = (update_data["code"] or "").strip()
            if not code:
                self._raise_bad_request(Messages.CONDITIONNEMENT_CODE_VIDE)
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, code, exclude_id=id):
                self._raise_conflict(Messages.CONDITIONNEMENT_CODE_EXISTS.format(code=code))
            update_data["code"] = code
        if "unite_id" in update_data and await self._unite_repo.find_by_id(update_data["unite_id"]) is None:
            self._raise_bad_request(Messages.CONDITIONNEMENT_UNITE_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)
