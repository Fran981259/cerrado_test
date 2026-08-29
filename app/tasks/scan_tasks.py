"""
Tarefas de Scan — Atualiza Brasil
VERSÃO REAL - Coleta de portais brasileiros.
"""

from app.celery_app import celery_app
from app.scanner import RealPortalScanner, scan_all_portals
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.scan_tasks.scan_brazil_news",
    bind=True,
    max_retries=3,
    time_limit=300
)
def scan_brazil_news(self):
    """
    Coleta notícias de portais brasileiros (piloto MS).
    VERSÃO REAL com scraping.
    """
    logger.info("[SCAN] Iniciando scan de portais BR")
    
    try:
        scanner = RealPortalScanner()
        results = scanner.scan_all()
        
        logger.info(f"[SCAN] Concluído: {results['summary']}")
        
        return {
            "status": "success",
            "articles_collected": len(results.get("articles", [])),
            "portals": results.get("summary", {}),
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"[SCAN] Erro: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.scan_tasks.scan_specific_portal",
    bind=True,
    max_retries=3,
    time_limit=60
)
def scan_specific_portal(self, portal_url: str):
    """Escaneia um portal específico."""
    logger.info(f"[SCAN] Portal: {portal_url}")
    
    try:
        scanner = RealPortalScanner()
        for portal in scanner.PORTALS:
            if portal["url"] == portal_url:
                result = scanner._scan_portal(portal)
                return result
        
        return {"status": "error", "message": "Portal não encontrado"}
        
    except Exception as e:
        logger.error(f"[SCAN] Erro: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.scan_tasks.scan_and_queue",
    bind=True,
    max_retries=3,
    time_limit=300
)
def scan_and_queue(self):
    """
    Scan completo: coleta e coloca na fila para reescrever.
    Este é o pipeline principal.
    """
    logger.info("[SCAN] Scan + Queue - Iniciando")
    
    try:
        # 1. Scan
        scanner = RealPortalScanner()
        scan_results = scanner.scan_all()
        articles = scan_results.get("articles", [])
        
        logger.info(f"[SCAN] Coletados {len(articles)} artigos")
        
        # 2. Classifica cada artigo
        from app.classifier import classify_articles
        classified = classify_articles(articles)
        
        # 3. Filtra por qualidade
        from app.filter import filter_articles
        filtered = filter_articles(classified)
        
        logger.info(f"[SCAN] Após filtro: {len(filtered)} artigos")
        
        # 4. Fila para reescrita
        queued = 0
        for article in filtered:
            try:
                # Chama tarefa de reescrita
                rewrite_single_article.delay(article)
                queued += 1
            except Exception as e:
                logger.error(f"[SCAN] Erro ao enfileirar: {e}")
        
        logger.info(f"[SCAN] Enfileirados {queued} artigos para reescrita")
        
        return {
            "status": "success",
            "collected": len(articles),
            "filtered": len(filtered),
            "queued": queued,
        }
        
    except Exception as e:
        logger.error(f"[SCAN] Erro no pipeline: {e}")
        raise self.retry(exc=e)


# Import task local para evitar circular
def rewrite_single_article(article):
    from app.tasks.rewrite_tasks import rewrite_single_article as task
    return task.delay(article)
