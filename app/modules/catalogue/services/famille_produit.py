# app/modules/catalogue/services/famille_produit.py
# -----------------------------------------------------------------------------
# Use Case Famille de produits (couche Application).
# -----------------------------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.models import FamilleProduit
from app.modules.catalogue.repositories import FamilleProduitRepository
from app.modules.catalogue.schemas import FamilleProduitCreate, FamilleProduitUpdate
from app.modules.catalogue.services.base import BaseCatalogueService
from app.modules.catalogue.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository


class FamilleProduitService(BaseCatalogueService):
    """Service de gestion des familles de produits (par entreprise)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = FamilleProduitRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)

    async def _ensure_entreprise_exists(self, entreprise_id: int) -> None:
        ent = await self._entreprise_repo.find_by_id(entreprise_id)
        if ent is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)

    async def get_by_id(self, id: int) -> FamilleProduit | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> FamilleProduit:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.FAMILLE_PRODUIT_NOT_FOUND)
        return ent

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[FamilleProduit], int]:
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def create(self, data: FamilleProduitCreate) -> FamilleProduit:
        await self._ensure_entreprise_exists(data.entreprise_id)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.FAMILLE_PRODUIT_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.FAMILLE_PRODUIT_CODE_EXISTS.format(code=code))
        if data.parent_id is not None:
            parent = await self._repo.find_by_id(data.parent_id)
            if parent is None or parent.entreprise_id != data.entreprise_id:
                self._raise_bad_request(Messages.FAMILLE_PARENT_NOT_FOUND)
        ent = FamilleProduit(
            entreprise_id=data.entreprise_id,
            parent_id=data.parent_id,
            code=code,
            libelle=data.libelle,
            description=data.description,
            niveau=data.niveau,
            ordre_affichage=data.ordre_affichage,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: FamilleProduitUpdate) -> FamilleProduit:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            code = (update_data["code"] or "").strip()
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, code, exclude_id=id):
                self._raise_conflict(Messages.FAMILLE_PRODUIT_CODE_EXISTS.format(code=code))
        if "parent_id" in update_data and update_data["parent_id"] is not None:
            parent = await self._repo.find_by_id(update_data["parent_id"])
            if parent is None or parent.entreprise_id != ent.entreprise_id:
                self._raise_bad_request(Messages.FAMILLE_PARENT_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete_soft(self, id: int) -> None:
        ent = await self.get_or_404(id)
        ent.deleted_at = datetime.now(UTC)
        await self._repo.update(ent)
