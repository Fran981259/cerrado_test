"""First-party, rate-limited page-view tracking route."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

from app.database import get_session
from app.rate_limit import is_rate_limited

router = APIRouter()
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 30


class TrackRequest(BaseModel):
    """Validated first-party analytics payload."""

    path: str = Field(..., max_length=500)
    referrer: str = Field(default="", max_length=500)


@router.post("/api/analytics/track")
def track_pageview(request_data: TrackRequest, request: Request):
    """Store a page view unless the client exceeded the rate limit."""
    try:
        limited = _is_rate_limited(request)
    except RuntimeError:
        return JSONResponse(status_code=503, content={"status": "rate_limit_unavailable"})
    if limited:
        return {"status": "rate_limited"}
    db = get_session()
    try:
        from app.schema import PageView

        db.add(PageView(path=request_data.path, referrer=request_data.referrer.split("?")[0]))
        db.commit()
        return {"status": "ok"}
    except Exception as error:
        logger.error("Erro no tracking de analytics (%s)", type(error).__name__)
        return {"status": "error"}
    finally:
        db.close()


def _is_rate_limited(request: Request) -> bool:
    """Apply a shared counter keyed by client address."""
    client_ip = request.client.host if request.client else "unknown"
    return is_rate_limited(f"portal:analytics:{client_ip}", _MAX_REQUESTS, _WINDOW_SECONDS)
