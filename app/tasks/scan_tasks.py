"""
Tarefas de Scan — Portal Cerrado
VERSÃO REAL - Coleta de portais brasileiros e PERSISTE no banco de dados.
"""

from app.celery_app import celery_app
from app.scanner import RealPortalScanner
from app.database import get_session
from app.schema import NewsArticle, Reporter
from typing import Optional
import hashlib
import re
import logging
from datetime import datetime, timezone
from app.contracts import as_utc, category_name, sources_list
from app.schema import ArticleIdentity
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


def _clean_plain_text(value: str) -> str:
    if not value:
        return ""
    try:
        from bs4 import BeautifulSoup
        value = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    except Exception:
        value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[\r\n\t]+", " ", value)
    return re.sub(r"\s{2,}", " ", value).strip()


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
            dt = as_utc(dt).replace(tzinfo=None)
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
    Pula artigos já existentes (deduplicação por URL hash + similaridade de título).
    """
    db = get_session()
    inserted = 0
    duplicates = 0
    errors = 0
    fetched = 0
    fetch_miss = 0
    seen = set()
    recent_titles = []
    try:
        from app.rewriter import get_reporter_for_category
        from app.article_fetcher import ArticleFetcher
        from app.filter import DuplicateDetector
        from datetime import datetime as _dt
        fetcher = ArticleFetcher() if fetch_details else None

        # Carrega títulos recentes para dedup por similaridade
        try:
            recent = db.query(NewsArticle.title).filter(
                NewsArticle.status.in_(["draft", "classified", "rewritten", "published"])
            ).order_by(NewsArticle.created_at.desc()).limit(200).all()
            recent_titles = [r[0] for r in recent if r[0]]
        except Exception:
            recent_titles = []

        for a in articles:
            try:
                url = a.get("url", "")
                h = _url_hash(a.get("identity_key") or url)
                if not url and not (a.get("needs_review") and a.get("identity_key")):
                    errors += 1
                    continue
                if h in seen:
                    duplicates += 1
                    continue
                seen.add(h)

                exists = (
                    db.query(NewsArticle)
                    .filter(NewsArticle.compliance_hash == h)
                    .first()
                )
                if exists:
                    duplicates += 1
                    continue

                # Trava de Idioma e Qualidade Semântica
                from app.filter import ContentFilter
                new_title = (a.get("title") or "")[:500]
                new_summary = (a.get("summary") or "")[:2000]

                # Dedup por similaridade de título (Exata e Semântica)
                is_title_dup = False
                if new_title and recent_titles:
                    dummy = {"title": new_title}
                    for existing_title in recent_titles[-50:]:
                        if DuplicateDetector.are_duplicates(dummy, {"title": existing_title}, threshold=0.85):
                            is_title_dup = True
                            break
                        # Se não for similar exato, tenta similaridade semântica de palavras-chave
                        if DuplicateDetector.are_semantically_similar(new_title, existing_title):
                            logger.info(f"[SCAN] Duplicata SEMÂNTICA detectada: '{new_title}' e '{existing_title}'")
                            is_title_dup = True
                            break
                            
                if is_title_dup:
                    duplicates += 1
                    continue

                identity = ArticleIdentity(key="source:" + h)
                db.add(identity)
                db.flush()

                # ---- Extração de alta qualidade da página real ----
                title = _clean_plain_text(a.get("title") or "")[:500]
                lead = _clean_plain_text(a.get("summary") or "")[:2000]
                body = a.get("body") or ""
                published_at = None
                author = None
                image_url = None

                if fetcher:
                    detail = fetcher.fetch(url, base_summary=a.get("summary", ""))
                    if detail.get("status") == "success":
                        fetched += 1
                        if detail.get("title"):
                            title = _clean_plain_text(detail["title"])[:500]
                        if detail.get("lead"):
                            lead = _clean_plain_text(detail["lead"])[:2000]
                        body = detail.get("content") or ""
                        published_at = _parse_iso_datetime(detail.get("published_at"))
                        author = (detail.get("author") or "")[:200]
                        image_url = (detail.get("image_url") or "")[:500]
                    else:
                        fetch_miss += 1
                        if detail.get("status") == "blocked":
                            db.rollback()
                            errors += 1
                            continue

                # Anti-Frankenstein Check (RSS Title vs HTML Body)
                rss_title_text = _clean_plain_text(a.get("title") or "")
                if rss_title_text and body:
                    # check overlap
                    import re
                    def get_words(t): 
                        return set(w for w in re.findall(r'\b\w+\b', t.lower()) if len(w) > 2)
                    rt_words = get_words(rss_title_text)
                    b_words = get_words(body)
                    if rt_words:
                        overlap = len(rt_words.intersection(b_words)) / len(rt_words)
                        if overlap < 0.15 and len(rt_words) >= 3:
                            logger.warning(f"[SCAN] Frankenstein detectado na raiz! Abortando URL {url}")
                            db.rollback()
                            errors += 1
                            continue

                title = _clean_plain_text(a.get("title_pt") or title)[:500]
                lead = _clean_plain_text(a.get("summary_pt") or lead)[:2000]
                category = category_name(a.get("category"))
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
                        email=f"{reporter_profile.slug}@portalcerrado.com.br",
                    )
                    db.add(reporter)
                    db.flush()

                slug = _make_draft_slug(title, h)
                dt_now = datetime.now(timezone.utc)
                article = NewsArticle(
                        title=title,
                        slug=slug,
                        summary=lead,
                        content=body,
                        author=author,
                        image_url=image_url,
                        reporter_id=reporter.id,
                        sources=sources_list([{"url": url, "name": a.get("source", ""), "title": title}]),
                        original_text=body or lead,
                        compliance_hash=h,
                        status="review" if a.get("needs_review") else "draft",
                        category=category,
                        tags=[category],
                        is_curiosity=bool(a.get("is_curiosity")),
                        published_at=published_at,
                        created_at=dt_now,
                        updated_at=dt_now,
                    )
                db.add(article)
                db.flush()
                identity.article_id = article.id
                db.commit()
                inserted += 1
            except IntegrityError:
                db.rollback()
                if db.get(ArticleIdentity, "source:" + h):
                    duplicates += 1
                else:
                    errors += 1
            except Exception as exc:
                db.rollback()
                errors += 1
                logger.error("[SCAN] erro ao persistir artigo (%s)", type(exc).__name__)
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
    time_limit=600,
    soft_time_limit=540
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
    name="app.tasks.scan_tasks.scan_and_queue",
    bind=True,
    max_retries=3,
    time_limit=600,
    soft_time_limit=540
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
    time_limit=1500,
    soft_time_limit=1380
)
def run_full_pipeline(self):
    """
    Executa o pipeline completo de forma síncrona e confiável:
    scan -> persistir drafts -> classificar -> reescrever -> publicar.
    É o gatilho principal do agendamento.
    """
    MIN_ARTICLES_PER_DAY = 50
    # lock distribuído para evitar sobreposição beat 1800s
    lock_acquired = False
    lock_key = "lock:run_full_pipeline"
    redis_client = None
    try:
        import os
        if os.getenv("REDIS_URL"):
            import redis as _r
            try:
                redis_client = _r.from_url(os.getenv("REDIS_URL"), socket_connect_timeout=2, socket_timeout=2)
                lock_acquired = bool(redis_client.set(lock_key, "1", nx=True, ex=1500))
                if not lock_acquired:
                    logger.warning("[PIPELINE] Pipeline já em execução — pulando esta janela")
                    return {"status": "skipped", "reason": "pipeline already running"}
            except Exception:
                lock_acquired = False
                redis_client = None
        logger.info("[PIPELINE] Iniciando pipeline completo")
        from app.tasks.classify_tasks import classify_pending_articles
        from app.tasks.rewrite_tasks import rewrite_pending_articles
        from app.tasks.publish_tasks import publish_ready_articles
        from app.database import get_session
        from app.schema import NewsArticle
        from datetime import datetime, timezone, timedelta

        scan_result = scan_and_queue()
        classify_result = classify_pending_articles()
        rewrite_result = rewrite_pending_articles()
        publish_result = publish_ready_articles()

        # Volume enforcement: conta artigos publicados hoje
        try:
            db = get_session()
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            published_today = db.query(NewsArticle).filter(
                NewsArticle.status == "published",
                NewsArticle.published_at >= today_start
            ).count()
            db.close()

            if published_today < MIN_ARTICLES_PER_DAY:
                logger.warning(
                    f"[PIPELINE] Volume abaixo da meta: {published_today}/{MIN_ARTICLES_PER_DAY} artigos publicados hoje"
                )
            else:
                logger.info(f"[PIPELINE] Volume ok: {published_today}/{MIN_ARTICLES_PER_DAY} artigos publicados hoje")
        except Exception as vol_err:
            logger.warning(f"[PIPELINE] Não foi possível verificar volume: {vol_err}")

        logger.info("[PIPELINE] Pipeline completo finalizado")
        return {
            "status": "success",
            "scan": scan_result,
            "classify": classify_result,
            "rewrite": rewrite_result,
            "publish": publish_result,
        }
    except Exception as e:
        logger.error(f"[PIPELINE] Erro: {e}")
        raise self.retry(exc=e)
    finally:
        if redis_client and lock_acquired:
            try:
                redis_client.delete(lock_key)
            except Exception:
                pass
