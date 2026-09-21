"""
Aplicação Principal — Portal Cerrado
API FastAPI REAL - consulta banco de dados.
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass
import sys
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import List, Literal, Optional

import sentry_sdk
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_
from app.analytics_routes import router as analytics_router
from app.contracts import CATEGORIES, category_name, iso_utc

from app.database import get_session, init_db
from app.editorial_routes import list_articles_for_review, router as editorial_router
from app.editorial import review_natural_writing
from app.ml_editorial import get_latest_trend_signals
from app.operations_routes import router as operations_router
from app.publisher import ArticlePublisher
from app.schema import NewsArticle, Reporter
from app.security import require_api_key

# Configurar Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )
    logger.info("Sentry configurado e ativo.")


def _run_pipeline_once() -> None:
    """Executa o pipeline completo uma vez (scan -> classify -> rewrite -> publish -> export)."""
    try:
        from app.tasks.scan_tasks import run_full_pipeline

        run_full_pipeline()
    except Exception as e:
        logger.error(f"[SCHEDULER] erro no pipeline: {e}")


def _local_scheduler(interval_seconds: int = 1800) -> None:
    """Agendador local que roda o pipeline a cada intervalo (sem depender de Redis/Celery)."""
    logger.info(f"[SCHEDULER] Iniciado — pipeline a cada {interval_seconds}s")
    while True:
        try:
            _run_pipeline_once()
        except Exception as e:
            logger.error(f"[SCHEDULER] erro: {e}")
        time.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa banco e scheduler local durante o ciclo de vida da aplicação."""
    init_db()
    enabled = os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1"
    celery_active = os.getenv("CELERY_SCHEDULER", "0") == "1"
    if celery_active:
        enabled = False
    if enabled:
        interval = int(os.getenv("LOCAL_SCHEDULER_INTERVAL", "1800"))
        t = threading.Thread(target=_local_scheduler, args=(interval,), daemon=True)
        t.start()
        logger.info(
            f"[SCHEDULER] Agendador LOCAL ativo — intervalo {interval}s (CELERY_SCHEDULER=0, ENABLE_LOCAL_SCHEDULER=1)"
        )
    else:
        reason = "CELERY_SCHEDULER=1 (Beat assume)" if celery_active else "ENABLE_LOCAL_SCHEDULER=0"
        logger.info(f"[SCHEDULER] Agendador LOCAL desativado ({reason}) — pipeline via Celery Beat")
    yield


app = FastAPI(
    title="Portal Cerrado",
    description="Sistema automatizado de notícias com repórteres digitais",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Auth dependency for write endpoints ---


# CORS — explicit origins, not wildcard+credentials (invalid per spec)
def _cors_origins():
    raw = os.getenv("CORS_ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS") or ""
    if raw.strip():
        return [o.strip() for o in raw.split(",") if o.strip()]
    # default: prod domain + Tailscale/dev
    site = os.getenv("SITE_URL", "http://100.95.111.24:3000")
    frontend = os.getenv("NEXT_PUBLIC_SITE_URL", site)
    return [
        site.rstrip("/"),
        frontend.rstrip("/"),
        "http://100.95.111.24:3000",
        "http://localhost:3000",
        "http://localhost:8000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(operations_router)
app.include_router(editorial_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {
        "portal": "Portal Cerrado",
        "version": "1.0.0",
        "status": "operacional",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
def health_check():
    """Verifica saúde do sistema."""
    db = None
    try:
        db = get_session()
        count = db.query(NewsArticle).count()
        return {
            "status": "healthy",
            "database": "connected",
            "articles_count": count,
        }
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "database": "unavailable"})
    finally:
        if db is not None:
            db.close()


@app.get("/live")
def liveness():
    return {"status": "alive"}


@app.get("/api/news")
def list_news(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str = Query(None),
    reporter_slug: str = Query(None),
    region: Optional[Literal["ms"]] = Query(None),
    sort_by: str = Query("recent", pattern="^(recent|trend)$"),
):
    """Lista as notícias publicadas (do banco REAL)."""
    publisher = ArticlePublisher()
    try:
        # Direct Python callers (including internal tests) receive FastAPI's
        # Query sentinel as the default; only a resolved string is a filter.
        resolved_region = region if isinstance(region, str) else None
        query_filters = {"category": category, "reporter_slug": reporter_slug}
        if resolved_region:
            query_filters["region"] = resolved_region
        total = publisher.count_published_articles(**query_filters)
        articles = publisher.get_published_articles(limit=limit, offset=offset, sort_by=sort_by, **query_filters)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "category": category,
            "reporter_slug": reporter_slug,
            "region": resolved_region,
            "sort_by": sort_by,
            "news": articles,
        }
    except Exception as e:
        logger.error("Listagem indisponivel (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Noticias temporariamente indisponiveis") from None
    finally:
        publisher.close()


@app.get("/api/news/{slug}")
def get_article(slug: str):
    """Busca uma matéria por slug."""
    db = None
    try:
        db = get_session()
        article = (
            db.query(NewsArticle)
            .filter(NewsArticle.slug == slug, NewsArticle.status == "published", NewsArticle.region == "ms")
            .first()
        )

        if not article:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")

        return ArticlePublisher(db)._article_to_dict(article)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Materia indisponivel (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Materia temporariamente indisponivel") from None
    finally:
        if db is not None:
            db.close()


@app.get("/api/trends")
def list_trends(limit: int = Query(8, ge=1, le=20)):
    """Retorna os temas mais quentes detectados pelo ML editorial."""
    try:
        trends = get_latest_trend_signals(limit=limit)
        return {"trends": trends, "total": len(trends)}
    except Exception as e:
        logger.error("Tendencias indisponiveis (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Tendencias temporariamente indisponiveis") from None


class PublishArticleRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    reporter_slug: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    summary: Optional[str] = Field(default=None, max_length=2_000)
    sources: Optional[List[dict[str, str]]] = Field(default=None, max_length=20)
    original_text: Optional[str] = None
    body: Optional[str] = None
    hash: Optional[str] = Field(default=None, max_length=64)
    tags: Optional[List[str]] = Field(default=None, max_length=30)
    image_url: Optional[str] = Field(default=None, max_length=500)
    region: Optional[Literal["ms"]] = None
    importance_score: Optional[float] = None
    engagement_score: Optional[float] = None
    priority_tier: Optional[Literal["TIER_1", "TIER_2", "TIER_3", "REJECT"]] = None


@app.post("/api/publish")
def publish_article_endpoint(
    article: PublishArticleRequest, _auth=Depends(require_api_key), idempotency_key: str = Header(None)
):
    """Publica uma matéria manualmente. Requer X-API-Key."""
    publisher = ArticlePublisher()
    try:
        result = publisher.publish_article(article.model_dump(exclude_unset=True), idempotency_key=idempotency_key)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from None
    except Exception as e:
        logger.error("Publicacao indisponivel (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Publicacao temporariamente indisponivel") from None
    finally:
        publisher.close()


@app.get("/api/editorial/review")
def list_articles_for_review(_auth=Depends(require_api_key)):
    db = None
    try:
        db = get_session()
        articles = (
            db.query(NewsArticle)
            .filter(
                or_(
                    NewsArticle.status.in_(["review", "classified", "draft"]),
                    and_(
                        NewsArticle.status == "published",
                        NewsArticle.visibility == "public",
                        NewsArticle.region == "ms",
                    ),
                )
            )
            .order_by(NewsArticle.created_at.desc())
            .limit(2000)
            .all()
        )

        return {
            "articles": [
                {
                    "slug": a.slug,
                    "title": a.title,
                    "summary": a.summary,
                    "content": a.content,
                    "original_text": a.original_text,
                    "writing_review": [finding.as_dict() for finding in review_natural_writing(a.content or "")],
                    "category": a.category,
                    "importance_score": a.importance_score,
                    "engagement_score": a.engagement_score,
                    "status": a.status,
                    "published_at": iso_utc(a.published_at),
                    "created_at": iso_utc(a.created_at),
                }
                for a in articles
            ]
        }
    except Exception as e:
        logger.error("Falha ao listar matérias para curadoria (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        if db is not None:
            db.close()


class UpdateReviewRequest(BaseModel):
    content: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    importance_score: Optional[int] = Field(default=None, ge=0, le=100)
    engagement_score: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[Literal["draft", "classified", "review", "rewritten", "failed", "published"]] = None


@app.put("/api/editorial/review/{slug}")
def update_article_review(slug: str, data: UpdateReviewRequest, _auth=Depends(require_api_key)):
    db = None
    try:
        db = get_session()
        article = db.query(NewsArticle).filter(NewsArticle.slug == slug).with_for_update().first()
        if not article:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        is_publishing = False
        if "category" in update_data:
            category = category_name(update_data["category"])
            if category not in CATEGORIES:
                raise HTTPException(status_code=422, detail="Categoria invalida")
            article.category = category
        if "content" in update_data:
            article.content = update_data["content"]
        if "importance_score" in update_data:
            article.importance_score = update_data["importance_score"]
        if "engagement_score" in update_data:
            article.engagement_score = update_data["engagement_score"]
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == "published" and article.status != "published":
                is_publishing = True
            else:
                article.status = new_status

        if is_publishing:
            publisher = ArticlePublisher(db)
            publisher.publish_existing(article)

        article.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success", "slug": slug}
    except HTTPException:
        raise
    except Exception as e:
        if db is not None:
            db.rollback()
        logger.error("Falha ao atualizar matéria (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        if db is not None:
            db.close()


class TrackRequest(BaseModel):
    path: str = Field(..., max_length=500)
    referrer: str = Field(default="", max_length=500)


# In-memory rate limiting dict (for simplicity, using global dict)
_analytics_rate_limit: dict[str, tuple[float, int]] = {}


@app.post("/api/analytics/track")
def track_pageview(req: TrackRequest, request: Request):
    """Grava o acesso da página (First-party analytics)."""
    # Rate Limiting simple
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    if client_ip in _analytics_rate_limit:
        last_req_time, count = _analytics_rate_limit[client_ip]
        if now - last_req_time < 60:
            if count >= 30:  # max 30 requests per minute
                return {"status": "rate_limited"}
            _analytics_rate_limit[client_ip] = (last_req_time, count + 1)
        else:
            _analytics_rate_limit[client_ip] = (now, 1)
    else:
        _analytics_rate_limit[client_ip] = (now, 1)

    db = None
    try:
        db = get_session()
        from app.schema import PageView

        # Clean referrer, remove query params if any
        ref = req.referrer.split("?")[0][:500] if req.referrer else ""
        path = req.path[:500]

        pv = PageView(path=path, referrer=ref)
        db.add(pv)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        logger.error("Erro no tracking de analytics (%s)", type(e).__name__)
        # Não levanta erro 500 pra não quebrar requisições do front, falha silenciosamente
        return {"status": "error"}
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
