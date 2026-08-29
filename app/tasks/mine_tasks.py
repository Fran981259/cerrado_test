"""
Tarefas de Mineração de Notícias Globais
"""
from app.celery_app import celery_app
from app.miner import MinerPipeline, GlobalNewsMiner
from app.translator import NewsTranslator
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.mine_tasks.mine_global_news",
    bind=True,
    max_retries=3,
    default_retry_delay=60
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
        logger.info(f"[CELERY] Mineração concluída: {len(articles)} artigos")
        return {
            "status": "success",
            "articles_mined": len(articles),
            "timestamp": str(__import__('datetime').datetime.utcnow())
        }
    except Exception as e:
        logger.error(f"[CELERY] Erro em mine_global_news: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.mine_tasks.translate_article",
    bind=True,
    max_retries=3
)
def translate_article(self, article_data: dict):
    """Traduz um artigo específico para pt-BR."""
    try:
        translator = NewsTranslator()
        translated = translator.translate(article_data)
        return {"status": "success", "translated": translated}
    except Exception as e:
        logger.error(f"[CELERY] Erro em translate_article: {e}")
        raise self.retry(exc=e)
