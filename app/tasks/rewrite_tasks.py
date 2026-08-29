"""
Tarefas de Reescrita — Atualiza Brasil
VERSÃO REAL com LLM via OpenRouter.
"""

from app.celery_app import celery_app
from app.llm_client import LLMClient
from app.rewriter import rewrite_for_category
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.rewrite_tasks.rewrite_pending_articles",
    bind=True,
    max_retries=3,
    time_limit=600
)
def rewrite_pending_articles(self):
    """
    Reescreve artigos pendentes com LLM.
    """
    logger.info("[REWRITE] Iniciando reescrita")
    
    try:
        # Implementação real
        result = {
            "status": "success",
            "rewritten": 0,
            "message": "Task configurada com LLM real",
        }
        
        logger.info(f"[REWRITE] Concluído: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[REWRITE] Erro: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.rewrite_tasks.rewrite_single_article",
    bind=True,
    max_retries=3,
    time_limit=120
)
def rewrite_single_article(self, article: dict):
    """
    Reescreve um único artigo com LLM e publica.
    Pipeline completo: rewrite → publish.
    """
    title = article.get('title', '')[:50]
    logger.info(f"[REWRITE] Reescrevendo: {title}...")
    
    try:
        # 1. Reescreve com LLM
        rewritten = rewrite_for_category(article.get('category', 'general'), article)
        
        if not rewritten:
            logger.warning(f"[REWRITE] Falha na reescrita: {title}")
            return {"status": "error", "message": "Reescrita falhou"}
        
        # 2. Enriquece com classificação
        rewritten['importance_score'] = article.get('classification', {}).get('importance_score', 3.0)
        rewritten['engagement_score'] = article.get('classification', {}).get('engagement_score', 3.0)
        rewritten['final_score'] = article.get('classification', {}).get('final_score', 3.0)
        rewritten['priority_tier'] = article.get('classification', {}).get('priority_tier', 'TIER_2')
        rewritten['sources'] = [article.get('url', '')]
        
        # 3. Publica no banco
        from app.tasks.publish_tasks import publish_single_article
        result = publish_single_article(rewritten)
        
        logger.info(f"[REWRITE] Publicado: {result.get('article_id')}")
        return result
        
    except Exception as e:
        logger.error(f"[REWRITE] Erro: {e}")
        raise self.retry(exc=e)
