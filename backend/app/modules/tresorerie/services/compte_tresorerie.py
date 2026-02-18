# app/modules/tresorerie/services/compte_tresorerie.py
# -----------------------------------------------------------------------------
# Service métier : comptes trésorerie (CRUD).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.parametrage.repositories import DeviseRepository, EntrepriseRepository
from app.modules.tresorerie.models import CompteTresorerie, TypeCompteTresorerie
from app.modules.tresorerie.repositories import CompteTresorerieRepository
from app.modules.tresorerie.schemas import CompteTresorerieCreate, CompteTresorerieUpdate
from app.modules.tresorerie.services.base import BaseTresorerieService
from app.modules.tresorerie.services.messages import Messages


class CompteTresorerieService(BaseTresorerieService):
    """Service de gestion des comptes trésorerie (caisse, bancaire)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = CompteTresorerieRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._devise_repo = DeviseRepository(db)

    def _validate_type_compte(self, value: str) -> None:
        valid = [e.value for e in TypeCompteTresorerie]
        if value not in valid:
            self._raise_bad_request(Messages.TYPE_COMPTE_INVALIDE.format(valeur=value))

    async def get_by_id(self, id: int) -> CompteTresorerie | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> CompteTresorerie:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.COMPTE_TRESORERIE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        actif_only: bool = False,
        type_compte: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[CompteTresorerie], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            actif_only=actif_only,
            type_compte=type_compte,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: CompteTresorerieCreate) -> CompteTresorerie:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._devise_repo.find_by_id(data.devise_id) is None:
            self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        self._validate_type_compte(data.type_compte)
        ent = CompteTresorerie(
            entreprise_id=data.entreprise_id,
            type_compte=data.type_compte,
            libelle=data.libelle.strip(),
            numero_compte=data.numero_compte,
            iban=data.iban,
            devise_id=data.devise_id,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: CompteTresorerieUpdate) -> CompteTresorerie:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "type_compte" in update_data and update_data["type_compte"] is not None:
            self._validate_type_compte(update_data["type_compte"])
        if "devise_id" in update_data and update_data["devise_id"] is not None:
            if await self._devise_repo.find_by_id(update_data["devise_id"]) is None:
                self._raise_not_found(Messages.DEVISE_NOT_FOUND)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

