# app/core/security.py
# -----------------------------------------------------------------------------
# Sécurité : hash des mots de passe (bcrypt) et tokens JWT (création / décodage).
# Aucun import des modèles Utilisateur ou d'autres modules métier pour éviter
# les imports circulaires. Les infos utilisateur sont passées en paramètre.
# -----------------------------------------------------------------------------

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

# Contexte Passlib pour bcrypt (rounds injecté dans hash_password via config)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_secret_and_algorithm() -> tuple[str, str]:
    """Retourne SECRET_KEY et ALGORITHM depuis la config (évite de charger Settings au top-level)."""
    s = get_settings()
    return s.SECRET_KEY, s.ALGORITHM


def hash_password(plain_password: str) -> str:
    """
    Hash un mot de passe en clair avec bcrypt.
    À utiliser avant stockage en base (table utilisateurs.mot_de_passe_hash).
    Le coût bcrypt est lu depuis la config (BCRYPT_ROUNDS).
    """
    rounds = get_settings().BCRYPT_ROUNDS
    return _pwd_context.hash(plain_password, rounds=rounds)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond au hash stocké.
    Retourne True si conforme, False sinon.
    """
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Crée un token JWT d'accès.
    :param subject: Identifiant du sujet (souvent user_id ou login)
    :param expires_delta: Durée de validité (défaut = ACCESS_TOKEN_EXPIRE_MINUTES)
    :param extra_claims: Claims additionnels (ex: {"entreprise_id": 1, "role": "admin"})
    :return: Token JWT encodé (chaîne)
    """
    secret, algorithm = _get_secret_and_algorithm()
    s = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(UTC) + expires_delta
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Décode et valide un token JWT. Vérifie la signature et l'expiration.
    :return: Payload (dict) si valide, None si token invalide ou expiré.
    """
    secret, algorithm = _get_secret_and_algorithm()
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
