"""
Tarefas de Curiosidades
"""
from app.celery_app import celery_app
from app.curiosities import generate_all_daily_curiosities, mix_with_articles
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
        logger.info(f"[CELERY] {len(curiosities)} curiosidades geradas")
        return {
            "status": "success",
            "count": len(curiosities),
            "curiosities": curiosities
        }
    except Exception as e:
        logger.error(f"[CELERY] Erro em generate_daily_curiosities: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.curiosity_tasks.inject_curiosities_to_flow",
    bind=True,
    max_retries=3
)
def inject_curiosities_to_flow(self, articles: list, daily_target: int = 50):
    """Intercala curiosidades no fluxo de artigos."""
    try:
        mixed = mix_with_articles(articles, daily_target)
        return {"status": "success", "mixed_count": len(mixed)}
    except Exception as e:
        logger.error(f"[CELERY] Erro em inject_curiosities_to_flow: {e}")
        raise self.retry(exc=e)
