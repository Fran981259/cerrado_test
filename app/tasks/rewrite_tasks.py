"""
Tarefas de Reescrita — Atualiza Brasil
VERSÃO PROFISSIONAL: matérias longas (700-900 palavras) + cruzamento de fontes.
"""

from app.celery_app import celery_app
from app.rewriter import load_reporters_config
from app.groq_client import GroqClient
from app.scanner import RealPortalScanner
import logging
import re

logger = logging.getLogger(__name__)


def groq_client_source_name(url: str) -> str:
    if 'msnews.com.br' in url:
        return 'MS News'
    elif 'mstododia.com.br' in url:
        return 'MS Todo Dia'
    elif 'agenciadenoticias.ms.gov.br' in url:
        return 'Agência de Notícias MS'
    elif 'oestadoonline.com.br' in url:
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
                        "source": groq_client_source_name(urls[0] if urls else ""),
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
    Reescreve artigos em status 'classified' com LLM (Groq) ou fallback local,
    gravando o conteúdo e marcando-os como 'rewritten'.
    Roda a cada 30 minutos.
    """
    logger.info("[REWRITE] Iniciando reescrita de artigos classificados (profissional)")

    from app.database import get_session
    from app.schema import NewsArticle, Reporter
    from app.rewriter import load_reporters_config, ArticleRewriter
    from datetime import datetime

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
        groq = GroqClient()

        for art in articles:
            try:
                if not art.sources:
                    art.status = "failed"
                    art.updated_at = datetime.utcnow()
                    failed += 1
                    continue

                main_url = art.sources[0]["url"] if isinstance(art.sources, list) and art.sources else ""
                main_source = groq_client_source_name(main_url)

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
                if groq.api_key:
                    result_groq = groq.rewrite_article(
                        article_data,
                        reporter.get_system_prompt(),
                        reporter.attribution,
                        related_sources=related,
                    )
                    candidate = result_groq.get("rewritten_content", "")
                    if candidate and len(candidate.split()) >= 500:
                        content = candidate

                if not content:
                    fallback_rewriter = ArticleRewriter(reporter)
                    fallback = fallback_rewriter.rewrite(article_data)
                    content = fallback.get("content", "")

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
    Reescreve um único artigo com padrão PROFISSIONAL:
    - 700-900 palavras
    - Cruzamento com 2-3 fontes do mesmo fato
    - Estrutura lead → contexto → desenvolvimento → análise MS → fechamento
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

        # 2. Tenta Groq com prompt profissional longo
        groq = GroqClient()
        if groq.api_key:
            system_prompt = reporter.get_system_prompt()
            attribution = reporter.attribution
            result = groq.rewrite_article(article, system_prompt, attribution, related_sources=related)
            rewritten_content = result.get("rewritten_content", "")
            # valida tamanho mínimo profissional (700 ideal, 500 mínimo aceitável)
            if rewritten_content and len(rewritten_content.split()) >= 500:
                logger.info(f"[REWRITE] Groq OK — {len(rewritten_content.split())} palavras")
                # monta artigo final profissional
                final = {
                    "title": article.get("title", ""),
                    "content": rewritten_content,
                    "summary": article.get("summary", "")[:300],
                    "source_urls": [article.get("url", "")] + [r.get("url","") for r in related],
                    "source_names": [groq_client_source_name(article.get("url",""))] + [groq_client_source_name(r.get("url","")) for r in related],
                    "reporter_slug": reporter.slug,
                    "reporter_name": reporter.display_name,
                    "category": reporter.role,
                    "attribution": attribution,
                    "original_summary": article.get("summary", ""),
                    "rewritten_at": result.get("rewritten_at"),
                    "word_count": len(rewritten_content.split()),
                    "related_count": len(related),
                    "llm_provider": "groq",
                    "llm_model": groq.model,
                }
                # publica
                from app.tasks.publish_tasks import publish_single_article
                # garante compatibilidade com publisher
                final["sources"] = final["source_urls"]
                final["content"] = rewritten_content
                pub = publish_single_article(final)
                logger.info(f"[REWRITE] Publicado (Groq profissional): {pub.get('article_id')}")
                return pub
            else:
                logger.warning(f"[REWRITE] Groq gerou conteúdo curto ({len(rewritten_content.split()) if rewritten_content else 0} palavras), usando fallback profissional")

        # 3. Fallback: rewriter local profissional (sem LLM)
        from app.rewriter import ArticleRewriter
        rewriter = ArticleRewriter(reporter)
        fallback = rewriter.rewrite(article)
        # garante publicação mesmo sem Groq
        from app.tasks.publish_tasks import publish_single_article
        fallback["sources"] = fallback.get("source_urls", [])
        fallback["content"] = fallback.get("content", "")
        result = publish_single_article(fallback)
        logger.info(f"[REWRITE] Publicado (fallback profissional): {result.get('article_id')}")
        return result
        
    except Exception as e:
        logger.error(f"[REWRITE] Erro: {e}")
        raise self.retry(exc=e)
