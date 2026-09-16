"""
Tarefas de Curiosidades
"""
from app.celery_app import celery_app
from app.curiosities import generate_all_daily_curiosities
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.curiosity_tasks.generate_daily_curiosities",
    bind=True,
    max_retries=3
)
def generate_daily_curiosities(self):
    """
    Gera curiosidades para todas as categorias.
    Roda 1x ao dia às 06:00.
    """
    try:
        logger.info("[CELERY] Iniciando generate_daily_curiosities")
        curiosities = generate_all_daily_curiosities()
        from app.tasks.scan_tasks import _persist_articles
        import hashlib
        for article in curiosities:
            digest = hashlib.sha256(article["summary"].encode()).hexdigest()
            article["identity_key"] = "curiosity:" + digest
            article["needs_review"] = True
        persisted = _persist_articles(curiosities, fetch_details=False)
        logger.info(f"[CELERY] {len(curiosities)} curiosidades geradas")
        return {
            "status": "success",
            "count": len(curiosities),
            "curiosities": curiosities,
            "persisted": persisted,
        }
    except Exception as e:
        logger.error(f"[CELERY] Erro em generate_daily_curiosities: {e}")
        raise self.retry(exc=e)
