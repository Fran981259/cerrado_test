"""
Celery App — Portal Cerrado
Configuração do Celery para agendamento de tarefas.
"""

import os

from celery import Celery
from celery.schedules import crontab

from app.contracts import DISPLAY_TIMEZONE_NAME
from app.runtime_config import get_scheduler_settings

# Configuração do broker
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError("REDIS_URL obrigatorio em producao")
    REDIS_URL = "redis://localhost:6379/0"

SCHEDULER_SETTINGS = get_scheduler_settings()

# Criação do app Celery
celery_app = Celery(
    "portal_cerrado",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.scan_tasks",
        "app.tasks.classify_tasks",
        "app.tasks.rewrite_tasks",
        "app.tasks.publish_tasks",
        "app.tasks.auditor_tasks",
        "app.tasks.maintenance",
        "app.tasks.social_tasks",
    ],
)

# Configurações do Celery
celery_app.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=DISPLAY_TIMEZONE_NAME,
    enable_utc=True,
    # Configurações de resultado
    result_expires=3600,  # Resultados expiram em 1 hora
    result_backend_transport_options={"master_name": "mymaster"},
    # Configurações de task
    task_acks_late=True,  # Confirma após executar
    task_reject_on_worker_lost=True,
    task_time_limit=1500,  # pipeline completo pode levar ate 25 minutos
    task_soft_time_limit=1380,
    # Retry
    task_default_retry_delay=60,  # 1 minuto entre retries
    task_max_retries=3,
    # Beat schedule (agendamento)
    beat_schedule={
        # ================================
        # PIPELINE COMPLETO (scan -> classify -> rewrite -> publish -> export)
        # Roda a cada 30 minutos
        # ================================
        "run-full-pipeline": {
            "task": "app.tasks.scan_tasks.run_full_pipeline",
            "schedule": SCHEDULER_SETTINGS.pipeline_interval_seconds,
        },
        # ================================
        # LIMPEZA (1x ao dia)
        # ================================
        "cleanup-old-content": {
            "task": "app.tasks.maintenance.cleanup_old_content",
            "schedule": crontab(hour=3, minute=0),  # 03:00 todo dia
        },
        # ================================
        # SITEMAP (1x ao dia)
        # ================================
        # ================================
        # REDES SOCIAIS: TOP NEWS TWITTER (3x ao dia)
        # ================================
        "post-top-news-twitter": {
            "task": "app.tasks.social_tasks.post_top_news_twitter",
            "schedule": crontab(hour="8,14,20", minute=0),  # 08:00, 14:00, 20:00
        },
        # ================================
        # HEALTH CHECK (a cada 5 min)
        # ================================
        "system-health-check": {
            "task": "app.tasks.maintenance.system_health_check",
            "schedule": 300.0,  # A cada 5 minutos
        },
        # ================================
        # MÉTRICAS (1x por hora)
        # ================================
        "report-metrics": {
            "task": "app.tasks.maintenance.report_metrics",
            "schedule": crontab(minute=0),  # A cada hora (minuto 0)
        },
        # ================================
        # HORUS — AUDITORIA (1x por hora)
        # ================================
        "horus-full-audit": {
            "task": "app.tasks.auditor_tasks.full_audit",
            "schedule": crontab(minute=30),  # A cada hora (minuto 30)
        },
        # ================================
        # EVOLUÇÃO DE PERSONALIDADE (1x ao dia)
        # ================================
        "evolve-reporters": {
            "task": "app.tasks.auditor_tasks.evolve_reporters",
            "schedule": crontab(hour=2, minute=0),  # 02:00 todo dia
        },
    },
)
