# app/modules/paie/services/bulletin_paie.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.paie.models import BulletinPaie, LigneBulletinPaie
from app.modules.paie.repositories import (
    BulletinPaieRepository,
    LigneBulletinPaieRepository,
    PeriodePaieRepository,
)
from app.modules.paie.schemas import BulletinPaieCreate, BulletinPaieUpdate
from app.modules.paie.services.base import BasePaieService
from app.modules.paie.services.messages import Messages
from app.modules.parametrage.repositories import EntrepriseRepository
from app.modules.rh.repositories import EmployeRepository


class BulletinPaieService(BasePaieService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = BulletinPaieRepository(db)
        self._ligne_repo = LigneBulletinPaieRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._employe_repo = EmployeRepository(db)
        self._periode_repo = PeriodePaieRepository(db)

    async def get_by_id(self, id: int) -> BulletinPaie | None:
        return await self._repo.find_by_id(id)

    async def get_by_id_with_lignes(self, id: int) -> BulletinPaie | None:
        return await self._repo.find_by_id_with_lignes(id)

    async def get_by_id_with_lignes_or_404(self, id: int) -> BulletinPaie:
        """Retourne le bulletin avec ses lignes ou lève NotFoundError."""
        ent = await self._repo.find_by_id_with_lignes(id)
        if ent is None:
            self._raise_not_found(Messages.BULLETIN_PAIE_NOT_FOUND)
        return ent

    async def get_or_404(self, id: int) -> BulletinPaie:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.BULLETIN_PAIE_NOT_FOUND)
        return ent

    async def get_all(
        self,
        entreprise_id: int,
        *,
        employe_id: int | None = None,
        periode_paie_id: int | None = None,
        statut: str | None = None,
        skip: int = 0,
        limit: int = 200,
    ) -> tuple[list[BulletinPaie], int]:
        if await self._entreprise_repo.find_by_id(entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        return await self._repo.find_all(
            entreprise_id=entreprise_id,
            employe_id=employe_id,
            periode_paie_id=periode_paie_id,
            statut=statut,
            skip=skip,
            limit=limit,
        )

    async def create(self, data: BulletinPaieCreate) -> BulletinPaie:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._employe_repo.find_by_id(data.employe_id) is None:
            self._raise_not_found(Messages.EMPLOYE_NOT_FOUND)
        if await self._periode_repo.find_by_id(data.periode_paie_id) is None:
            self._raise_not_found(Messages.PERIODE_PAIE_NOT_FOUND)
        if await self._repo.find_by_employe_periode(data.entreprise_id, data.employe_id, data.periode_paie_id) is not None:
            self._raise_conflict(Messages.BULLETIN_PAIE_EXISTS)
        if data.statut not in ("brouillon", "valide", "paye"):
            self._raise_bad_request(Messages.STATUT_BULLETIN)
        ent = BulletinPaie(
            entreprise_id=data.entreprise_id,
            employe_id=data.employe_id,
            periode_paie_id=data.periode_paie_id,
            salaire_brut=data.salaire_brut,
            total_gains=data.total_gains,
            total_retenues=data.total_retenues,
            net_a_payer=data.net_a_payer,
            statut=data.statut,
        )
        ent = await self._repo.add(ent)
        for i, ligne in enumerate(data.lignes or []):
            lg = LigneBulletinPaie(
                bulletin_paie_id=ent.id,
                type_element_paie_id=ligne.type_element_paie_id,
                libelle=ligne.libelle,
                type=ligne.type,
                montant=ligne.montant,
                ordre=ligne.ordre or i,
            )
            await self._ligne_repo.add(lg)
        await self._db.flush()
        await self._db.refresh(ent)
        return ent

    async def update(self, id: int, data: BulletinPaieUpdate) -> BulletinPaie:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "statut" in update_data and update_data["statut"] not in ("brouillon", "valide", "paye"):
            self._raise_bad_request(Messages.STATUT_BULLETIN)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

