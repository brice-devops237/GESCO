# app/main.py
# -----------------------------------------------------------------------------
# Point d'entrée FastAPI (Clean Architecture : couche Présentation).
# Configure l'app, CORS, gestionnaires d'exceptions, lifespan et routeurs.
# -----------------------------------------------------------------------------

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.core.database import get_engine
from app.core.exceptions import AppHTTPException
from app.modules.auth.router import router as auth_router
from app.modules.catalogue.router import router as catalogue_router
from app.modules.parametrage.router import router as parametrage_router
from app.modules.partenaires.router import router as partenaires_router
from app.modules.commercial.router import router as commercial_router
from app.modules.achats.router import router as achats_router


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
    Au shutdown, fermeture du pool de connexions DB (évite fuites).
    """
    yield
    engine = get_engine()
    await engine.dispose()


def create_app() -> FastAPI:
    """Factory de l'application (testable, sans effets de bord à l'import)."""
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        description="API backend Gesco – Système de gestion commerciale Cameroun",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
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

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routeurs API v1 ---
    prefix = settings.API_V1_PREFIX
    app.include_router(auth_router, prefix=prefix)
    app.include_router(parametrage_router, prefix=prefix)
    app.include_router(catalogue_router, prefix=prefix)
    app.include_router(partenaires_router, prefix=prefix)
    app.include_router(commercial_router, prefix=prefix)
    app.include_router(achats_router, prefix=prefix)

    return app


app = create_app()


@app.get("/health")
async def health():
    """
    Santé de l'API (sans auth, sans DB). Pour load balancer et monitoring.
    """
    return {"status": "ok", "service": "gesco"}
