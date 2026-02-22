# app/modules/parametrage/services/devise.py
# -----------------------------------------------------------------------------
# Use Case Devise (couche Application). Dépend du repository uniquement.
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.models import Devise
from app.modules.parametrage.repositories import DeviseRepository
from app.modules.parametrage.repositories.taux_change_repository import TauxChangeRepository
from app.modules.parametrage.schemas import DeviseCreate, DeviseUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class DeviseService(BaseParametrageService):
    """Service de gestion des devises (référentiel)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = DeviseRepository(db)
        self._taux_repo = TauxChangeRepository(db)

    async def get_by_id(self, devise_id: int) -> Devise | None:
        """Retourne une devise par id ou None."""
        return await self._repo.find_by_id(devise_id)

    async def get_or_404(self, devise_id: int) -> Devise:
        dev = await self._repo.find_by_id(devise_id)
        if dev is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        return dev

    async def get_by_code(self, code: str) -> Devise | None:
        """Retourne une devise par code ou None."""
        return await self._repo.find_by_code(code)

    async def get_devises(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        inactif_only: bool = False,
        search: str | None = None,
        decimales: int | None = None,
    ) -> tuple[list[Devise], int]:
        """Liste les devises avec filtres optionnels (recherche texte, statut, décimales). Retourne (items, total)."""
        return await self._repo.find_all(
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            inactif_only=inactif_only,
            search=search,
            decimales=decimales,
        )

    async def get_stats(self) -> dict:
        """Statistiques globales sur les devises (total, actives, inactives)."""
        return await self._repo.get_stats()

    async def create(self, data: DeviseCreate) -> Devise:
        """Crée une devise après validation du code (non vide, unique)."""
        code_upper = (data.code or "").strip().upper()
        if not code_upper:
            self._raise_bad_request(Messages.DEVISE_CODE_VIDE)
        if await self._repo.find_by_code(code_upper):
            self._raise_conflict(Messages.DEVISE_CODE_EXISTS.format(code=code_upper))
        dev = Devise(
            code=code_upper,
            libelle=data.libelle,
            symbole=data.symbole,
            decimales=data.decimales,
            actif=data.actif,
        )
        return await self._repo.add(dev)

    async def update(self, devise_id: int, data: DeviseUpdate) -> Devise:
        """Met à jour une devise (champs partiels)."""
        dev = await self.get_or_404(devise_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(dev, key, value)
        return await self._repo.update(dev)

    async def delete(self, devise_id: int) -> None:
        """Supprime une devise. Refuse si elle est utilisée dans des taux de change."""
        dev = await self.get_or_404(devise_id)
        n = await self._taux_repo.count_by_devise_id(devise_id)
        if n > 0:
            self._raise_conflict(Messages.DEVISE_USED_IN_TAUX)
        await self._repo.delete(dev)

