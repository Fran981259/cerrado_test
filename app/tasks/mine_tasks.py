"""
Tarefas de Mineração de Notícias Globais
"""
from app.celery_app import celery_app
from app.miner import MinerPipeline
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.mine_tasks.mine_global_news",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=1500,
    soft_time_limit=1380,
)
def mine_global_news(self):
    """
    Coleta notícias de portais globais.
    Roda a cada 30 minutos.
    """
    try:
        logger.info("[CELERY] Iniciando mine_global_news")
        pipeline = MinerPipeline()
        articles = pipeline.run(target_volume=50)
        from app.tasks.scan_tasks import _persist_articles
        persisted = _persist_articles(articles)
        pipeline.miner.session.close()
        logger.info(f"[CELERY] Mineração concluída: {len(articles)} artigos")
        return {
            "status": "success",
            "articles_mined": len(articles),
            "persisted": persisted,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"[CELERY] Erro em mine_global_news: {e}")
        raise self.retry(exc=e)
