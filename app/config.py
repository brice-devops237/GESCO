# app/config.py
# -----------------------------------------------------------------------------
# Configuration centralisée de l'application Gesco.
# Charge les variables depuis l'environnement (.env) via pydantic-settings.
# Aucun import depuis les modules métier pour éviter les imports circulaires.
# -----------------------------------------------------------------------------

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Objet de configuration unique. Les attributs sont lus depuis les variables
    d'environnement (ou .env). Les noms de variables sont en MAJUSCULES.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignorer les variables d'environnement non déclarées
    )

    # --- Application ---
    APP_NAME: str = Field(default="Gesco", description="Nom de l'application")
    APP_ENV: str = Field(default="development", description="Environnement (development|staging|production)")
    DEBUG: bool = Field(default=True, description="Mode debug (logs détaillés, traces)")
    HOST: str = Field(default="0.0.0.0", description="Adresse d'écoute du serveur")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Port du serveur")
    API_V1_PREFIX: str = Field(default="/api/v1", description="Préfixe des routes API v1")
    TIMEZONE: str = Field(default="Africa/Douala", description="Fuseau horaire (Cameroun)")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="URL du frontend (CORS, redirections)")

    # --- Base de données ---
    # Par défaut : SQLite portable (app/db/gesco.db). Sinon : PostgreSQL via .env
    # SQLite async : sqlite+aiosqlite:///./app/db/gesco.db
    # SQLite sync (Alembic) : sqlite:///./app/db/gesco.db
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./app/db/gesco.db",
        description="URL de connexion asynchrone (asyncpg ou aiosqlite pour SQLite)",
    )
    DATABASE_URL_SYNC: str = Field(
        default="sqlite:///./app/db/gesco.db",
        description="URL de connexion synchrone (Alembic, scripts : psycopg2 ou sqlite)",
    )
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1, le=50, description="Taille du pool de connexions")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0, description="Connexions supplémentaires autorisées")
    DATABASE_ECHO: bool = Field(default=False, description="Logger les requêtes SQL (debug)")

    # --- Sécurité & JWT ---
    SECRET_KEY: str = Field(..., min_length=32, description="Clé secrète pour signature JWT (min 32 caractères)")
    ALGORITHM: str = Field(default="HS256", description="Algorithme de signature JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=1, description="Durée de validité du token d'accès (minutes)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, description="Durée de validité du token de rafraîchissement (jours)")
    BCRYPT_ROUNDS: int = Field(default=12, ge=4, le=18, description="Coût bcrypt (hash mot de passe)")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, ge=0, description="Requêtes max par minute par IP (0 = désactivé)")

    # --- CORS ---
    CORS_ORIGINS: str = Field(
        default="*",
        description="Origines autorisées, séparées par des virgules (ex: http://localhost:3000)",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Autoriser l'envoi des cookies/auth")

    # --- API (pagination) ---
    DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=500, description="Nombre d'éléments par page par défaut")
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=500, description="Nombre max d'éléments par page")

    # --- Locale & devise (Cameroun) ---
    DEFAULT_LOCALE: str = Field(default="fr_FR", description="Locale par défaut")
    DEFAULT_CURRENCY_CODE: str = Field(default="XAF", description="Code devise par défaut (FCFA)")
    DATE_FORMAT: str = Field(default="%d/%m/%Y", description="Format d'affichage des dates")
    DATETIME_FORMAT: str = Field(default="%d/%m/%Y %H:%M", description="Format d'affichage date+heure")

    # --- Fichiers ---
    MEDIA_ROOT: str = Field(default="./media", description="Répertoire des uploads et pièces jointes")
    MAX_UPLOAD_SIZE: int = Field(default=10_485_760, ge=0, description="Taille max d'un fichier uploadé (octets, 10 Mo)")

    # --- Cache & session ---
    REDIS_URL: Optional[str] = Field(default=None, description="URL Redis (vide = cache mémoire)")
    CACHE_SESSION_TTL_MINUTES: int = Field(default=1440, ge=1, description="TTL du cache de travail (minutes)")
    ENABLE_SESSION_RECOVERY: bool = Field(default=True, description="Activer la reprise de session")

    # --- Logging ---
    LOG_LEVEL: str = Field(default="INFO", description="Niveau de log (DEBUG|INFO|WARNING|ERROR)")
    LOG_FORMAT: str = Field(default="json", description="Format des logs (json|text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Fichier de log (vide = console uniquement)")

    def cors_origins_list(self) -> list[str]:
        """
        Retourne la liste des origines CORS (chaque valeur est une origine autorisée).
        Si CORS_ORIGINS vaut '*', retourne ['*'] pour autoriser toutes les origines.
        """
        if not self.CORS_ORIGINS or self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Retourne l'instance unique de Settings (mise en cache).
    À utiliser comme dépendance FastAPI : Depends(get_settings).
    """
    return Settings()
