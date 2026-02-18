# app/core/rate_limit.py
# -----------------------------------------------------------------------------
# Middleware de limitation du débit (requêtes par minute par IP).
# Désactivé si requests_per_minute <= 0.
# -----------------------------------------------------------------------------

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def _get_client_ip(request: Request) -> str:
    """Retourne l'IP du client (X-Forwarded-For si derrière proxy, sinon client.host)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Limite le nombre de requêtes par minute par IP (sliding window).
    Si la limite est dépassée, renvoie 429 Too Many Requests.
    """

    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._store: defaultdict[str, list[float]] = defaultdict(list)
        self._window_seconds = 60.0

    def _clean_old(self, ip: str) -> None:
        now = time.monotonic()
        cutoff = now - self._window_seconds
        self._store[ip] = [t for t in self._store[ip] if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        if self.requests_per_minute <= 0:
            return await call_next(request)
        ip = _get_client_ip(request)
        self._clean_old(ip)
        if len(self._store[ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Trop de requêtes. Réessayez plus tard.",
                    "code": "RATE_LIMIT_EXCEEDED",
                },
            )
        self._store[ip].append(time.monotonic())
        return await call_next(request)

