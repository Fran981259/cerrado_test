"""
Aplicação Principal — Portal Cerrado
API FastAPI REAL - consulta banco de dados.
"""

import logging
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
import threading
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import get_session, init_db
from app.schema import NewsArticle, Reporter
from app.publisher import ArticlePublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria tabelas se não existirem
init_db()

app = FastAPI(
    title="Portal Cerrado",
    description="Sistema automatizado de notícias com repórteres digitais",
    version="1.0.0"
)


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


@app.on_event("startup")
def _start_scheduler():
    """Inicia o agendador local se habilitado (padrão: sim, quando Celery não está no comando)."""
    enabled = os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1"
    celery_active = os.getenv("CELERY_SCHEDULER", "0") == "1"
    # Desliga o local scheduler quando o beat do Celery assume
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


# --- Auth dependency for write endpoints ---
from fastapi import Header, Depends

def require_api_key(x_api_key: str = Header(None)):
    expected = os.getenv("PUBLISH_API_KEY") or os.getenv("API_KEY")
    # If no key configured, deny in production, allow in dev with warning
    if not expected:
        if os.getenv("ENVIRONMENT", "development") == "production":
            logger.error("[AUTH] PUBLISH_API_KEY not set in production — denying write")
            raise HTTPException(status_code=503, detail="Server misconfigured: publish auth not set")
        logger.warning("[AUTH] PUBLISH_API_KEY not set — allowing write in dev (set it in production!)")
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


# CORS — explicit origins, not wildcard+credentials (invalid per spec)
def _cors_origins():
    raw = os.getenv("CORS_ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS") or ""
    if raw.strip():
        return [o.strip() for o in raw.split(",") if o.strip()]
    # default: prod domain + Tailscale/dev
    site = os.getenv("SITE_URL", "https://portalcerrado.com.br")
    frontend = os.getenv("NEXT_PUBLIC_SITE_URL", site)
    return [
        site.rstrip("/"),
        frontend.rstrip("/"),
        "https://portalcerrado.com.br",
        "http://localhost:3000",
        "http://100.95.111.24:3000",
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
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
def health_check():
    """Verifica saúde do sistema."""
    try:
        db = get_session()
        count = db.query(NewsArticle).count()
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "articles_count": count,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@app.get("/api/news")
def list_news(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str = Query(None)
):
    """Lista as notícias publicadas (do banco REAL)."""
    try:
        publisher = ArticlePublisher()
        articles = publisher.get_published_articles(limit=limit, category=category)
        publisher.close()
        
        return {
            "total": len(articles),
            "limit": limit,
            "offset": offset,
            "category": category,
            "news": articles,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/{slug}")
def get_article(slug: str):
    """Busca uma matéria por slug."""
    try:
        db = get_session()
        article = db.query(NewsArticle).filter(
            NewsArticle.slug == slug,
            NewsArticle.status == "published"
        ).first()
        
        if not article:
            db.close()
            raise HTTPException(status_code=404, detail="Matéria não encontrada")
        
        result = {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "content": article.content,
            "category": article.category,
            "reporter": article.reporter.display_name if article.reporter else None,
            "author": article.author,
            "image_url": article.image_url,
            "sources": article.sources,
            "tags": article.tags,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "is_curiosity": article.is_curiosity,
        }
        
        db.close()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reporters")
def list_reporters():
    """Lista os repórteres digitais."""
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
        
        db.close()
        return {"reporters": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/publish")
def publish_article_endpoint(article: dict, _auth=Depends(require_api_key)):
    """Publica uma matéria manualmente. Requer X-API-Key."""
    try:
        publisher = ArticlePublisher()
        result = publisher.publish_article(article)
        publisher.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
