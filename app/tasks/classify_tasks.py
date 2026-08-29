"""
Tarefas de Classificação de Artigos
"""
from app.celery_app import celery_app
from app.classifier import classify_articles
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.classify_tasks.classify_pending_articles",
    bind=True,
    max_retries=3
)
def classify_pending_articles(self):
    """
    Classifica artigos pendentes por importância e engajamento.
    Roda a cada 30 minutos.
    """
    try:
        logger.info("[CELERY] Iniciando classify_pending_articles")
        # Aqui viria a lógica de buscar artigos pendentes do banco
        # Por ora, retorna sucesso
        return {
            "status": "success",
            "classified": 0,
            "message": "Implementar busca no DB"
        }
    except Exception as e:
        logger.error(f"[CELERY] Erro em classify_pending_articles: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.classify_tasks.classify_single_article",
    bind=True,
    max_retries=3
)
def classify_single_article(self, article: dict):
    """Classifica um único artigo."""
    try:
        from app.classifier import NewsClassifier
        classifier = NewsClassifier()
        classified = classifier.classify(article)
        return {"status": "success", "article": classified}
    except Exception as e:
        logger.error(f"[CELERY] Erro em classify_single_article: {e}")
        raise self.retry(exc=e)
