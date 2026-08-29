"""
Aplicação Principal — Atualiza Brasil
API FastAPI REAL - consulta banco de dados.
"""

import logging
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
    title="Atualiza Brasil",
    description="Sistema automatizado de notícias com repórteres digitais",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "portal": "Atualiza Brasil",
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
def publish_article_endpoint(article: dict):
    """Publica uma matéria manualmente."""
    try:
        publisher = ArticlePublisher()
        result = publisher.publish_article(article)
        publisher.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
