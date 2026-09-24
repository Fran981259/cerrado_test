"""Tarefas Celery que orquestram a coleta e o pipeline editorial."""

import logging
import os
from datetime import datetime, timezone
from time import perf_counter

from app.celery_app import celery_app
from app.runtime_config import get_scheduler_settings
from app.scanner import RealPortalScanner
from app.tasks.scan_persistence import persist_articles as _persist_articles

logger = logging.getLogger(__name__)


def _scan_and_persist() -> tuple[dict, dict]:
    """Coleta os portais configurados e persiste os novos rascunhos."""
    results = RealPortalScanner().scan_all()
    articles = results.get("articles", [])
    logger.info("[SCAN] Coletados %s artigos", len(articles))
    persisted = _persist_articles(articles)
    logger.info("[SCAN] Persistidos: %s", persisted)
    return results, persisted


@celery_app.task(
    name="app.tasks.scan_tasks.scan_brazil_news", bind=True, max_retries=3, time_limit=600, soft_time_limit=540
)
def scan_brazil_news(self):
    """Coleta notícias locais e as persiste como rascunhos para o pipeline."""
    try:
        results, persisted = _scan_and_persist()
        return {
            "status": "success",
            "articles_collected": len(results.get("articles", [])),
            "portals": results.get("summary", {}),
            "persisted": persisted,
        }
    except Exception as error:
        logger.error("[SCAN] Erro: %s", error)
        raise self.retry(exc=error)


@celery_app.task(
    name="app.tasks.scan_tasks.scan_and_queue", bind=True, max_retries=3, time_limit=600, soft_time_limit=540
)
def scan_and_queue(self):
    """Coleta e coloca rascunhos na sequência classify, rewrite e publish."""
    try:
        results, persisted = _scan_and_persist()
        return {"status": "success", "collected": len(results.get("articles", [])), "persisted": persisted}
    except Exception as error:
        logger.error("[SCAN] Erro no pipeline: %s", error)
        raise self.retry(exc=error)


def _acquire_pipeline_lock():
    """Retorna o lock Redis do pipeline, ou ``None`` quando indisponível."""
    if not os.getenv("REDIS_URL"):
        return None
    try:
        import redis

        client = redis.from_url(os.getenv("REDIS_URL"), socket_connect_timeout=2, socket_timeout=2)
        return client if client.set("lock:run_full_pipeline", "1", nx=True, ex=1500) else False
    except Exception:
        return None


def _run_pipeline_stages() -> tuple[dict, dict]:
    """Executa as quatro etapas e mede a duração de cada uma."""
    from app.tasks.classify_tasks import classify_pending_articles
    from app.tasks.publish_tasks import publish_ready_articles
    from app.tasks.rewrite_tasks import rewrite_pending_articles

    stages = (
        ("scan", scan_and_queue),
        ("classify", classify_pending_articles),
        ("rewrite", rewrite_pending_articles),
        ("publish", publish_ready_articles),
    )
    results, timings = {}, {}
    for name, task in stages:
        started_at = perf_counter()
        results[name] = task()
        timings[name] = round(perf_counter() - started_at, 3)
    return results, timings


def _log_daily_volume() -> None:
    """Registra se a meta editorial diária de publicações locais foi atingida."""
    from app.database import get_session
    from app.schema import NewsArticle

    db = get_session()
    try:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        published = (
            db.query(NewsArticle)
            .filter(
                NewsArticle.status == "published",
                NewsArticle.visibility == "public",
                NewsArticle.region == "ms",
                NewsArticle.published_at >= today_start,
            )
            .count()
        )
        target = get_scheduler_settings().min_articles_per_day
        logger.info("[PIPELINE] Volume diário: %s/%s artigos publicados", published, target)
    finally:
        db.close()


def _release_pipeline_lock(client) -> None:
    """Libera o lock Redis quando esta execução o adquiriu."""
    if not client:
        return
    try:
        client.delete("lock:run_full_pipeline")
    except Exception:
        logger.warning("[PIPELINE] Não foi possível liberar o lock")


@celery_app.task(
    name="app.tasks.scan_tasks.run_full_pipeline", bind=True, max_retries=3, time_limit=1500, soft_time_limit=1380
)
def run_full_pipeline(self):
    """Executa scan, classificação, reescrita e publicação sob lock distribuído."""
    started_at = perf_counter()
    lock_client = _acquire_pipeline_lock()
    if lock_client is False:
        logger.warning("[PIPELINE] Pipeline já em execução — pulando esta janela")
        return {"status": "skipped", "reason": "pipeline already running"}
    try:
        results, timings = _run_pipeline_stages()
        _log_daily_volume()
        timings["total"] = round(perf_counter() - started_at, 3)
        logger.info("[PIPELINE] Duração por etapa (s): %s", timings)
        return {"status": "success", **results, "timings_seconds": timings}
    except Exception as error:
        logger.error("[PIPELINE] Erro: %s", error)
        raise self.retry(exc=error)
    finally:
        _release_pipeline_lock(lock_client)
