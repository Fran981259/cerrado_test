"""
Celery App — Atualiza Brasil
Configuração do Celery para agendamento de tarefas.
"""

from celery import Celery
from celery.schedules import crontab
import os

# Configuração do broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Criação do app Celery
celery_app = Celery(
    "atualiza_brasil",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.scan_tasks",
        "app.tasks.mine_tasks",
        "app.tasks.classify_tasks",
        "app.tasks.rewrite_tasks",
        "app.tasks.publish_tasks",
        "app.tasks.curiosity_tasks",
        "app.tasks.auditor_tasks",
        "app.tasks.maintenance",
        "app.tasks.frontend_tasks",
    ]
)

# Configurações do Celery
celery_app.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,

    # Configurações de resultado
    result_expires=3600,  # Resultados expiram em 1 hora
    result_backend_transport_options={
        "master_name": "mymaster"
    },

    # Configurações de task
    task_acks_late=True,  # Confirma após executar
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutos por task
    task_soft_time_limit=240,  # 4 minutos soft limit

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
            "schedule": 1800.0,  # A cada 30 minutos
        },

        # ================================
        # MINER (Notícias Globais)
        # ================================
        "mine-global-news": {
            "task": "app.tasks.mine_tasks.mine_global_news",
            "schedule": 1800.0,  # A cada 30 minutos
        },

        # ================================
        # CURIOSIDADES (1x ao dia)
        # ================================
        "generate-daily-curiosities": {
            "task": "app.tasks.curiosity_tasks.generate_daily_curiosities",
            "schedule": crontab(hour=6, minute=0),  # 06:00 todo dia
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
        "update-sitemap": {
            "task": "app.tasks.maintenance.update_sitemap",
            "schedule": crontab(hour=4, minute=0),  # 04:00 todo dia
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


@celery_app.task(bind=True)
def debug_task(self):
    """Task de debug para verificar se o Celery está rodando."""
    print(f"Request: {self.request!r}")
    return True
