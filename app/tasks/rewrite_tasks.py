"""Tarefas de Reescrita — Portal Cerrado."""

import logging
import re
from datetime import datetime

from app.celery_app import celery_app
from app.llm_client import LLMClient
from app.rewriter import load_reporters_config
from app.scanner import RealPortalScanner

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
                urls = [s.get("url", "") for s in (a.sources or [])] if isinstance(a.sources, list) else []
                if article.get("url") in urls:
                    continue
                t = (a.title or "").lower()
                score = sum(1 for kw in keywords if kw in t)
                if score >= 1:
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
    soft_time_limit=540
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
            .limit(50)
            .all()
        )

        reporters = load_reporters_config()
        llm = LLMClient()

        for art in articles:
            try:
                if not art.sources:
                    art.status = "failed"
                    art.updated_at = datetime.utcnow()
                    failed += 1
                    continue

                main_url = art.sources[0]["url"] if isinstance(art.sources, list) and art.sources else ""
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
                    if r.role == article_data["category"]:
                        reporter = r
                        break
                if not reporter:
                    reporter = list(reporters.values())[0]

                related = _find_related_sources(article_data, max_related=3)
                if related:
                    article_data["related_sources"] = related

                content = ""
                if llm.api_key:
                    result_llm = llm.rewrite_article(
                        article_data,
                        reporter.get_system_prompt(),
                        reporter.attribution,
                        related_sources=related,
                    )
                    candidate = result_llm.get("rewritten_content", "")
                    if candidate and len(candidate.split()) >= 700:
                        content = candidate

                if not content:
                    art.status = "failed"
                    art.updated_at = datetime.utcnow()
                    failed += 1
                    continue

                art.content = content
                art.summary = (art.summary or "")[:2000]
                art.status = "rewritten"
                art.updated_at = datetime.utcnow()
                rewritten += 1
            except Exception as e:
                logger.error(f"[REWRITE] erro num artigo: {e}")
                art.status = "failed"
                art.updated_at = datetime.utcnow()
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


@celery_app.task(
    name="app.tasks.rewrite_tasks.rewrite_single_article",
    bind=True,
    max_retries=3,
    time_limit=300
)
def rewrite_single_article(self, article: dict):
    """
    Reescreve um único artigo com padrão de jornal:
    - 700-900 palavras
    - Cruzamento com 2-3 fontes do mesmo fato
    - Estrutura pirâmide invertida + intertítulos
    """
    title = article.get('title', '')[:60]
    logger.info(f"[REWRITE] Reescrevendo (PROFISSIONAL): {title}...")
    
    try:
        category = article.get('category', 'general')
        reporters = load_reporters_config()
        # encontra repórter pela role ou fallback
        reporter = None
        for r in reporters.values():
            if r.role == category:
                reporter = r
                break
        if not reporter:
            reporter = list(reporters.values())[0]

        # 1. Busca fontes relacionadas para cruzamento
        related = _find_related_sources(article, max_related=3)
        if related:
            logger.info(f"[REWRITE] {len(related)} fontes relacionadas encontradas para cruzamento")
            article["related_sources"] = related

        # 2. Tenta Gemini/OpenAI com prompt profissional enxuto
        llm = LLMClient()
        if llm.api_key:
            system_prompt = reporter.get_system_prompt()
            attribution = reporter.attribution
            result = llm.rewrite_article(article, system_prompt, attribution, related_sources=related)
            rewritten_content = result.get("rewritten_content", "")
            # valida tamanho profissional longo (700-900 ideal, 700 mínimo)
            if rewritten_content and len(rewritten_content.split()) >= 700:
                logger.info(f"[REWRITE] LLM OK — {len(rewritten_content.split())} palavras")
                # monta artigo final profissional
                final = {
                    "title": article.get("title", ""),
                    "content": rewritten_content,
                    "summary": article.get("summary", "")[:300],
                    "source_urls": [article.get("url", "")] + [r.get("url","") for r in related],
                    "source_names": [source_name_from_url(article.get("url",""))] + [source_name_from_url(r.get("url","")) for r in related],
                    "reporter_slug": reporter.slug,
                    "reporter_name": reporter.display_name,
                    "category": reporter.role,
                    "attribution": attribution,
                    "original_summary": article.get("summary", ""),
                    "rewritten_at": result.get("rewritten_at"),
                    "word_count": len(rewritten_content.split()),
                    "related_count": len(related),
                    "llm_provider": llm.provider,
                    "llm_model": llm.model,
                }
                # publica
                from app.tasks.publish_tasks import publish_single_article
                # garante compatibilidade com publisher
                final["sources"] = final["source_urls"]
                final["content"] = rewritten_content
                pub = publish_single_article(final)
                logger.info(f"[REWRITE] Publicado (LLM profissional): {pub.get('article_id')}")
                return pub
            else:
                logger.warning(f"[REWRITE] LLM gerou conteúdo curto ({len(rewritten_content.split()) if rewritten_content else 0} palavras)")

        logger.warning(f"[REWRITE] LLM indisponivel ou curto demais para '{title}' — falhando sem fallback local")
        raise RuntimeError("Reescrita indisponível sem LLM")
        
    except Exception as e:
        logger.error(f"[REWRITE] Erro: {e}")
        raise self.retry(exc=e)
