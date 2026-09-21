"""First-party, rate-limited page-view tracking route."""

import time

from fastapi import APIRouter, Request
from loguru import logger
from pydantic import BaseModel, Field

from app.database import get_session

router = APIRouter()
_rate_limit: dict[str, tuple[float, int]] = {}
_WINDOW_SECONDS = 60
_MAX_REQUESTS = 30


class TrackRequest(BaseModel):
    """Validated first-party analytics payload."""

    path: str = Field(..., max_length=500)
    referrer: str = Field(default="", max_length=500)


@router.post("/api/analytics/track")
def track_pageview(request_data: TrackRequest, request: Request):
    """Store a page view unless the client exceeded the rate limit."""
    if _is_rate_limited(request):
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
    """Advance the bounded in-memory counter for one client address."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    last_time, count = _rate_limit.get(client_ip, (now, 0))
    if now - last_time >= _WINDOW_SECONDS:
        _rate_limit[client_ip] = (now, 1)
        return False
    if count >= _MAX_REQUESTS:
        return True
    _rate_limit[client_ip] = (last_time, count + 1)
    return False
