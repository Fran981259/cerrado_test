"""
Tarefas de Manutenção do Sistema — Atualiza Brasil
VERSÃO REAL: cleanup, sitemap, health e métricas com DB/Redis.
"""
from app.celery_app import celery_app
from datetime import datetime, timedelta
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
    Roda 1x ao dia às 03:00.
    """
    try:
        logger.info("[MAINTENANCE] Iniciando cleanup_old_content")
        from app.database import get_session
        from app.schema import NewsArticle, PublicationLog, ScrapingTask

        db = get_session()
        cleaned = 0
        try:
            now = datetime.utcnow()
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

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        logger.info(f"[MAINTENANCE] Cleanup: {cleaned} registros removidos")
        return {
            "status": "success",
            "cleaned": cleaned,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em cleanup_old_content: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.maintenance.update_sitemap",
    bind=True,
    max_retries=3
)
def update_sitemap(self):
    """
    Atualiza sitemap.xml com matérias publicadas (DB real).
    Gera frontend/public/sitemap.xml e frontend/src/data/sitemap.json para debug.
    Roda 1x ao dia às 04:00.
    """
    try:
        logger.info("[MAINTENANCE] Iniciando update_sitemap")
        from app.database import get_session
        from app.schema import NewsArticle
        import xml.etree.ElementTree as ET

        db = get_session()
        try:
            arts = db.query(NewsArticle).filter(
                NewsArticle.status == "published",
                NewsArticle.visibility == "public"
            ).order_by(NewsArticle.published_at.desc()).limit(500).all()
        finally:
            db.close()

        base = os.getenv("NEXT_PUBLIC_SITE_URL") or os.getenv("SITE_URL") or "https://atualizabrasil.news"
        base = base.rstrip("/")

        # monta XML
        urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        static = [
            (f"{base}/", "hourly", "1.0"),
            (f"{base}/sobre", "monthly", "0.6"),
            (f"{base}/privacidade", "yearly", "0.3"),
            (f"{base}/termos", "yearly", "0.3"),
            (f"{base}/contato", "yearly", "0.5"),
        ]
        for url, freq, prio in static:
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = url
            ET.SubElement(url_el, "changefreq").text = freq
            ET.SubElement(url_el, "priority").text = prio

        for a in arts:
            if not a.slug:
                continue
            url_el = ET.SubElement(urlset, "url")
            ET.SubElement(url_el, "loc").text = f"{base}/noticia/{a.slug}"
            lastmod = (a.published_at or a.updated_at or datetime.utcnow()).date().isoformat()
            ET.SubElement(url_el, "lastmod").text = lastmod
            ET.SubElement(url_el, "changefreq").text = "daily"
            ET.SubElement(url_el, "priority").text = "0.8"

        # escreve em frontend/public/sitemap.xml
        root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
        public_dir = os.path.join(root, "frontend", "public")
        os.makedirs(public_dir, exist_ok=True)
        out_path = os.path.join(public_dir, "sitemap.xml")
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ")
        tree.write(out_path, encoding="utf-8", xml_declaration=True)

        logger.info(f"[MAINTENANCE] Sitemap gerado: {len(arts)} notícias + 5 estáticas -> {out_path}")
        return {
            "status": "success",
            "sitemap_updated": True,
            "articles_in_sitemap": len(arts),
            "path": out_path
        }
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em update_sitemap: {e}")
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
            if os.getenv("ENABLE_LOCAL_SCHEDULER", "1") == "1":
                checks["redis"] += " (local scheduler ativo, tolerado)"
            else:
                status = "degraded"

        # Celery (se estamos aqui, está ok)
        checks["celery"] = "ok"

        # publicação recente (alerta se parada há >2h)
        try:
            from app.database import get_session
            from app.schema import NewsArticle
            db = get_session()
            try:
                cutoff = datetime.utcnow() - timedelta(hours=2)
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
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "checks": checks
        }
    except Exception as e:
        logger.error(f"[MAINTENANCE] Erro em system_health_check: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.utcnow().isoformat()}


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
            now = datetime.utcnow()
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
