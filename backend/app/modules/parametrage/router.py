# app/modules/parametrage/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module Paramétrage. Isolation multi-tenant : listes
# scoped par ValidatedEntrepriseId ; GET/PATCH/DELETE/POST vérifient entreprise.
# Devises, taux de change, permissions : référentiels globaux. Extension monde réel.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.core.dependencies import DbSession
from app.core.exceptions import ForbiddenError
from app.modules.parametrage import schemas
from app.modules.parametrage.dependencies import CurrentUser, RequirePermission, ValidatedEntrepriseId
from app.modules.parametrage.services.affectation_utilisateur_pdv import (
    AffectationUtilisateurPdvService,
)
from app.modules.parametrage.services.devise import DeviseService
from app.modules.parametrage.services.entreprise import EntrepriseService
from app.modules.parametrage.services.permission import PermissionService
from app.modules.parametrage.services.point_vente import PointVenteService
from app.modules.parametrage.services.role import RoleService
from app.modules.parametrage.services.taux_change import TauxChangeService
from app.modules.parametrage.services.utilisateur import UtilisateurService

router = APIRouter(
    prefix="/parametrage",
    responses={401: {"description": "Non authentifié"}, 403: {"description": "Droits insuffisants"}},
)

TAG_ENTREPRISES = "Paramétrage - Entreprises"
TAG_DEVISES = "Paramétrage - Devises"
TAG_TAUX_CHANGE = "Paramétrage - Taux de change"
TAG_POINTS_VENTE = "Paramétrage - Points de vente"
TAG_ROLES = "Paramétrage - Rôles"
TAG_PERMISSIONS = "Paramétrage - Permissions"
TAG_UTILISATEURS = "Paramétrage - Utilisateurs"
TAG_AFFECTATIONS_PDV = "Paramétrage - Affectations utilisateur-PDV"


# --- Entreprises ---

@router.get("/entreprises/stats", response_model=schemas.EntrepriseStatsResponse, tags=[TAG_ENTREPRISES])
async def get_entreprises_stats(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Statistiques globales sur les entreprises (total, actives, inactives, répartition par régime et pays)."""
    return await EntrepriseService(db).get_stats()


@router.get("/entreprises", response_model=schemas.ListEntreprisesResponse, tags=[TAG_ENTREPRISES])
async def list_entreprises(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    actif_only: bool = False,
    inactif_only: bool = False,
    search: str | None = None,
):
    """Liste paginée des entreprises (items + total pour la pagination)."""
    service = EntrepriseService(db)
    items, total = await service.get_entreprises(
        skip=skip, limit=limit, actif_only=actif_only, inactif_only=inactif_only, search=search
    )
    return schemas.ListEntreprisesResponse(items=items, total=total)


@router.get("/entreprises/{entreprise_id}", response_model=schemas.EntrepriseResponse, tags=[TAG_ENTREPRISES])
async def get_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'une entreprise par id. Accessible pour toute entreprise si l'utilisateur a la permission parametrage read (liste / édition)."""
    return await EntrepriseService(db).get_or_404(entreprise_id)


@router.post("/entreprises", response_model=schemas.EntrepriseResponse, status_code=201, tags=[TAG_ENTREPRISES])
async def create_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.EntrepriseCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'une entreprise."""
    return await EntrepriseService(db).create(data)


@router.patch("/entreprises/{entreprise_id}", response_model=schemas.EntrepriseResponse, tags=[TAG_ENTREPRISES])
async def update_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    data: schemas.EntrepriseUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'une entreprise."""
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await EntrepriseService(db).update(entreprise_id, data)


@router.delete("/entreprises/{entreprise_id}", status_code=204, tags=[TAG_ENTREPRISES])
async def delete_entreprise(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Soft delete d'une entreprise."""
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await EntrepriseService(db).delete_soft(entreprise_id)


# --- Devises ---

@router.get("/devises/stats", response_model=schemas.DeviseStatsResponse, tags=[TAG_DEVISES])
async def get_devises_stats(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Statistiques globales sur les devises (total, actives, inactives)."""
    data = await DeviseService(db).get_stats()
    return schemas.DeviseStatsResponse(**data)


@router.get("/devises", response_model=schemas.ListDevisesResponse, tags=[TAG_DEVISES])
async def list_devises(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actif_only: bool = False,
    inactif_only: bool = Query(False, description="Si True, ne retourne que les devises inactives"),
    search: str | None = Query(None, description="Recherche sur code, libellé, symbole"),
    decimales: int | None = Query(None, ge=0, le=6, description="Filtrer par nombre de décimales"),
):
    """Liste paginée des devises (items + total)."""
    items, total = await DeviseService(db).get_devises(
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        inactif_only=inactif_only,
        search=search,
        decimales=decimales,
    )
    return schemas.ListDevisesResponse(items=items, total=total)


@router.get("/devises/{devise_id}", response_model=schemas.DeviseResponse, tags=[TAG_DEVISES])
async def get_devise(
    db: DbSession,
    current_user: CurrentUser,
    devise_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'une devise par id."""
    return await DeviseService(db).get_or_404(devise_id)


@router.post("/devises", response_model=schemas.DeviseResponse, status_code=201, tags=[TAG_DEVISES])
async def create_devise(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.DeviseCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'une devise."""
    return await DeviseService(db).create(data)


@router.patch("/devises/{devise_id}", response_model=schemas.DeviseResponse, tags=[TAG_DEVISES])
async def update_devise(
    db: DbSession,
    current_user: CurrentUser,
    devise_id: int,
    data: schemas.DeviseUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'une devise."""
    return await DeviseService(db).update(devise_id, data)


@router.delete("/devises/{devise_id}", status_code=204, tags=[TAG_DEVISES])
async def delete_devise(
    db: DbSession,
    current_user: CurrentUser,
    devise_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Suppression d'une devise. Refusée si la devise est utilisée dans des taux de change."""
    await DeviseService(db).delete(devise_id)
    return Response(status_code=204)


# --- Taux de change ---

# Chemin à 3 segments pour éviter que GET /taux-change/{taux_id} matche "stats" comme taux_id (422)
@router.get("/taux-change/stats/summary", response_model=schemas.TauxChangeStatsResponse, tags=[TAG_TAUX_CHANGE])
async def get_taux_change_stats(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Statistiques globales sur les taux de change (total)."""
    data = await TauxChangeService(db).get_stats()
    return schemas.TauxChangeStatsResponse(total=int(data["total"]))


@router.get("/taux-change", response_model=schemas.ListTauxChangeResponse, tags=[TAG_TAUX_CHANGE])
async def list_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    devise_from_id: int | None = None,
    devise_to_id: int | None = None,
    date_effet_min: str | None = Query(None, description="Date d'effet min (YYYY-MM-DD)"),
    date_effet_max: str | None = Query(None, description="Date d'effet max (YYYY-MM-DD)"),
):
    """Liste paginée des taux de change (items + total)."""
    from datetime import date as date_cls
    d_min = date_cls.fromisoformat(date_effet_min) if date_effet_min else None
    d_max = date_cls.fromisoformat(date_effet_max) if date_effet_max else None
    items, total = await TauxChangeService(db).get_taux_changes(
        skip=skip,
        limit=limit,
        devise_from_id=devise_from_id,
        devise_to_id=devise_to_id,
        date_effet_min=d_min,
        date_effet_max=d_max,
    )
    return schemas.ListTauxChangeResponse(items=items, total=total)


@router.get("/taux-change/{taux_id}", response_model=schemas.TauxChangeResponse, tags=[TAG_TAUX_CHANGE])
async def get_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    taux_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'un taux de change par id."""
    return await TauxChangeService(db).get_or_404(taux_id)


@router.post("/taux-change", response_model=schemas.TauxChangeResponse, status_code=201, tags=[TAG_TAUX_CHANGE])
async def create_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.TauxChangeCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'un taux de change."""
    return await TauxChangeService(db).create(data)


@router.patch("/taux-change/{taux_id}", response_model=schemas.TauxChangeResponse, tags=[TAG_TAUX_CHANGE])
async def update_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    taux_id: int,
    data: schemas.TauxChangeUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'un taux de change (taux, source)."""
    return await TauxChangeService(db).update(taux_id, data)


@router.delete("/taux-change/{taux_id}", status_code=204, tags=[TAG_TAUX_CHANGE])
async def delete_taux_change(
    db: DbSession,
    current_user: CurrentUser,
    taux_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Suppression d'un taux de change."""
    await TauxChangeService(db).delete(taux_id)
    return Response(status_code=204)


# --- Points de vente ---

@router.get("/entreprises/{entreprise_id}/points-vente/stats", response_model=schemas.PointVenteStatsResponse, tags=[TAG_POINTS_VENTE])
async def get_points_vente_stats(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Statistiques des points de vente d'une entreprise."""
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PointVenteService(db).get_stats(entreprise_id)


@router.get("/entreprises/{entreprise_id}/points-vente", response_model=schemas.ListPointsVenteResponse, tags=[TAG_POINTS_VENTE])
async def list_points_vente(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    actif_only: bool = False,
    inactif_only: bool = Query(False, description="Si True, ne retourne que les points inactifs"),
    search: str | None = Query(None, description="Recherche sur code, libellé, ville"),
    type: str | None = Query(None, description="Filtrer par type : principal, secondaire, depot"),
):
    """Liste paginée des points de vente d'une entreprise (items + total)."""
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    items, total = await PointVenteService(db).get_points_vente(
        entreprise_id,
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        inactif_only=inactif_only,
        search=search,
        type_filter=type,
    )
    return schemas.ListPointsVenteResponse(items=items, total=total)


@router.get("/points-vente/{point_vente_id}", response_model=schemas.PointDeVenteResponse, tags=[TAG_POINTS_VENTE])
async def get_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'un point de vente par id."""
    ent = await PointVenteService(db).get_or_404(point_vente_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/points-vente", response_model=schemas.PointDeVenteResponse, status_code=201, tags=[TAG_POINTS_VENTE])
async def create_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PointDeVenteCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'un point de vente."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PointVenteService(db).create(data)


@router.patch("/points-vente/{point_vente_id}", response_model=schemas.PointDeVenteResponse, tags=[TAG_POINTS_VENTE])
async def update_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
    data: schemas.PointDeVenteUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'un point de vente."""
    ent = await PointVenteService(db).get_or_404(point_vente_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await PointVenteService(db).update(point_vente_id, data)


@router.delete("/points-vente/{point_vente_id}", status_code=204, tags=[TAG_POINTS_VENTE])
async def delete_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Suppression logique (soft delete) d'un point de vente."""
    ent = await PointVenteService(db).get_or_404(point_vente_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await PointVenteService(db).delete_soft(point_vente_id)
    return Response(status_code=204)


# --- Rôles ---

@router.get("/roles", response_model=list[schemas.RoleResponse], tags=[TAG_ROLES])
async def list_roles(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: ValidatedEntrepriseId,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """Liste des rôles (filtrée par entreprise de l'utilisateur)."""
    return await RoleService(db).get_roles(
        entreprise_id=entreprise_id, skip=skip, limit=limit
    )


@router.get("/roles/{role_id}", response_model=schemas.RoleResponse, tags=[TAG_ROLES])
async def get_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'un rôle par id."""
    ent = await RoleService(db).get_or_404(role_id)
    if ent.entreprise_id is not None and ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/roles", response_model=schemas.RoleResponse, status_code=201, tags=[TAG_ROLES])
async def create_role(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.RoleCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'un rôle."""
    if data.entreprise_id is not None and data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await RoleService(db).create(data)


@router.patch("/roles/{role_id}", response_model=schemas.RoleResponse, tags=[TAG_ROLES])
async def update_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
    data: schemas.RoleUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'un rôle."""
    ent = await RoleService(db).get_or_404(role_id)
    if ent.entreprise_id is not None and ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await RoleService(db).update(role_id, data)


# --- Permissions ---

@router.get(
    "/permissions",
    response_model=list[schemas.PermissionWithRolesResponse],
    tags=[TAG_PERMISSIONS],
)
async def list_permissions(
    db: DbSession,
    current_user: CurrentUser,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=200),
    module: str | None = None,
    include_roles: bool = Query(False, description="Inclure les rôles affectés à chaque permission"),
):
    """Liste des permissions (référentiel)."""
    service = PermissionService(db)
    if include_roles:
        return await service.get_permissions_with_roles(
            skip=skip, limit=limit, module=module
        )
    perms = await service.get_permissions(
        skip=skip, limit=limit, module=module
    )
    return [
        schemas.PermissionWithRolesResponse(
            id=p.id, module=p.module, action=p.action, libelle=p.libelle, roles=[]
        )
        for p in perms
    ]


@router.get("/permissions/{permission_id}", response_model=schemas.PermissionResponse, tags=[TAG_PERMISSIONS])
async def get_permission(
    db: DbSession,
    current_user: CurrentUser,
    permission_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'une permission par id."""
    return await PermissionService(db).get_or_404(permission_id)


@router.post("/permissions", response_model=schemas.PermissionResponse, status_code=201, tags=[TAG_PERMISSIONS])
async def create_permission(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PermissionCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'une permission."""
    return await PermissionService(db).create(data)


@router.post("/permissions-roles", response_model=schemas.PermissionRoleResponse, status_code=201, tags=[TAG_PERMISSIONS])
async def add_permission_to_role(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.PermissionRoleCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Associe une permission à un rôle."""
    return await PermissionService(db).add_permission_to_role(data)


@router.delete("/permissions-roles/{role_id}/{permission_id}", status_code=204, tags=[TAG_PERMISSIONS])
async def remove_permission_from_role(
    db: DbSession,
    current_user: CurrentUser,
    role_id: int,
    permission_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Retire une permission d'un rôle."""
    await PermissionService(db).remove_permission_from_role(role_id, permission_id)


# --- Utilisateurs ---

@router.get("/entreprises/{entreprise_id}/utilisateurs", response_model=list[schemas.UtilisateurResponse], tags=[TAG_UTILISATEURS])
async def list_utilisateurs(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    actif_only: bool = False,
    search: str | None = None,
):
    """Liste des utilisateurs d'une entreprise."""
    if entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await UtilisateurService(db).get_utilisateurs(
        entreprise_id,
        skip=skip,
        limit=limit,
        actif_only=actif_only,
        search=search,
    )


@router.get("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse, tags=[TAG_UTILISATEURS])
async def get_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Détail d'un utilisateur par id."""
    ent = await UtilisateurService(db).get_or_404(utilisateur_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return ent


@router.post("/utilisateurs", response_model=schemas.UtilisateurResponse, status_code=201, tags=[TAG_UTILISATEURS])
async def create_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.UtilisateurCreate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Création d'un utilisateur (mot de passe hashé côté serveur)."""
    if data.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await UtilisateurService(db).create(data)


async def _update_utilisateur_impl(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    data: schemas.UtilisateurUpdate,
):
    """Logique commune PATCH/PUT."""
    ent = await UtilisateurService(db).get_or_404(utilisateur_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await UtilisateurService(db).update(utilisateur_id, data)


@router.patch("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse, tags=[TAG_UTILISATEURS])
async def update_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    data: schemas.UtilisateurUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour partielle d'un utilisateur."""
    return await _update_utilisateur_impl(db, current_user, utilisateur_id, data)


@router.put("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse, tags=[TAG_UTILISATEURS])
async def update_utilisateur_put(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    data: schemas.UtilisateurUpdate,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Mise à jour d'un utilisateur (alias de PATCH)."""
    return await _update_utilisateur_impl(db, current_user, utilisateur_id, data)


@router.patch(
    "/utilisateurs/{utilisateur_id}/changer-mot-de-passe",
    status_code=204,
    tags=[TAG_UTILISATEURS],
)
async def changer_mot_de_passe_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    data: schemas.UtilisateurChangePassword,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """
    Change le mot de passe d'un utilisateur.
    Si c'est son propre compte : ancien_mot_de_passe requis.
    Si admin (autre utilisateur) : seul nouveau_mot_de_passe requis.
    """
    ent = await UtilisateurService(db).get_or_404(utilisateur_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await UtilisateurService(db).change_password(
        utilisateur_id, data, current_user_id=current_user.id
    )
    return Response(status_code=204)


@router.delete("/utilisateurs/{utilisateur_id}", status_code=204, tags=[TAG_UTILISATEURS])
async def delete_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Désactivation logique (soft delete) d'un utilisateur."""
    ent = await UtilisateurService(db).get_or_404(utilisateur_id)
    if ent.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await UtilisateurService(db).delete_soft(utilisateur_id)
    return Response(status_code=204)


# --- Affectations utilisateur / PDV ---

@router.get("/utilisateurs/{utilisateur_id}/affectations-pdv", response_model=list[schemas.AffectationUtilisateurPdvResponse], tags=[TAG_AFFECTATIONS_PDV])
async def list_affectations_by_utilisateur(
    db: DbSession,
    current_user: CurrentUser,
    utilisateur_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Liste des affectations PDV pour un utilisateur."""
    user = await UtilisateurService(db).get_or_404(utilisateur_id)
    if user.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await AffectationUtilisateurPdvService(db).get_affectations_by_utilisateur(
        utilisateur_id
    )


@router.get("/points-vente/{point_vente_id}/affectations", response_model=list[schemas.AffectationUtilisateurPdvResponse], tags=[TAG_AFFECTATIONS_PDV])
async def list_affectations_by_point_vente(
    db: DbSession,
    current_user: CurrentUser,
    point_vente_id: int,
    _perm: None = RequirePermission("parametrage", "read"),
):
    """Liste des affectations utilisateurs pour un point de vente."""
    pdv = await PointVenteService(db).get_or_404(point_vente_id)
    if pdv.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await AffectationUtilisateurPdvService(db).get_affectations_by_point_vente(
        point_vente_id
    )


@router.post("/affectations-utilisateur-pdv", response_model=schemas.AffectationUtilisateurPdvResponse, status_code=201, tags=[TAG_AFFECTATIONS_PDV])
async def create_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    data: schemas.AffectationUtilisateurPdvCreate,
):
    """Crée une affectation utilisateur <-> point de vente."""
    user = await UtilisateurService(db).get_or_404(data.utilisateur_id)
    if user.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    pdv = await PointVenteService(db).get_or_404(data.point_de_vente_id)
    if pdv.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await AffectationUtilisateurPdvService(db).create(data)


@router.patch("/affectations-utilisateur-pdv/{affectation_id}", response_model=schemas.AffectationUtilisateurPdvResponse, tags=[TAG_AFFECTATIONS_PDV])
async def update_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    affectation_id: int,
    data: schemas.AffectationUtilisateurPdvUpdate,
):
    """Met à jour une affectation (ex. est_principal)."""
    a = await AffectationUtilisateurPdvService(db).get_or_404(affectation_id)
    user = await UtilisateurService(db).get_or_404(a.utilisateur_id)
    if user.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    return await AffectationUtilisateurPdvService(db).update(affectation_id, data)


@router.delete("/affectations-utilisateur-pdv/{affectation_id}", status_code=204, tags=[TAG_AFFECTATIONS_PDV])
async def delete_affectation_pdv(
    db: DbSession,
    current_user: CurrentUser,
    affectation_id: int,
    _perm: None = RequirePermission("parametrage", "write"),
):
    """Supprime une affectation utilisateur-PDV."""
    a = await AffectationUtilisateurPdvService(db).get_or_404(affectation_id)
    user = await UtilisateurService(db).get_or_404(a.utilisateur_id)
    if user.entreprise_id != current_user.entreprise_id:
        raise ForbiddenError(detail="Accès à une autre entreprise non autorisé", code="FORBIDDEN_ENTREPRISE")
    await AffectationUtilisateurPdvService(db).delete(affectation_id)

