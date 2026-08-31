"""
Tarefas de Publicação — Atualiza Brasil
VERSÃO REAL - Publica artigos no banco de dados.
"""

from app.celery_app import celery_app
from app.publisher import ArticlePublisher
from app.database import get_session
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.publish_tasks.publish_ready_articles",
    bind=True,
    max_retries=3,
    time_limit=300
)
def publish_ready_articles(self):
    """
    Publica artigos reescritos (status 'rewritten') no portal,
    definindo status='published' e published_at.
    Roda a cada 30 minutos.
    """
    logger.info("[PUBLISH] Iniciando publicação de artigos reescritos")

    from app.database import get_session
    from app.schema import NewsArticle
    from datetime import datetime

    db = get_session()
    published = 0
    failed = 0
    try:
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.status == "rewritten")
            .order_by(NewsArticle.updated_at.asc())
            .limit(100)
            .all()
        )
        for art in articles:
            try:
                if not art.content or not art.slug:
                    # gera slug se necessário para publicação
                    if not art.slug:
                        publisher = ArticlePublisher(db)
                        art.slug = publisher._generate_slug(art.title)
                art.status = "published"
                art.published_at = datetime.utcnow()
                art.visibility = "public"
                art.updated_at = datetime.utcnow()
                published += 1
            except Exception as e:
                logger.error(f"[PUBLISH] erro num artigo: {e}")
                failed += 1
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[PUBLISH] erro no lote: {e}")
        raise
    finally:
        db.close()

    logger.info(f"[PUBLISH] Publicados: {published}, falhas: {failed}")
    return {"status": "success", "published": published, "failed": failed}


@celery_app.task(
    name="app.tasks.publish_tasks.publish_single_article",
    bind=True,
    max_retries=3,
    time_limit=60
)
def publish_single_article(self, article: dict):
    """Publica um único artigo no banco."""
    logger.info(f"[PUBLISH] Publicando: {article.get('title', '')[:50]}...")
    
    try:
        publisher = ArticlePublisher()
        result = publisher.publish_article(article)
        publisher.close()
        
        logger.info(f"[PUBLISH] Sucesso: {result['article_id']}")
        return result
        
    except Exception as e:
        logger.error(f"[PUBLISH] Erro: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.publish_tasks.publish_batch",
    bind=True,
    max_retries=3,
    time_limit=600
)
def publish_batch(self, articles: list):
    """Publica múltiplos artigos em lote."""
    logger.info(f"[PUBLISH] Batch de {len(articles)} artigos")
    
    try:
        publisher = ArticlePublisher()
        results = publisher.publish_batch(articles)
        publisher.close()
        
        published = sum(1 for r in results if r.get('success'))
        failed = len(results) - published
        
        logger.info(f"[PUBLISH] Batch completo: {published} sucesso, {failed} falha")
        
        return {
            "status": "success",
            "total": len(articles),
            "published": published,
            "failed": failed,
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"[PUBLISH] Erro no batch: {e}")
        raise self.retry(exc=e)
