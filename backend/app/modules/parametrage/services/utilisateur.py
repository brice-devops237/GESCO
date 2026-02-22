# app/modules/parametrage/services/utilisateur.py
# -----------------------------------------------------------------------------
# Use Case Utilisateur (couche Application). Hash du mot de passe côté serveur.
# -----------------------------------------------------------------------------

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.modules.parametrage.models import Utilisateur
from app.modules.parametrage.repositories import (
    EntrepriseRepository,
    PointVenteRepository,
    RoleRepository,
    UtilisateurRepository,
)
from app.modules.parametrage.schemas import UtilisateurChangePassword, UtilisateurCreate, UtilisateurUpdate
from app.modules.parametrage.services.base import BaseParametrageService
from app.modules.parametrage.services.messages import Messages


class UtilisateurService(BaseParametrageService):
    """Use cases pour l'agrégat Utilisateur."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self._repo = UtilisateurRepository(db)
        self._entreprise_repo = EntrepriseRepository(db)
        self._role_repo = RoleRepository(db)
        self._pdv_repo = PointVenteRepository(db)

    async def get_utilisateurs(
        self,
        entreprise_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        actif_only: bool = False,
        search: str | None = None,
    ) -> list[Utilisateur]:
        """Liste des utilisateurs d'une entreprise."""
        return await self._repo.find_by_entreprise(
            entreprise_id,
            skip=skip,
            limit=limit,
            actif_only=actif_only,
            search=search,
        )

    async def get_by_login(self, entreprise_id: int, login: str) -> Utilisateur | None:
        """Retourne l'utilisateur par login ou email (pour l'authentification)."""
        return await self._repo.find_by_entreprise_and_login_or_email(entreprise_id, (login or "").strip())

    async def get_by_login_global(self, login: str) -> Utilisateur | None:
        """Retourne l'utilisateur par login ou email, toutes entreprises (connexion sans entreprise_id)."""
        return await self._repo.find_by_login_or_email_global((login or "").strip())

    async def get_or_404(self, utilisateur_id: int) -> Utilisateur:
        user = await self._repo.find_by_id(utilisateur_id)
        if user is None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        return user

    async def create(self, data: UtilisateurCreate) -> Utilisateur:
        if await self._entreprise_repo.find_by_id(data.entreprise_id) is None:
            self._raise_not_found(Messages.ENTREPRISE_NOT_FOUND)
        if await self._role_repo.find_by_id(data.role_id) is None:
            self._raise_not_found(Messages.ROLE_NOT_FOUND)
        if data.point_de_vente_id is not None:
            if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
        login = (data.login or "").strip()
        if not login:
            self._raise_bad_request(Messages.UTILISATEUR_LOGIN_INVALID)
        if await self._repo.find_by_entreprise_and_login(data.entreprise_id, login) is not None:
            self._raise_conflict(Messages.UTILISATEUR_LOGIN_EXISTS.format(login=login))
        entity = Utilisateur(
            entreprise_id=data.entreprise_id,
            point_de_vente_id=data.point_de_vente_id,
            role_id=data.role_id,
            login=login,
            mot_de_passe_hash=hash_password(data.mot_de_passe),
            email=data.email,
            nom=(data.nom or "").strip(),
            prenom=(data.prenom or "").strip() if data.prenom else None,
            telephone=data.telephone,
            actif=data.actif,
        )
        return await self._repo.add(entity)

    async def update(self, utilisateur_id: int, data: UtilisateurUpdate) -> Utilisateur:
        user = await self.get_or_404(utilisateur_id)
        if data.role_id is not None:
            if await self._role_repo.find_by_id(data.role_id) is None:
                self._raise_not_found(Messages.ROLE_NOT_FOUND)
            user.role_id = data.role_id
        if data.point_de_vente_id is not None:
            if await self._pdv_repo.find_by_id(data.point_de_vente_id) is None:
                self._raise_not_found(Messages.POINT_VENTE_NOT_FOUND)
            user.point_de_vente_id = data.point_de_vente_id
        if data.email is not None:
            user.email = data.email
        if data.nom is not None:
            user.nom = data.nom.strip() or user.nom
        if data.prenom is not None:
            user.prenom = data.prenom.strip() if data.prenom else None
        if data.telephone is not None:
            user.telephone = data.telephone
        if data.actif is not None:
            user.actif = data.actif
        if data.mot_de_passe is not None and data.mot_de_passe.strip():
            user.mot_de_passe_hash = hash_password(data.mot_de_passe)
        return await self._repo.update(user)

    async def set_derniere_connexion(self, utilisateur_id: int) -> None:
        """Met à jour la date de dernière connexion (audit, suivi)."""
        user = await self._repo.find_by_id(utilisateur_id)
        if user is not None:
            user.derniere_connexion_at = datetime.now(UTC)
            await self._repo.update(user)

    async def change_password(
        self,
        utilisateur_id: int,
        data: UtilisateurChangePassword,
        *,
        current_user_id: int,
    ) -> None:
        """
        Change le mot de passe d'un utilisateur.
        Si utilisateur_id == current_user_id : ancien_mot_de_passe requis et vérifié.
        Sinon (admin) : seul nouveau_mot_de_passe requis.
        """
        user = await self.get_or_404(utilisateur_id)
        nouveau = (data.nouveau_mot_de_passe or "").strip()
        if len(nouveau) < 8:
            self._raise_bad_request(Messages.UTILISATEUR_MOT_DE_PASSE_REQUIS)
        if utilisateur_id == current_user_id:
            if not (data.ancien_mot_de_passe or "").strip():
                self._raise_bad_request(Messages.UTILISATEUR_MOT_DE_PASSE_INCORRECT)
            if not verify_password(data.ancien_mot_de_passe, user.mot_de_passe_hash):
                self._raise_bad_request(Messages.UTILISATEUR_MOT_DE_PASSE_INCORRECT)
        user.mot_de_passe_hash = hash_password(nouveau)
        await self._repo.update(user)

    async def delete_soft(self, utilisateur_id: int) -> None:
        """Désactivation logique (soft delete) d'un utilisateur."""
        user = await self.get_or_404(utilisateur_id)
        if user.deleted_at is not None:
            self._raise_not_found(Messages.UTILISATEUR_NOT_FOUND)
        user.deleted_at = datetime.now(UTC)
        user.actif = False
        await self._repo.update(user)

