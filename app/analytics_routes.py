"""First-party, rate-limited page-view tracking route."""

import ipaddress
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

from app.database import get_db
from app.rate_limit import is_rate_limited

router = APIRouter()
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 30


class TrackRequest(BaseModel):
    """Validated first-party analytics payload."""

    path: str = Field(..., max_length=500)
    referrer: str = Field(default="", max_length=500)


@router.post("/api/analytics/track")
def track_pageview(request_data: TrackRequest, request: Request, db=Depends(get_db)):
    """Store a page view unless the client exceeded the rate limit."""
    try:
        limited = _is_rate_limited(request)
    except RuntimeError:
        return JSONResponse(status_code=503, content={"status": "rate_limit_unavailable"})
    if limited:
        return {"status": "rate_limited"}
    try:
        from app.schema import PageView

        db.add(PageView(path=request_data.path, referrer=request_data.referrer.split("?")[0]))
        db.commit()
        return {"status": "ok"}
    except Exception as error:
        logger.error("Erro no tracking de analytics (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Analytics temporariamente indisponível") from None


def _is_rate_limited(request: Request) -> bool:
    """Apply a shared counter keyed by client address."""
    client_ip = _client_ip(request)
    return is_rate_limited(f"portal:analytics:{client_ip}", _MAX_REQUESTS, _WINDOW_SECONDS)


def _trusted_proxy_hosts() -> set[str]:
    """Load the explicit proxy allowlist used for forwarded client addresses."""
    raw = os.getenv("TRUSTED_PROXY_HOSTS", "127.0.0.1,::1")
    return {value.strip() for value in raw.split(",") if value.strip()}


def _client_ip(request: Request) -> str:
    """Use X-Forwarded-For only when the immediate sender is trusted."""
    immediate = request.client.host if request.client else "unknown"
    if immediate not in _trusted_proxy_hosts() and "*" not in _trusted_proxy_hosts():
        return immediate
    forwarded = request.headers.get("x-forwarded-for", "")
    for candidate in forwarded.split(","):
        value = candidate.strip()
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            continue
    return immediate
