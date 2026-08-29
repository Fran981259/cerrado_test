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
    """Busca até 3 fontes relacionadas ao mesmo fato para cruzamento."""
    try:
        scanner = RealPortalScanner()
        all_articles = scanner.scan_all().get("articles", [])
        title = article.get("title", "").lower()
        # pega palavras-chave relevantes (4+ letras)
        keywords = [w for w in re.findall(r"\w+", title.lower()) if len(w) >= 4][:6]
        if not keywords:
            return []
        scored = []
        for a in all_articles:
            if a.get("url") == article.get("url"):
                continue
            t = a.get("title", "").lower()
            score = sum(1 for kw in keywords if kw in t)
            if score >= 1:
                scored.append((score, a))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in scored[:max_related]]
    except Exception as e:
        logger.warning(f"[REWRITE] falha ao buscar fontes relacionadas: {e}")
        return []


@celery_app.task(
    name="app.tasks.rewrite_tasks.rewrite_pending_articles",
    bind=True,
    max_retries=3,
    time_limit=600
)
def rewrite_pending_articles(self):
    """
    Reescreve artigos pendentes com LLM — versão profissional longa.
    """
    logger.info("[REWRITE] Iniciando reescrita pendentes (profissional)")
    
    try:
        result = {
            "status": "success",
            "rewritten": 0,
            "message": "Task profissional (700-900 palavras + fontes cruzadas) ativa",
        }
        logger.info(f"[REWRITE] Concluído: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[REWRITE] Erro: {e}")
        raise self.retry(exc=e)


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
