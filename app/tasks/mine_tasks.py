"""Compatibility task for retired global-news queues."""

import logging
from datetime import datetime, timezone

from app.celery_app import celery_app
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
    """Acknowledge retired jobs without collecting or publishing anything."""
    # Kept as a harmless compatibility entrypoint for queues that still contain
    # the old task name. Global mining is not part of Portal Cerrado's mandate.
    logger.warning("[CELERY] mine_global_news ignorada: mineração global está desativada pela política editorial")
    return {
        "status": "disabled",
        "articles_mined": 0,
        "persisted": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
