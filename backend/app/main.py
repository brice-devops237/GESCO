# app/main.py
# -----------------------------------------------------------------------------
# Point d'entrée FastAPI (Clean Architecture : couche Présentation).
# - Crée l'application via create_app(), enregistre les 15 routeurs sous /api/v1.
# - Gestion des erreurs (AppHTTPException, HTTPException, Exception), CORS, lifespan.
# - Rate limiting, logging, création du répertoire DB SQLite au démarrage.
# - Endpoints racine : GET / (infos API), GET /health (santé sans DB).
# - OpenAPI : tags, schéma JWT Bearer pour Authorize dans /docs.
# -----------------------------------------------------------------------------

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import get_engine
from app.core.exceptions import AppHTTPException
from app.core.logging_config import setup_logging
from app.core.rate_limit import RateLimitMiddleware
from app.modules.achats.router import router as achats_router
from app.modules.auth.router import router as auth_router
from app.modules.catalogue.router import router as catalogue_router
from app.modules.commercial.router import router as commercial_router
from app.modules.comptabilite.router import router as comptabilite_router
from app.modules.immobilisations.router import router as immobilisations_router
from app.modules.paie.router import router as paie_router
from app.modules.parametrage.router import router as parametrage_router
from app.modules.partenaires.router import router as partenaires_router
from app.modules.rapports.router import router as rapports_router
from app.modules.rh.router import router as rh_router
from app.modules.stock.router import router as stock_router
from app.modules.systeme.router import router as systeme_router
from app.modules.tresorerie.router import router as tresorerie_router


def _error_response(status_code: int, detail: Any, code: str | None = None) -> dict:
    """Réponse JSON standard pour les erreurs API."""
    body: dict = {"detail": detail}
    if code:
        body["code"] = code
    return body


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Cycle de vie : démarrage et arrêt propre.
    - Configuration du logging (LOG_LEVEL, LOG_FORMAT, LOG_FILE).
    - Création du répertoire app/db si SQLite.
    - Au shutdown, fermeture du pool de connexions DB (évite fuites).
    """
    settings = get_settings()
    setup_logging(
        level=settings.LOG_LEVEL,
        format_type=settings.LOG_FORMAT,
        log_file=settings.LOG_FILE or None,
    )
    if "sqlite" in settings.DATABASE_URL:
        # Créer le répertoire parent du fichier SQLite si nécessaire
        parts = settings.DATABASE_URL.split("///")
        if len(parts) >= 2:
            db_path = parts[-1].strip().lstrip("./")
            if db_path:
                parent = Path(db_path).parent
                if parent and str(parent) != ".":
                    parent.mkdir(parents=True, exist_ok=True)
    yield
    engine = get_engine()
    await engine.dispose()


# Tags OpenAPI segmentés par table/ressource (un tag par ressource pour /docs)
OPENAPI_TAGS = [
    {"name": "Authentification", "description": "Connexion par entreprise, login et mot de passe ; token JWT Bearer."},
    # Paramétrage
    {"name": "Paramétrage - Entreprises", "description": "Entreprises (sociétés). NIU, régime fiscal, devise principale."},
    {"name": "Paramétrage - Devises", "description": "Référentiel devises (XAF, EUR, USD)."},
    {"name": "Paramétrage - Taux de change", "description": "Taux de change entre devises par date."},
    {"name": "Paramétrage - Points de vente", "description": "Points de vente et dépôts par entreprise."},
    {"name": "Paramétrage - Rôles", "description": "Rôles (par entreprise ou système)."},
    {"name": "Paramétrage - Permissions", "description": "Permissions (module/action) et liaison aux rôles."},
    {"name": "Paramétrage - Utilisateurs", "description": "Utilisateurs (login, mot de passe hash, rôle)."},
    {"name": "Paramétrage - Affectations utilisateur-PDV", "description": "Liaison utilisateur ↔ point de vente."},
    # Catalogue
    {"name": "Catalogue - Unités de mesure", "description": "Unités (pièce, kg, L, etc.)."},
    {"name": "Catalogue - Taux TVA", "description": "Taux de TVA (0 %, 19,25 % CGI Cameroun)."},
    {"name": "Catalogue - Familles de produits", "description": "Familles et sous-familles de produits."},
    {"name": "Catalogue - Conditionnements", "description": "Conditionnements (caisse, carton, etc.)."},
    {"name": "Catalogue - Produits", "description": "Produits (code, libellé, prix, TVA, seuils)."},
    {"name": "Catalogue - Produits-Conditionnements", "description": "Liaison produit ↔ conditionnement."},
    {"name": "Catalogue - Canaux de vente", "description": "Canaux de vente par entreprise."},
    {"name": "Catalogue - Prix produits", "description": "Prix par canal/PDV et période."},
    {"name": "Catalogue - Variantes produit", "description": "Variantes d'un produit."},
    # Partenaires
    {"name": "Partenaires - Types de tiers", "description": "Types (client, fournisseur)."},
    {"name": "Partenaires - Tiers", "description": "Tiers clients et fournisseurs (NIU, canal, limite crédit)."},
    {"name": "Partenaires - Contacts", "description": "Contacts rattachés aux tiers."},
    # Commercial
    {"name": "Commercial - États document", "description": "États (brouillon, validé, annulé) par type de document."},
    {"name": "Commercial - Devis", "description": "Devis clients."},
    {"name": "Commercial - Commandes", "description": "Commandes clients."},
    {"name": "Commercial - Factures", "description": "Factures clients (facture, avoir, proforma, duplicata)."},
    {"name": "Commercial - Bons de livraison", "description": "Bons de livraison."},
    # Achats
    {"name": "Achats - Dépôts", "description": "Dépôts (entrepôts) par entreprise."},
    {"name": "Achats - Commandes fournisseurs", "description": "Commandes fournisseurs."},
    {"name": "Achats - Réceptions", "description": "Réceptions (livraisons fournisseur)."},
    {"name": "Achats - Factures fournisseurs", "description": "Factures fournisseurs et statut paiement."},
    # Stock
    {"name": "Stock - Stocks", "description": "Niveaux de stock par dépôt/produit/variante."},
    {"name": "Stock - Mouvements de stock", "description": "Entrées, sorties, transferts, inventaires."},
    {"name": "Stock - Alertes", "description": "Alertes de stock (seuils min/max)."},
    # Trésorerie
    {"name": "Trésorerie - Modes de paiement", "description": "Modes de paiement (espèces, virement, mobile money, etc.)."},
    {"name": "Trésorerie - Comptes trésorerie", "description": "Comptes caisse et bancaires."},
    {"name": "Trésorerie - Règlements", "description": "Règlements clients et fournisseurs."},
    # Comptabilité
    {"name": "Comptabilité - Comptes comptables", "description": "Plan comptable (OHADA/CEMAC)."},
    {"name": "Comptabilité - Journaux comptables", "description": "Journaux (Ventes, Achats, Banque, Caisse, OD)."},
    {"name": "Comptabilité - Périodes comptables", "description": "Périodes d'exercice (ouverture/clôture)."},
    {"name": "Comptabilité - Écritures comptables", "description": "Écritures et lignes (débit/crédit)."},
    # RH
    {"name": "RH - Départements", "description": "Départements ou services."},
    {"name": "RH - Postes", "description": "Postes (fonctions) par département."},
    {"name": "RH - Types de contrat", "description": "Types de contrat (CDI, CDD, etc.)."},
    {"name": "RH - Employés", "description": "Employés (CNPS, NIU, poste, salaire)."},
    {"name": "RH - Types de congé", "description": "Types de congé (annuel, maladie, etc.)."},
    {"name": "RH - Demandes de congé", "description": "Demandes de congé et approbation."},
    {"name": "RH - Soldes de congé", "description": "Soldes de congés par employé/type/année."},
    {"name": "RH - Objectifs", "description": "Objectifs (CA, quantités) par employé."},
    {"name": "RH - Taux de commission", "description": "Taux de commission par catégorie."},
    {"name": "RH - Commissions", "description": "Commissions versées ou à verser."},
    {"name": "RH - Avances", "description": "Avances sur salaire."},
    # Paie
    {"name": "Paie - Périodes de paie", "description": "Périodes de paie (mois/année)."},
    {"name": "Paie - Types d'éléments de paie", "description": "Types (salaire de base, CNPS, IR, etc.)."},
    {"name": "Paie - Bulletins de paie", "description": "Bulletins et lignes de paie."},
    # Immobilisations
    {"name": "Immobilisations - Catégories", "description": "Catégories d'immobilisations."},
    {"name": "Immobilisations - Immobilisations", "description": "Actifs immobilisés (véhicules, matériel)."},
    {"name": "Immobilisations - Lignes d'amortissement", "description": "Lignes d'amortissement (dotations)."},
    # Système
    {"name": "Système - Paramètres", "description": "Paramètres applicatifs par entreprise."},
    {"name": "Système - Journal d'audit", "description": "Traçabilité des actions (création, modification, connexion)."},
    {"name": "Système - Notifications", "description": "Notifications in-app par utilisateur."},
    {"name": "Système - Licences logicielles", "description": "Licences logicielles par entreprise."},
    # Rapports
    {"name": "Rapports - Chiffre d'affaires", "description": "Chiffre d'affaires sur une période."},
    {"name": "Rapports - Tableau de bord", "description": "Synthèse (CA, factures, commandes, employés actifs)."},
]


def create_app() -> FastAPI:
    """Factory de l'application (testable, sans effets de bord à l'import)."""
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        description="API backend Gesco – Système de gestion intégré multi-entreprises pour le Cameroun et la zone CEMAC. Couvre paramétrage, catalogue, partenaires, ventes, achats, stock, trésorerie, comptabilité, RH, paie, immobilisations et rapports.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=OPENAPI_TAGS,
    )

    # --- Gestionnaires d'exceptions (réponse JSON cohérente) ---
    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        _request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(exc.status_code, exc.detail, getattr(exc, "code", None)),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(exc.status_code, exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Erreur serveur non gérée : réponse 500 cohérente (évite d'exposer les détails)."""
        return JSONResponse(
            status_code=500,
            content=_error_response(500, "Erreur interne du serveur", code="INTERNAL_ERROR"),
        )

    # --- CORS (ajouté en premier = couche externe) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Rate limiting (dernière couche avant les routes = exécuté en premier à la réception) ---
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    )

    # --- Routeurs API v1 (ordre = priorité métier, cf. docs/MODULES_PRIORITES.md) ---
    # P0: auth, parametrage | P1: catalogue, partenaires | P2: commercial, achats, stock
    # P3: tresorerie, comptabilite | P4: rh, paie | P5: systeme, rapports, immobilisations
    prefix = settings.API_V1_PREFIX
    app.include_router(auth_router, prefix=prefix)
    app.include_router(parametrage_router, prefix=prefix)
    app.include_router(catalogue_router, prefix=prefix)
    app.include_router(partenaires_router, prefix=prefix)
    app.include_router(commercial_router, prefix=prefix)
    app.include_router(achats_router, prefix=prefix)
    app.include_router(stock_router, prefix=prefix)
    app.include_router(tresorerie_router, prefix=prefix)
    app.include_router(comptabilite_router, prefix=prefix)
    app.include_router(rh_router, prefix=prefix)
    app.include_router(paie_router, prefix=prefix)
    app.include_router(systeme_router, prefix=prefix)
    app.include_router(rapports_router, prefix=prefix)
    app.include_router(immobilisations_router, prefix=prefix)

    # --- OpenAPI : schéma JWT Bearer pour "Authorize" dans /docs ---
    def custom_openapi():
        if app.openapi_schema is not None:
            return app.openapi_schema
        from fastapi.openapi.utils import get_openapi
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Token obtenu via POST /api/v1/auth/login (entreprise_id, login, password).",
            },
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    return app


app = create_app()


@app.get(
    "/",
    summary="Racine API",
    description="Informations et liens utiles (documentation, santé). Sans authentification.",
    response_description="Nom, version et liens de l'API.",
)
async def root():
    """Point d'entrée racine : infos API et liens vers docs / health."""
    settings = get_settings()
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "description": "API backend Gesco – Gestion intégrée multi-entreprises (Cameroun, CEMAC).",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": settings.API_V1_PREFIX,
    }


@app.get(
    "/health",
    summary="Santé de l'API",
    description="Endpoint de health check sans authentification ni accès base. Utilisable par les load balancers et outils de monitoring.",
    response_description="Statut OK et nom du service.",
)
async def health():
    """Santé de l'API (sans auth, sans DB). Pour load balancer et monitoring."""
    return {"status": "ok", "service": "gesco"}

