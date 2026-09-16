"""
Aplicação Principal — Portal Cerrado
API FastAPI REAL - consulta banco de dados.
"""

import logging
import secrets
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
import threading
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import get_session, init_db
from app.ml_editorial import get_latest_trend_signals
from app.schema import NewsArticle, Reporter
from app.publisher import ArticlePublisher
from fastapi.responses import JSONResponse
from app.contracts import iso_utc
from sqlalchemy import func

import sentry_sdk
from loguru import logger
import sys

# Configurar Loguru
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

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
        logger.info(f"[SCHEDULER] Agendador LOCAL ativo — intervalo {interval}s (CELERY_SCHEDULER=0, ENABLE_LOCAL_SCHEDULER=1)")
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
from fastapi import Header, Depends

def require_api_key(x_api_key: str = Header(None)):
    expected = os.getenv("PUBLISH_API_KEY") or os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Publicacao indisponivel: autenticacao nao configurada")
    if not isinstance(x_api_key, str) or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


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
    sort_by: str = Query("recent", pattern="^(recent|trend)$")
):
    """Lista as notícias publicadas (do banco REAL)."""
    publisher = ArticlePublisher()
    try:
        total = publisher.count_published_articles(category=category, reporter_slug=reporter_slug)
        articles = publisher.get_published_articles(limit=limit, offset=offset, category=category, reporter_slug=reporter_slug, sort_by=sort_by)
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "category": category,
            "reporter_slug": reporter_slug,
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
        article = db.query(NewsArticle).filter(
            NewsArticle.slug == slug,
            NewsArticle.status == "published"
        ).first()
        
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


@app.get("/api/sitemap")
def sitemap_articles(after_id: int = Query(0, ge=0), through_id: int = Query(None, ge=0), limit: int = Query(1000, ge=1, le=1000)):
    db = None
    try:
        db = get_session()
        upper = through_id if through_id is not None else (db.query(func.max(NewsArticle.id)).scalar() or 0)
        rows = db.query(NewsArticle.id, NewsArticle.slug, NewsArticle.updated_at, NewsArticle.published_at).filter(
            NewsArticle.status == "published", NewsArticle.visibility == "public",
            NewsArticle.id > after_id, NewsArticle.id <= upper, NewsArticle.slug.isnot(None),
        ).order_by(NewsArticle.id).limit(limit).all()
        return {"through_id": upper, "articles": [{"id": row.id, "slug": row.slug,
                "updated_at": iso_utc(row.updated_at), "published_at": iso_utc(row.published_at)} for row in rows]}
    except Exception:
        raise HTTPException(status_code=503, detail="Sitemap temporariamente indisponivel") from None
    finally:
        if db is not None:
            db.close()


@app.get("/api/reporters")
def list_reporters():
    """Lista os repórteres digitais."""
    db = None
    try:
        db = get_session()
        reporters = db.query(Reporter).filter(Reporter.active == True).all()
        
        result = [
            {
                "slug": r.slug,
                "name": r.display_name,
                "role": r.role,
                "articles_published": r.articles_published,
                "stage": r.personality_stage,
            }
            for r in reporters
        ]
        
        return {"reporters": result}
    except Exception as e:
        logger.error("Reporteres indisponiveis (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Reporteres temporariamente indisponiveis") from None
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


@app.post("/api/publish")
def publish_article_endpoint(article: dict, _auth=Depends(require_api_key), idempotency_key: str = Header(None)):
    """Publica uma matéria manualmente. Requer X-API-Key."""
    publisher = ArticlePublisher()
    try:
        result = publisher.publish_article(article, idempotency_key=idempotency_key)
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
        articles = db.query(NewsArticle).filter(
            NewsArticle.status.in_(["review", "classified", "draft"])
        ).order_by(NewsArticle.created_at.desc()).limit(50).all()
        
        return {"articles": [
            {
                "slug": a.slug,
                "title": a.title,
                "summary": a.summary,
                "original_text": a.original_text,
                "category": a.category,
                "importance_score": a.importance_score,
                "engagement_score": a.engagement_score,
                "status": a.status
            } for a in articles
        ]}
    except Exception as e:
        logger.error("Falha ao listar matérias para curadoria (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        if db is not None:
            db.close()


@app.put("/api/editorial/review/{slug}")
def update_article_review(slug: str, data: dict, _auth=Depends(require_api_key)):
    db = None
    try:
        db = get_session()
        article = db.query(NewsArticle).filter(NewsArticle.slug == slug).first()
        if not article:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")
            
        if "category" in data:
            article.category = data["category"]
        if "importance_score" in data:
            article.importance_score = data["importance_score"]
        if "engagement_score" in data:
            article.engagement_score = data["engagement_score"]
        if "status" in data:
            article.status = data["status"]
            if article.status == "published" and not article.published_at:
                article.published_at = datetime.now(timezone.utc)
                
        article.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success", "slug": slug}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Falha ao atualizar matéria (%s)", type(e).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        if db is not None:
            db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
