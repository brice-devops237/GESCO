# app/modules/partenaires/services/contact.py
# -----------------------------------------------------------------------------
# Use Case Contact (personne rattachée à un tiers) (couche Application).
# -----------------------------------------------------------------------------

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.partenaires.models import Contact
from app.modules.partenaires.repositories import ContactRepository, TiersRepository
from app.modules.partenaires.schemas import ContactCreate, ContactUpdate
from app.modules.partenaires.services.base import BasePartenairesService
from app.modules.partenaires.services.messages import Messages


class ContactService(BasePartenairesService):
    """Service de gestion des contacts (personnes rattachées aux tiers)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = ContactRepository(db)
        self._tiers_repo = TiersRepository(db)

    async def get_by_id(self, id: int) -> Contact | None:
        return await self._repo.find_by_id(id)

    async def get_or_404(self, id: int) -> Contact:
        ent = await self._repo.find_by_id(id)
        if ent is None:
            self._raise_not_found(Messages.CONTACT_NOT_FOUND)
        return ent

    async def get_by_tiers(
        self,
        tiers_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
    ) -> tuple[list[Contact], int]:
        return await self._repo.find_by_tiers(
            tiers_id, skip=skip, limit=limit, actif_only=actif_only
        )

    async def create(self, data: ContactCreate) -> Contact:
        if await self._tiers_repo.find_by_id(data.tiers_id) is None:
            self._raise_not_found(Messages.CONTACT_TIERS_NOT_FOUND)
        nom = (data.nom or "").strip()
        if not nom:
            self._raise_bad_request(Messages.CONTACT_NOM_VIDE)
        ent = Contact(
            tiers_id=data.tiers_id,
            nom=nom,
            prenom=data.prenom,
            fonction=data.fonction,
            telephone=data.telephone,
            email=data.email,
            est_principal=data.est_principal,
            actif=data.actif,
        )
        return await self._repo.add(ent)

    async def update(self, id: int, data: ContactUpdate) -> Contact:
        ent = await self.get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)
        if "nom" in update_data:
            update_data["nom"] = (update_data.get("nom") or "").strip()
            if not update_data["nom"]:
                self._raise_bad_request(Messages.CONTACT_NOM_VIDE)
        for key, value in update_data.items():
            setattr(ent, key, value)
        return await self._repo.update(ent)

    async def delete(self, id: int) -> None:
        ent = await self.get_or_404(id)
        await self._repo.delete(ent)
