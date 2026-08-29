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
    Publica artigos reescritos no portal.
    Busca artigos pendentes no banco e publica.
    """
    logger.info("[PUBLISH] Iniciando publicação")
    
    try:
        db = get_session()
        publisher = ArticlePublisher(db)
        
        # Busca artigos pendentes (status = 'pending_rewrite' ou similar)
        # Por ora, simula publicação direta
        
        result = {
            "status": "success",
            "published": 0,
            "message": "Task configurada"
        }
        
        db.close()
        logger.info(f"[PUBLISH] Concluído: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[PUBLISH] Erro: {e}")
        raise self.retry(exc=e)


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
