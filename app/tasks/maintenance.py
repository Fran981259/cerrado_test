"""
Tarefas de Manutenção do Sistema — Portal Cerrado
VERSÃO REAL: cleanup, sitemap, health e métricas com DB/Redis.
"""
from app.celery_app import celery_app
from datetime import datetime, timedelta, timezone
import logging
import os

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.maintenance.cleanup_old_content",
    bind=True,
    max_retries=3
)
def cleanup_old_content(self):
    """
    Remove conteúdo antigo: drafts >7d, failed >3d, logs antigos.
    Arquiva publicadas antigas (visibility='archived', saem das listas/sitemap,
    link direto continua abrindo). Roda 1x ao dia às 03:00.
    """
    ARCHIVE_DAYS = int(os.getenv("ARCHIVE_DAYS_AFTER_PUBLISH", "30"))
    try:
        logger.info("[MAINTENANCE] Iniciando cleanup_old_content")
        from app.database import get_session
        from app.schema import NewsArticle, PublicationLog, ScrapingTask, EditorialTrendSignal

        db = get_session()
        cleaned = 0
        try:
            now = datetime.now(timezone.utc)
            db.query(EditorialTrendSignal).filter(EditorialTrendSignal.generated_at < now - timedelta(days=2)).delete(synchronize_session=False)
            # drafts com mais de 7 dias sem evoluir
            cutoff_draft = now - timedelta(days=7)
            q1 = db.query(NewsArticle).filter(
                NewsArticle.status == "draft",
                NewsArticle.created_at < cutoff_draft
            ).delete(synchronize_session=False)
            cleaned += q1

            # failed com mais de 3 dias
            cutoff_failed = now - timedelta(days=3)
            q2 = db.query(NewsArticle).filter(
                NewsArticle.status == "failed",
                NewsArticle.updated_at < cutoff_failed
            ).delete(synchronize_session=False)
            cleaned += q2

            # logs de publicação com mais de 90 dias (LGPD)
            cutoff_logs = now - timedelta(days=90)
            try:
                q3 = db.query(PublicationLog).filter(PublicationLog.created_at < cutoff_logs).delete(synchronize_session=False)
                cleaned += q3
            except Exception:
                q3 = 0

            # scraping tasks antigas >30d
            try:
                cutoff_scrap = now - timedelta(days=30)
                q4 = db.query(ScrapingTask).filter(ScrapingTask.created_at < cutoff_scrap).delete(synchronize_session=False)
                cleaned += q4
            except Exception:
                q4 = 0

            # publicadas antigas: arquiva (não apaga — preserva link e histórico)
            cutoff_arch = now - timedelta(days=ARCHIVE_DAYS)
            archived = db.query(NewsArticle).filter(
                NewsArticle.status == "published",
                NewsArticle.visibility == "public",
                NewsArticle.published_at < cutoff_arch
            ).update({"visibility": "archived"}, synchronize_session=False)

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        logger.info(f"[MAINTENANCE] Cleanup: {cleaned} removidos, {archived} arquivados")
        return {
            "status": "success",
            "cleaned": cleaned,
            "archived": archived,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em cleanup_old_content: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.maintenance.system_health_check",
    bind=True,
    max_retries=3
)
def system_health_check(self):
    """
    Verifica saúde real: DB, Redis, contagem de publicações recentes.
    Roda a cada 5 minutos.
    """
    try:
        checks = {}
        status = "healthy"

        # DB
        try:
            from app.database import get_session
            from app.schema import NewsArticle
            db = get_session()
            try:
                db.execute  # noqa
                # query simples
                cnt = db.query(NewsArticle).count()
                checks["database"] = f"ok ({cnt} artigos)"
            finally:
                db.close()
        except Exception as e:
            checks["database"] = f"fail: {e}"
            status = "unhealthy"

        # Redis
        try:
            import redis as redis_lib
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis_lib.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            checks["redis"] = "ok"
        except Exception as e:
            checks["redis"] = f"fail: {e}"
            # não marca unhealthy se for local fallback sem Redis
            if os.getenv("ENABLE_LOCAL_SCHEDULER", "0") == "1" and os.getenv("CELERY_SCHEDULER", "0") != "1":
                checks["redis"] += " (local scheduler ativo, tolerado)"
            else:
                if status != "unhealthy":
                    status = "degraded"

        # Celery (se estamos aqui, está ok)
        checks["celery"] = "task_executed; worker/beat heartbeat requires external monitoring"

        # publicação recente (alerta se parada há >2h)
        try:
            from app.database import get_session
            from app.schema import NewsArticle
            db = get_session()
            try:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
                recent = db.query(NewsArticle).filter(
                    NewsArticle.status == "published",
                    NewsArticle.published_at >= cutoff
                ).count()
                checks["recent_published_2h"] = recent
                if recent == 0:
                    # só alerta se já deveria haver publicações (após GO-LIVE)
                    checks["publication"] = "warn: nenhuma publicação nas últimas 2h"
            finally:
                db.close()
        except Exception as e:
            checks["publication"] = f"check fail: {e}"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "checks": checks
        }
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em system_health_check: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}


@celery_app.task(
    name="app.tasks.maintenance.report_metrics",
    bind=True,
    max_retries=3
)
def report_metrics(self):
    """
    Reporta métricas reais de produção.
    Roda 1x por hora.
    """
    try:
        logger.info("[MAINTENANCE] Reportando métricas")
        from app.database import get_session
        from app.schema import NewsArticle
        from sqlalchemy import func

        db = get_session()
        try:
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            hour_start = now.replace(minute=0, second=0, microsecond=0)

            articles_today = db.query(NewsArticle).filter(
                NewsArticle.status == "published",
                NewsArticle.published_at >= today_start
            ).count()

            articles_this_hour = db.query(NewsArticle).filter(
                NewsArticle.status == "published",
                NewsArticle.published_at >= hour_start
            ).count()

            total_published = db.query(NewsArticle).filter(NewsArticle.status == "published").count()
            total_draft = db.query(NewsArticle).filter(NewsArticle.status == "draft").count()
            total_failed = db.query(NewsArticle).filter(NewsArticle.status == "failed").count()
            total_all = db.query(NewsArticle).count()

            # por categoria
            by_cat = db.query(NewsArticle.category, func.count()).filter(
                NewsArticle.status == "published"
            ).group_by(NewsArticle.category).all()
            by_category = {cat or "unknown": cnt for cat, cnt in by_cat}

            # taxa sucesso = published / total
            success_rate = (total_published / total_all * 100) if total_all else 0

            # erros recentes = failed nas últimas 24h
            cutoff_24h = now - timedelta(hours=24)
            errors_24h = db.query(NewsArticle).filter(
                NewsArticle.status == "failed",
                NewsArticle.updated_at >= cutoff_24h
            ).count()

        finally:
            db.close()

        metrics = {
            "timestamp": now.isoformat(),
            "articles_today": articles_today,
            "articles_this_hour": articles_this_hour,
            "total_published": total_published,
            "total_draft": total_draft,
            "total_failed": total_failed,
            "total_all": total_all,
            "by_category": by_category,
            "success_rate": round(success_rate, 2),
            "errors_24h": errors_24h
        }
        logger.info(f"[MAINTENANCE] Métricas: {metrics}")
        return metrics
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em report_metrics: {e}")
        raise self.retry(exc=e)
