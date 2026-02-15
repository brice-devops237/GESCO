# app/modules/partenaires/services/tiers.py
# -----------------------------------------------------------------------------
# Use Case Tiers (clients / fournisseurs) (couche Application).
# -----------------------------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.catalogue.repositories import CanalVenteRepository
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.partenaires.models import Tiers
from app.modules.partenaires.repositories import TiersRepository, TypeTiersRepository
from app.modules.partenaires.schemas import TiersCreate, TiersUpdate
from app.modules.partenaires.services.base import BasePartenairesService
from app.modules.partenaires.services.messages import Messages


class TiersService(BasePartenairesService):
    """Service de gestion des tiers (clients, fournisseurs)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = TiersRepository(db)
        self._type_tiers_repo = TypeTiersRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._canal_repo = CanalVenteRepository(db)

    async def get_all(
        self,
        *,
        entreprise_id: int | None = None,
        type_tiers_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Tiers], int]:
        """Liste des tiers avec total."""
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            type_tiers_id=type_tiers_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def get_or_404(self, id: int) -> Tiers:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.TIERS_NOT_FOUND)
        return ent

    async def create(self, data: TiersCreate) -> Tiers:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.TIERS_ENTREPRISE_NOT_FOUND)
        if await self._type_tiers_repo.find_by_id(data.type_tiers_id) is None:
            self._raise_not_found(Messages.TIERS_TYPE_TIERS_NOT_FOUND)
        if data.canal_vente_id is not None:
            if await self._canal_repo.find_by_id(data.canal_vente_id) is None:
                self._raise_not_found(Messages.TIERS_CANAL_VENTE_NOT_FOUND)
        code = (data.code or "").strip()
        if not code:
            self._raise_bad_request(Messages.TIERS_CODE_VIDE)
        if await self._repo.exists_by_entreprise_and_code(data.entreprise_id, code):
            self._raise_conflict(Messages.TIERS_CODE_EXISTS.format(code=code))
        ent = Tiers(
            entreprise_id=data.entreprise_id,
            type_tiers_id=data.type_tiers_id,
            code=code,
            raison_sociale=(data.raison_sociale or "").strip(),
            nom_contact=(data.nom or "").strip() or None,
            niu=data.niu,
            adresse=data.adresse,
            ville=data.ville,
            region=data.region,
            pays=data.pays or "CMR",
            telephone=data.telephone,
            telephone_secondaire=data.telephone_secondaire,
            email=data.email,
            canal_vente_id=data.canal_vente_id,
            limite_credit=data.limite_credit,
            delai_paiement_jours=data.delai_paiement_jours,
            compte_bancaire=data.compte_bancaire,
            mobile_money_numero=data.mobile_money_numero,
            mobile_money_operateur=data.mobile_money_operateur,
            segment=data.segment,
            notes=data.notes,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: TiersUpdate) -> Tiers:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "type_tiers_id" in update_data and update_data["type_tiers_id"] is not None:
            if await self._type_tiers_repo.find_by_id(update_data["type_tiers_id"]) is None:
                self._raise_not_found(Messages.TIERS_TYPE_TIERS_NOT_FOUND)
        if "canal_vente_id" in update_data and update_data["canal_vente_id"] is not None:
            if await self._canal_repo.find_by_id(update_data["canal_vente_id"]) is None:
                self._raise_not_found(Messages.TIERS_CANAL_VENTE_NOT_FOUND)
        if "code" in update_data and update_data["code"] is not None:
            code = update_data["code"].strip()
            if not code:
                self._raise_bad_request(Messages.TIERS_CODE_VIDE)
            if await self._repo.exists_by_entreprise_and_code(ent.entreprise_id, code, exclude_id=id):
                self._raise_conflict(Messages.TIERS_CODE_EXISTS.format(code=code))
            update_data["code"] = code
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete_soft(self, id: int) -> None:
        ent = await self.get_or_404(id)
        ent.deleted_at = datetime.now(UTC)
        await self._repo.update(ent)
