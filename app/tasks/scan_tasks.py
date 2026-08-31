"""
Tarefas de Scan — Atualiza Brasil
VERSÃO REAL - Coleta de portais brasileiros e PERSISTE no banco de dados.
"""

from app.celery_app import celery_app
from app.scanner import RealPortalScanner, scan_all_portals
from app.database import get_session
from app.schema import NewsArticle, Reporter
from typing import Optional
import hashlib
import re
import logging

logger = logging.getLogger(__name__)


def _url_hash(url: str) -> str:
    """Cria hash único a partir da URL de origem (para deduplicação)."""
    return hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:64]


def _parse_iso_datetime(value) -> Optional[object]:
    if not value or not isinstance(value, str):
        return None
    try:
        from dateutil import parser as _parser
        dt = _parser.isoparse(value.strip())
        # SQLite via SQLAlchemy espera datetime naive; remove tzinfo
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception:
        try:
            # tenta formato simples
            from datetime import datetime as _dt
            for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return _dt.strptime(value.strip()[:19], fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        return None


def _make_draft_slug(title: str, url_hash: str) -> str:
    """Gera um slug único e estável para um rascunho (baseado no título + hash)."""
    import unicodedata
    t = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t.lower()).strip("-")[:80]
    t = t or "artigo"
    # sufixo curto do hash garante unicidade sem expor dados sensíveis
    return f"{t}-{url_hash[:6]}"


def _persist_articles(articles: list, fetch_details: bool = True) -> dict:
    """
    Persiste artigos coletados no banco com status 'draft'.
    Se `fetch_details`, baixa a página real de cada matéria nova para
    extrair título limpo, lead, corpo completo, data, autor e imagem.
    Pula artigos já existentes (deduplicação pela URL de origem).
    """
    db = get_session()
    inserted = 0
    duplicates = 0
    errors = 0
    fetched = 0
    fetch_miss = 0
    try:
        from app.rewriter import get_reporter_for_category
        from app.article_fetcher import ArticleFetcher
        from datetime import datetime as _dt
        fetcher = ArticleFetcher() if fetch_details else None

        for a in articles:
            try:
                url = a.get("url", "")
                h = _url_hash(url)
                if not url:
                    errors += 1
                    continue

                exists = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.compliance_hash == h)
                    .first()
                )
                if exists:
                    duplicates += 1
                    continue

                # ---- Extração de alta qualidade da página real ----
                title = (a.get("title") or "")[:500]
                lead = (a.get("summary") or "")[:2000]
                body = ""
                published_at = None
                author = None
                image_url = None

                if fetcher:
                    detail = fetcher.fetch(url, base_summary=a.get("summary", ""))
                    if detail.get("status") == "success":
                        fetched += 1
                        if detail.get("title"):
                            title = detail["title"][:500]
                        if detail.get("lead"):
                            lead = detail["lead"][:2000]
                        body = detail.get("content") or ""
                        published_at = _parse_iso_datetime(detail.get("published_at"))
                        author = (detail.get("author") or "")[:200]
                        image_url = (detail.get("image_url") or "")[:500]
                    else:
                        fetch_miss += 1

                category = a.get("category") or "general"
                reporter_profile = get_reporter_for_category(category) or list(
                    __import__("app.rewriter", fromlist=["load_reporters_config"])
                    .load_reporters_config()
                    .values()
                )[0]

                reporter = (
                    db.query(Reporter)
                    .filter(Reporter.slug == reporter_profile.slug)
                    .first()
                )
                if not reporter:
                    reporter = Reporter(
                        slug=reporter_profile.slug,
                        display_name=reporter_profile.display_name,
                        role=reporter_profile.role,
                        email=f"{reporter_profile.slug}@atualizabrasil.news",
                    )
                    db.add(reporter)
                    db.flush()

                slug = _make_draft_slug(title, h)
                dt_now = _dt.utcnow()
                db.add(
                    NewsArticle(
                        title=title,
                        slug=slug,
                        summary=lead,
                        content=body,
                        author=author,
                        image_url=image_url,
                        reporter_id=reporter.id,
                        sources=[{"url": url, "name": a.get("source", ""), "title": title}],
                        original_text=body or lead,
                        compliance_hash=h,
                        status="draft",
                        category=category,
                        tags=[category],
                        published_at=published_at,
                        created_at=dt_now,
                        updated_at=dt_now,
                    )
                )
                inserted += 1
            except Exception:
                errors += 1
                logger.exception("[SCAN] erro ao persistir artigo")
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[SCAN] erro no commit: {e}")
        raise
    finally:
        db.close()

    return {
        "inserted": inserted,
        "duplicates": duplicates,
        "errors": errors,
        "fetched": fetched,
        "fetch_miss": fetch_miss,
    }


@celery_app.task(
    name="app.tasks.scan_tasks.scan_brazil_news",
    bind=True,
    max_retries=3,
    time_limit=300
)
def scan_brazil_news(self):
    """
    Coleta notícias de portais brasileiros (piloto MS) e persiste no banco
    como rascunhos (status='draft') para o restante do pipeline processar.
    """
    logger.info("[SCAN] Iniciando scan de portais BR")
    
    try:
        scanner = RealPortalScanner()
        results = scanner.scan_all()
        collected = results.get("articles", [])
        logger.info(f"[SCAN] Coletados {len(collected)} artigos: {results['summary']}")

        persisted = _persist_articles(collected)
        logger.info(f"[SCAN] Persistidos: {persisted}")
        
        return {
            "status": "success",
            "articles_collected": len(collected),
            "portals": results.get("summary", {}),
            "persisted": persisted,
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
    Scan completo: coleta portais e persiste rascunhos no banco
    para o pipeline (classify -> rewrite -> publish) processar.
    """
    logger.info("[SCAN] Scan + persistência - Iniciando")
    
    try:
        scanner = RealPortalScanner()
        scan_results = scanner.scan_all()
        articles = scan_results.get("articles", [])
        logger.info(f"[SCAN] Coletados {len(articles)} artigos")
        
        persisted = _persist_articles(articles)
        logger.info(f"[SCAN] Persistidos: {persisted}")
        
        return {
            "status": "success",
            "collected": len(articles),
            "persisted": persisted,
        }
        
    except Exception as e:
        logger.error(f"[SCAN] Erro no pipeline: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.scan_tasks.run_full_pipeline",
    bind=True,
    max_retries=3,
    time_limit=900,
    soft_time_limit=820
)
def run_full_pipeline(self):
    """
    Executa o pipeline completo de forma síncrona e confiável:
    scan -> persistir drafts -> classificar -> reescrever -> publicar -> exportar frontend.
    É o gatilho principal do agendamento.
    """
    logger.info("[PIPELINE] Iniciando pipeline completo")
    try:
        from app.tasks.classify_tasks import classify_pending_articles
        from app.tasks.rewrite_tasks import rewrite_pending_articles
        from app.tasks.publish_tasks import publish_ready_articles
        from app.tasks.frontend_tasks import export_frontend_articles

        scan_result = scan_and_queue()
        classify_result = classify_pending_articles()
        rewrite_result = rewrite_pending_articles()
        publish_result = publish_ready_articles()
        export_result = export_frontend_articles()

        logger.info("[PIPELINE] Pipeline completo finalizado")
        return {
            "status": "success",
            "scan": scan_result,
            "classify": classify_result,
            "rewrite": rewrite_result,
            "publish": publish_result,
            "export": export_result,
        }
    except Exception as e:
        logger.error(f"[PIPELINE] Erro: {e}")
        raise self.retry(exc=e)

