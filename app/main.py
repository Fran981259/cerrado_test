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
from datetime import datetime, timezone
from typing import Literal, Optional

import sentry_sdk
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.analytics_routes import router as analytics_router
from app.database import get_session, init_db
from app.editorial_routes import router as editorial_router
from app.ml_editorial import get_latest_trend_signals
from app.operations_routes import router as operations_router
from app.publisher import ArticlePublisher
from app.schema import NewsArticle

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
    if not raw.strip():
        if os.getenv("ENVIRONMENT", "development").lower() == "production":
            raise RuntimeError("CORS_ALLOWED_ORIGINS obrigatório em produção")
        return ["http://100.95.111.24:3000", "http://localhost:3000", "http://localhost:8000"]
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if "*" in origins:
        raise RuntimeError("CORS_ALLOWED_ORIGINS não pode usar wildcard com credenciais")
    return list(dict.fromkeys(origins))


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
