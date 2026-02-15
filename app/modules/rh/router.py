# app/modules/rh/router.py
# -----------------------------------------------------------------------------
# Routes API v1 pour le module RH. Préfixe /rh.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.modules.parametrage.dependencies import CurrentUser
from app.modules.rh import schemas
from app.modules.rh.services import (
    AvanceService,
    CommissionService,
    DemandeCongeService,
    DepartementService,
    EmployeService,
    ObjectifService,
    PosteService,
    SoldeCongeService,
    TauxCommissionService,
    TypeCongeService,
    TypeContratService,
)

router = APIRouter(prefix="/rh")

TAG_DEPARTEMENTS = "RH - Départements"
TAG_POSTES = "RH - Postes"
TAG_TYPES_CONTRAT = "RH - Types de contrat"
TAG_EMPLOYES = "RH - Employés"
TAG_TYPES_CONGE = "RH - Types de congé"
TAG_DEMANDES_CONGE = "RH - Demandes de congé"
TAG_SOLDES_CONGE = "RH - Soldes de congé"
TAG_OBJECTIFS = "RH - Objectifs"
TAG_TAUX_COMMISSION = "RH - Taux de commission"
TAG_COMMISSIONS = "RH - Commissions"
TAG_AVANCES = "RH - Avances"


# --- Départements ---
@router.get("/departements", response_model=list[schemas.DepartementResponse], tags=[TAG_DEPARTEMENTS])
async def list_departements(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await DepartementService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/departements/{id}", response_model=schemas.DepartementResponse, tags=[TAG_DEPARTEMENTS])
async def get_departement(db: DbSession, current_user: CurrentUser, id: int):
    return await DepartementService(db).get_or_404(id)


@router.post("/departements", response_model=schemas.DepartementResponse, status_code=201, tags=[TAG_DEPARTEMENTS])
async def create_departement(db: DbSession, current_user: CurrentUser, data: schemas.DepartementCreate):
    return await DepartementService(db).create(data)


@router.patch("/departements/{id}", response_model=schemas.DepartementResponse, tags=[TAG_DEPARTEMENTS])
async def update_departement(db: DbSession, current_user: CurrentUser, id: int, data: schemas.DepartementUpdate):
    return await DepartementService(db).update(id, data)


# --- Postes ---
@router.get("/postes", response_model=list[schemas.PosteResponse], tags=[TAG_POSTES])
async def list_postes(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    departement_id: int | None = None,
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await PosteService(db).get_all(
        entreprise_id=entreprise_id,
        departement_id=departement_id,
        actif_only=actif_only,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/postes/{id}", response_model=schemas.PosteResponse, tags=[TAG_POSTES])
async def get_poste(db: DbSession, current_user: CurrentUser, id: int):
    return await PosteService(db).get_or_404(id)


@router.post("/postes", response_model=schemas.PosteResponse, status_code=201, tags=[TAG_POSTES])
async def create_poste(db: DbSession, current_user: CurrentUser, data: schemas.PosteCreate):
    return await PosteService(db).create(data)


@router.patch("/postes/{id}", response_model=schemas.PosteResponse, tags=[TAG_POSTES])
async def update_poste(db: DbSession, current_user: CurrentUser, id: int, data: schemas.PosteUpdate):
    return await PosteService(db).update(id, data)


# --- Types de contrat ---
@router.get("/types-contrat", response_model=list[schemas.TypeContratResponse], tags=[TAG_TYPES_CONTRAT])
async def list_types_contrat(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await TypeContratService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/types-contrat/{id}", response_model=schemas.TypeContratResponse, tags=[TAG_TYPES_CONTRAT])
async def get_type_contrat(db: DbSession, current_user: CurrentUser, id: int):
    return await TypeContratService(db).get_or_404(id)


@router.post("/types-contrat", response_model=schemas.TypeContratResponse, status_code=201, tags=[TAG_TYPES_CONTRAT])
async def create_type_contrat(db: DbSession, current_user: CurrentUser, data: schemas.TypeContratCreate):
    return await TypeContratService(db).create(data)


@router.patch("/types-contrat/{id}", response_model=schemas.TypeContratResponse, tags=[TAG_TYPES_CONTRAT])
async def update_type_contrat(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TypeContratUpdate):
    return await TypeContratService(db).update(id, data)


# --- Employés ---
@router.get("/employes", response_model=list[schemas.EmployeResponse], tags=[TAG_EMPLOYES])
async def list_employes(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    departement_id: int | None = None,
    poste_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
):
    items, _ = await EmployeService(db).get_all(
        entreprise_id=entreprise_id,
        actif_only=actif_only,
        departement_id=departement_id,
        poste_id=poste_id,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/employes/{id}", response_model=schemas.EmployeResponse, tags=[TAG_EMPLOYES])
async def get_employe(db: DbSession, current_user: CurrentUser, id: int):
    return await EmployeService(db).get_or_404(id)


@router.post("/employes", response_model=schemas.EmployeResponse, status_code=201, tags=[TAG_EMPLOYES])
async def create_employe(db: DbSession, current_user: CurrentUser, data: schemas.EmployeCreate):
    return await EmployeService(db).create(data)


@router.patch("/employes/{id}", response_model=schemas.EmployeResponse, tags=[TAG_EMPLOYES])
async def update_employe(db: DbSession, current_user: CurrentUser, id: int, data: schemas.EmployeUpdate):
    return await EmployeService(db).update(id, data)


# --- Types de congé ---
@router.get("/types-conge", response_model=list[schemas.TypeCongeResponse], tags=[TAG_TYPES_CONGE])
async def list_types_conge(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await TypeCongeService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/types-conge/{id}", response_model=schemas.TypeCongeResponse, tags=[TAG_TYPES_CONGE])
async def get_type_conge(db: DbSession, current_user: CurrentUser, id: int):
    return await TypeCongeService(db).get_or_404(id)


@router.post("/types-conge", response_model=schemas.TypeCongeResponse, status_code=201, tags=[TAG_TYPES_CONGE])
async def create_type_conge(db: DbSession, current_user: CurrentUser, data: schemas.TypeCongeCreate):
    return await TypeCongeService(db).create(data)


@router.patch("/types-conge/{id}", response_model=schemas.TypeCongeResponse, tags=[TAG_TYPES_CONGE])
async def update_type_conge(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TypeCongeUpdate):
    return await TypeCongeService(db).update(id, data)


# --- Demandes de congé ---
@router.get("/demandes-conge", response_model=list[schemas.DemandeCongeResponse], tags=[TAG_DEMANDES_CONGE])
async def list_demandes_conge(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    statut: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await DemandeCongeService(db).get_all(
        entreprise_id=entreprise_id,
        employe_id=employe_id,
        statut=statut,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/demandes-conge/{id}", response_model=schemas.DemandeCongeResponse, tags=[TAG_DEMANDES_CONGE])
async def get_demande_conge(db: DbSession, current_user: CurrentUser, id: int):
    return await DemandeCongeService(db).get_or_404(id)


@router.post("/demandes-conge", response_model=schemas.DemandeCongeResponse, status_code=201, tags=[TAG_DEMANDES_CONGE])
async def create_demande_conge(db: DbSession, current_user: CurrentUser, data: schemas.DemandeCongeCreate):
    return await DemandeCongeService(db).create(data)


@router.patch("/demandes-conge/{id}", response_model=schemas.DemandeCongeResponse, tags=[TAG_DEMANDES_CONGE])
async def update_demande_conge(db: DbSession, current_user: CurrentUser, id: int, data: schemas.DemandeCongeUpdate):
    return await DemandeCongeService(db).update(id, data, user_id=current_user.id)


# --- Soldes de congé ---
@router.get("/soldes-conge", response_model=list[schemas.SoldeCongeResponse], tags=[TAG_SOLDES_CONGE])
async def list_soldes_conge(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    annee: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
):
    items, _ = await SoldeCongeService(db).get_all(
        entreprise_id=entreprise_id,
        employe_id=employe_id,
        annee=annee,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/soldes-conge/{id}", response_model=schemas.SoldeCongeResponse, tags=[TAG_SOLDES_CONGE])
async def get_solde_conge(db: DbSession, current_user: CurrentUser, id: int):
    return await SoldeCongeService(db).get_or_404(id)


@router.post("/soldes-conge", response_model=schemas.SoldeCongeResponse, status_code=201, tags=[TAG_SOLDES_CONGE])
async def create_solde_conge(db: DbSession, current_user: CurrentUser, data: schemas.SoldeCongeCreate):
    return await SoldeCongeService(db).create(data)


@router.patch("/soldes-conge/{id}", response_model=schemas.SoldeCongeResponse, tags=[TAG_SOLDES_CONGE])
async def update_solde_conge(db: DbSession, current_user: CurrentUser, id: int, data: schemas.SoldeCongeUpdate):
    return await SoldeCongeService(db).update(id, data)


# --- Objectifs ---
@router.get("/objectifs", response_model=list[schemas.ObjectifResponse], tags=[TAG_OBJECTIFS])
async def list_objectifs(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await ObjectifService(db).get_all(
        entreprise_id=entreprise_id, employe_id=employe_id, skip=skip, limit=limit
    )
    return items


@router.get("/objectifs/{id}", response_model=schemas.ObjectifResponse, tags=[TAG_OBJECTIFS])
async def get_objectif(db: DbSession, current_user: CurrentUser, id: int):
    return await ObjectifService(db).get_or_404(id)


@router.post("/objectifs", response_model=schemas.ObjectifResponse, status_code=201, tags=[TAG_OBJECTIFS])
async def create_objectif(db: DbSession, current_user: CurrentUser, data: schemas.ObjectifCreate):
    return await ObjectifService(db).create(data)


@router.patch("/objectifs/{id}", response_model=schemas.ObjectifResponse, tags=[TAG_OBJECTIFS])
async def update_objectif(db: DbSession, current_user: CurrentUser, id: int, data: schemas.ObjectifUpdate):
    return await ObjectifService(db).update(id, data)


# --- Taux de commission ---
@router.get("/taux-commissions", response_model=list[schemas.TauxCommissionResponse], tags=[TAG_TAUX_COMMISSION])
async def list_taux_commissions(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    actif_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    items, _ = await TauxCommissionService(db).get_all(
        entreprise_id=entreprise_id, actif_only=actif_only, skip=skip, limit=limit
    )
    return items


@router.get("/taux-commissions/{id}", response_model=schemas.TauxCommissionResponse, tags=[TAG_TAUX_COMMISSION])
async def get_taux_commission(db: DbSession, current_user: CurrentUser, id: int):
    return await TauxCommissionService(db).get_or_404(id)


@router.post("/taux-commissions", response_model=schemas.TauxCommissionResponse, status_code=201, tags=[TAG_TAUX_COMMISSION])
async def create_taux_commission(db: DbSession, current_user: CurrentUser, data: schemas.TauxCommissionCreate):
    return await TauxCommissionService(db).create(data)


@router.patch("/taux-commissions/{id}", response_model=schemas.TauxCommissionResponse, tags=[TAG_TAUX_COMMISSION])
async def update_taux_commission(db: DbSession, current_user: CurrentUser, id: int, data: schemas.TauxCommissionUpdate):
    return await TauxCommissionService(db).update(id, data)


# --- Commissions ---
@router.get("/commissions", response_model=list[schemas.CommissionResponse], tags=[TAG_COMMISSIONS])
async def list_commissions(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    payee: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await CommissionService(db).get_all(
        entreprise_id=entreprise_id,
        employe_id=employe_id,
        payee=payee,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/commissions/{id}", response_model=schemas.CommissionResponse, tags=[TAG_COMMISSIONS])
async def get_commission(db: DbSession, current_user: CurrentUser, id: int):
    return await CommissionService(db).get_or_404(id)


@router.post("/commissions", response_model=schemas.CommissionResponse, status_code=201, tags=[TAG_COMMISSIONS])
async def create_commission(db: DbSession, current_user: CurrentUser, data: schemas.CommissionCreate):
    return await CommissionService(db).create(data)


@router.patch("/commissions/{id}", response_model=schemas.CommissionResponse, tags=[TAG_COMMISSIONS])
async def update_commission(db: DbSession, current_user: CurrentUser, id: int, data: schemas.CommissionUpdate):
    return await CommissionService(db).update(id, data)


# --- Avances ---
@router.get("/avances", response_model=list[schemas.AvanceResponse], tags=[TAG_AVANCES])
async def list_avances(
    db: DbSession,
    current_user: CurrentUser,
    entreprise_id: int = Query(..., description="ID de l'entreprise"),
    employe_id: int | None = None,
    rembourse: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    items, _ = await AvanceService(db).get_all(
        entreprise_id=entreprise_id,
        employe_id=employe_id,
        rembourse=rembourse,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/avances/{id}", response_model=schemas.AvanceResponse, tags=[TAG_AVANCES])
async def get_avance(db: DbSession, current_user: CurrentUser, id: int):
    return await AvanceService(db).get_or_404(id)


@router.post("/avances", response_model=schemas.AvanceResponse, status_code=201, tags=[TAG_AVANCES])
async def create_avance(db: DbSession, current_user: CurrentUser, data: schemas.AvanceCreate):
    return await AvanceService(db).create(data, created_by_id=current_user.id)


@router.patch("/avances/{id}", response_model=schemas.AvanceResponse, tags=[TAG_AVANCES])
async def update_avance(db: DbSession, current_user: CurrentUser, id: int, data: schemas.AvanceUpdate):
    return await AvanceService(db).update(id, data)
