"""Tarefas de Reescrita — Portal Cerrado."""

import logging
import re
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.llm_client import LLMClient
from app.rewriter import load_reporters_config
from app.scanner import RealPortalScanner
from app.contracts import category_name, sources_list

logger = logging.getLogger(__name__)


def source_name_from_url(url: str) -> str:
    if 'msnews.com.br' in url:
        return 'MS News'
    if 'mstododia.com.br' in url:
        return 'MS Todo Dia'
    if 'agenciadenoticias.ms.gov.br' in url:
        return 'Agência de Notícias MS'
    if 'oestadoonline.com.br' in url:
        return 'O Estado Online'
    return 'Portal de Notícias'


def _find_related_sources(article: dict, max_related: int = 3) -> list:
    """Busca até 3 fontes relacionadas ao mesmo fato no banco para cruzamento."""
    try:
        from app.database import get_session
        from app.schema import NewsArticle
        db = get_session()
        try:
            title = article.get("title", "").lower()
            keywords = [w for w in re.findall(r"\w+", title) if len(w) >= 4][:6]
            if not keywords:
                return []
            candidates = db.query(NewsArticle).filter(
                NewsArticle.status.in_(["classified", "rewritten", "published"])
            ).limit(300).all()
            scored = []
            for a in candidates:
                urls = [s["url"] for s in sources_list(a.sources)]
                if article.get("url") in urls:
                    continue
                t = (a.title or "").lower()
                score = sum(1 for kw in keywords if kw in t)
                if score >= 2:
                    scored.append((score, {
                        "title": a.title,
                        "summary": a.summary or "",
                        "url": urls[0] if urls else "",
                        "source": source_name_from_url(urls[0] if urls else ""),
                    }))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [a for _, a in scored[:max_related]]
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"[REWRITE] falha ao buscar fontes relacionadas: {e}")
        return []


@celery_app.task(
    name="app.tasks.rewrite_tasks.rewrite_pending_articles",
    bind=True,
    max_retries=3,
    time_limit=600,
    soft_time_limit=540,
    rate_limit="15/m"
)
def rewrite_pending_articles(self):
    """
    Reescreve artigos em status 'classified' com LLM (Gemini/OpenAI),
    gravando o conteúdo e marcando-os como 'rewritten'.
    Roda a cada 30 minutos.
    """
    logger.info("[REWRITE] Iniciando reescrita de artigos classificados (profissional)")

    from app.database import get_session
    from app.schema import NewsArticle, Reporter

    db = get_session()
    rewritten = 0
    failed = 0
    try:
        articles = (
            db.query(NewsArticle)
            .filter(NewsArticle.status == "classified")
            .order_by(NewsArticle.final_score.desc())
            .with_for_update(skip_locked=True)
            .limit(5)
            .all()
        )

        reporters = load_reporters_config()
        llm = LLMClient()

        for art in articles:
            try:
                if not art.sources:
                    art.status = "failed"
                    art.updated_at = datetime.now(timezone.utc)
                    failed += 1
                    continue

                sources = sources_list(art.sources)
                if not sources:
                    art.status = "review"
                    failed += 1
                    continue
                main_url = sources[0]["url"]
                main_source = source_name_from_url(main_url)

                # corpo real extraído do portal (proveniência) ou, se ausente, o lead
                raw_body = (art.original_text or art.content or "")[:6000]
                clean_lead = (art.summary or "")[:400]

                article_data = {
                    "title": art.title,
                    "summary": clean_lead,
                    "body": raw_body,
                    "url": main_url,
                    "source": main_source,
                    "category": art.category or "general",
                    "published_at": art.published_at.isoformat() if art.published_at else None,
                    "author": art.author,
                }

                # repórter pela categoria
                reporter = None
                for r in reporters.values():
                    if category_name(r.role) == category_name(article_data["category"]):
                        reporter = r
                        break
                if not reporter:
                    reporter = list(reporters.values())[0]

                related = _find_related_sources(article_data, max_related=3)
                if related:
                    article_data["related_sources"] = related

                content = ""
                if llm.api_key:
                    import time as _time

                    # Espaçamento p/ respeitar RPM do tier gratuito do Gemini (flash-lite: ~10 RPM)
                    _time.sleep(12)
                    result_llm = llm.rewrite_article(
                        article_data,
                        reporter.get_system_prompt(),
                        reporter.attribution,
                        related_sources=related,
                    )
                    candidate = result_llm.get("rewritten_content", "")
                    if candidate and len(candidate.split()) >= 350:
                        content = candidate

                if not content:
                    # An upstream outage or a short answer must not delete the source.
                    art.status = "classified"
                    art.updated_at = datetime.now(timezone.utc)
                    failed += 1
                    continue

                art.content = content
                art.summary = (art.summary or "")[:2000]
                art.status = "rewritten"
                art.updated_at = datetime.now(timezone.utc)
                rewritten += 1
            except Exception as e:
                logger.error("[REWRITE] erro num artigo (%s)", type(e).__name__)
                art.status = "classified"
                art.updated_at = datetime.now(timezone.utc)
                failed += 1
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[REWRITE] erro no lote: {e}")
        raise
    finally:
        db.close()

    logger.info(f"[REWRITE] Reescritos: {rewritten}, falhas: {failed}")
    return {"status": "success", "rewritten": rewritten, "failed": failed}
