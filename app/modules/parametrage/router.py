# app/modules/parametrage/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Paramétrage (A.1). Chaque route instancie
# le service concerné avec la session DB et appelle les méthodes de la classe.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage import schemas
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.parametrage.services.affectation_utilisateur_pdv import AffectationUtilisateurPdvService
from app.modules.parametrage.services.devise import DeviseService
from app.modules.parametrage.services.entreprise import EntrepriseService
from app.modules.parametrage.services.permission import PermissionService
from app.modules.parametrage.services.point_vente import PointVenteService
from app.modules.parametrage.services.role import RoleService
from app.modules.parametrage.services.taux_change import TauxChangeService
from app.modules.parametrage.services.utilisateur import UtilisateurService

router = APIRouter(prefix="/parametrage", tags=["Paramétrage"])


# --- Entreprises ---

@router.get("/entreprises", response_model=list[schemas.EntrepriseResponse])
async def list_entreprises(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste paginée des entreprises."""
    service = EntrepriseService(db)
    items, _ = await service.get_entreprises(
        skip=skip, limit=limit, actif_only=actif_only, search=search
    )
    return items


@router.get("/entreprises/{entreprise_id}", response_model=schemas.EntrepriseResponse)
async def get_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
):
    """Détail d'une entreprise par id."""
    return await EntrepriseService(db).get_or_404(entreprise_id)


@router.post("/entreprises", response_model=schemas.EntrepriseResponse, status_code=201)
async def create_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.EntrepriseCreate,
):
    """Création d'une entreprise."""
    return await EntrepriseService(db).create(data)


@router.patch("/entreprises/{entreprise_id}", response_model=schemas.EntrepriseResponse)
async def update_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    data: schemas.EntrepriseUpdate,
):
    """Mise à jour partielle d'une entreprise."""
    return await EntrepriseService(db).update(entreprise_id, data)


@router.delete("/entreprises/{entreprise_id}", status_code=204)
async def delete_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
):
    """Soft delete d'une entreprise."""
    await EntrepriseService(db).delete_soft(entreprise_id)


# --- Devises ---

@router.get("/devises", response_model=list[schemas.DeviseResponse])
async def list_devises(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actif_only: bool = False,
):
    """Liste des devises (référentiel)."""
    return await DeviseService(db).get_devises(
        skip=skip, limit=limit, actif_only=actif_only
    )


@router.get("/devises/{devise_id}", response_model=schemas.DeviseResponse)
async def get_devise(
    db: DbSession,
    current_user: CurrentUser,
    devise_id: int,
):
    """Détail d'une devise par id."""
    return await DeviseService(db).get_or_404(devise_id)


@router.post("/devises", response_model=schemas.DeviseResponse, status_code=201)
async def create_devise(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.DeviseCreate,
):
    """Création d'une devise."""
    return await DeviseService(db).create(data)


@router.patch("/devises/{devise_id}", response_model=schemas.DeviseResponse)
async def update_devise(
    db: DbSession,
    current_user: CurrentUser,
    devise_id: int,
    data: schemas.DeviseUpdate,
):
    """Mise à jour partielle d'une devise."""
    return await DeviseService(db).update(devise_id, data)


# --- Taux de change ---

@router.get("/taux-change", response_model=list[schemas.TauxChangeResponse])
async def list_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    devise_from_id: int | None = None,
    devise_to_id: int | None = None,
):
    """Liste des taux de change (filtres optionnels)."""
    return await TauxChangeService(db).get_taux_changes(
        skip=skip,
        limit=limit,
        devise_from_id=devise_from_id,
        devise_to_id=devise_to_id,
    )


@router.get("/taux-change/{taux_id}", response_model=schemas.TauxChangeResponse)
async def get_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    taux_id: int,
):
    """Détail d'un taux de change par id."""
    return await TauxChangeService(db).get_or_404(taux_id)


@router.post("/taux-change", response_model=schemas.TauxChangeResponse, status_code=201)
async def create_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.TauxChangeCreate,
):
    """Création d'un taux de change."""
    return await TauxChangeService(db).create(data)


# --- Points de vente ---

@router.get("/entreprises/{entreprise_id}/points-vente", response_model=list[schemas.PointDeVenteResponse])
async def list_points_vente(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actif_only: bool = False,
):
    """Liste des points de vente d'une entreprise."""
    return await PointVenteService(db).get_points_vente(
        entreprise_id, skip=skip, limit=limit, actif_only=actif_only
    )


@router.get("/points-vente/{point_vente_id}", response_model=schemas.PointDeVenteResponse)
async def get_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
):
    """Détail d'un point de vente par id."""
    return await PointVenteService(db).get_or_404(point_vente_id)


@router.post("/points-vente", response_model=schemas.PointDeVenteResponse, status_code=201)
async def create_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PointDeVenteCreate,
):
    """Création d'un point de vente."""
    return await PointVenteService(db).create(data)


@router.patch("/points-vente/{point_vente_id}", response_model=schemas.PointDeVenteResponse)
async def update_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
    data: schemas.PointDeVenteUpdate,
):
    """Mise à jour partielle d'un point de vente."""
    return await PointVenteService(db).update(point_vente_id, data)


# --- Rôles ---

@router.get("/roles", response_model=list[schemas.RoleResponse])
async def list_roles(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Liste des rôles (optionnellement filtrée par entreprise)."""
    return await RoleService(db).get_roles(
        entreprise_id=entreprise_id, skip=skip, limit=limit
    )


@router.get("/roles/{role_id}", response_model=schemas.RoleResponse)
async def get_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
):
    """Détail d'un rôle par id."""
    return await RoleService(db).get_or_404(role_id)


@router.post("/roles", response_model=schemas.RoleResponse, status_code=201)
async def create_role(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.RoleCreate,
):
    """Création d'un rôle."""
    return await RoleService(db).create(data)


@router.patch("/roles/{role_id}", response_model=schemas.RoleResponse)
async def update_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
    data: schemas.RoleUpdate,
):
    """Mise à jour partielle d'un rôle."""
    return await RoleService(db).update(role_id, data)


# --- Permissions ---

@router.get("/permissions", response_model=list[schemas.PermissionResponse])
async def list_permissions(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=200),
    module: str | None = None,
):
    """Liste des permissions (référentiel)."""
    return await PermissionService(db).get_permissions(
        skip=skip, limit=limit, module=module
    )


@router.get("/permissions/{permission_id}", response_model=schemas.PermissionResponse)
async def get_permission(
    db: DbSession,
    current_user: CurrentUser,
    permission_id: int,
):
    """Détail d'une permission par id."""
    return await PermissionService(db).get_or_404(permission_id)


@router.post("/permissions", response_model=schemas.PermissionResponse, status_code=201)
async def create_permission(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PermissionCreate,
):
    """Création d'une permission."""
    return await PermissionService(db).create(data)


@router.post("/permissions-roles", response_model=schemas.PermissionRoleResponse, status_code=201)
async def add_permission_to_role(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PermissionRoleCreate,
):
    """Associe une permission à un rôle."""
    return await PermissionService(db).add_permission_to_role(data)


@router.delete("/permissions-roles/{role_id}/{permission_id}", status_code=204)
async def remove_permission_from_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
    permission_id: int,
):
    """Retire une permission d'un rôle."""
    await PermissionService(db).remove_permission_from_role(role_id, permission_id)


# --- Utilisateurs ---

@router.get("/entreprises/{entreprise_id}/utilisateurs", response_model=list[schemas.UtilisateurResponse])
async def list_utilisateurs(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des utilisateurs d'une entreprise."""
    return await UtilisateurService(db).get_utilisateurs(
        entreprise_id,
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        search=search,
    )


@router.get("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
async def get_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
):
    """Détail d'un utilisateur par id."""
    return await UtilisateurService(db).get_or_404(utilisateur_id)


@router.post("/utilisateurs", response_model=schemas.UtilisateurResponse, status_code=201)
async def create_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.UtilisateurCreate,
):
    """Création d'un utilisateur (mot de passe hashé côté serveur)."""
    return await UtilisateurService(db).create(data)


@router.patch("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
async def update_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    data: schemas.UtilisateurUpdate,
):
    """Mise à jour partielle d'un utilisateur."""
    return await UtilisateurService(db).update(utilisateur_id, data)


# --- Affectations utilisateur / PDV ---

@router.get("/utilisateurs/{utilisateur_id}/affectations-pdv", response_model=list[schemas.AffectationUtilisateurPdvResponse])
async def list_affectations_by_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
):
    """Liste des affectations PDV pour un utilisateur."""
    return await AffectationUtilisateurPdvService(db).get_affectations_by_utilisateur(
        utilisateur_id
    )


@router.get("/points-vente/{point_vente_id}/affectations", response_model=list[schemas.AffectationUtilisateurPdvResponse])
async def list_affectations_by_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
):
    """Liste des affectations utilisateurs pour un point de vente."""
    return await AffectationUtilisateurPdvService(db).get_affectations_by_point_vente(
        point_vente_id
    )


@router.post("/affectations-utilisateur-pdv", response_model=schemas.AffectationUtilisateurPdvResponse, status_code=201)
async def create_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.AffectationUtilisateurPdvCreate,
):
    """Crée une affectation utilisateur <-> point de vente."""
    return await AffectationUtilisateurPdvService(db).create(data)


@router.patch("/affectations-utilisateur-pdv/{affectation_id}", response_model=schemas.AffectationUtilisateurPdvResponse)
async def update_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    affectation_id: int,
    data: schemas.AffectationUtilisateurPdvUpdate,
):
    """Met à jour une affectation (ex. est_principal)."""
    return await AffectationUtilisateurPdvService(db).update(affectation_id, data)


@router.delete("/affectations-utilisateur-pdv/{affectation_id}", status_code=204)
async def delete_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    affectation_id: int,
):
    """Supprime une affectation utilisateur-PDV."""
    await AffectationUtilisateurPdvService(db).delete(affectation_id)
