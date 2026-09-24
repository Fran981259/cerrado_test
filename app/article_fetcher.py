"""
Fetcher de Artigos de Alta Qualidade — Portal Cerrado
Extrai a PÁGINA REAL de cada matéria (não apenas o card da listagem):
- título limpo (JSON-LD / OG / h1)
- lead/resumo (meta description / JSON-LD)
- CORPO COMPLETO do texto (JSON-LD articleBody / <article> / main)
- data de publicação, autor e imagem
- limpeza de ruído (menu, "leia mais", prefixos repetidos, texto oculto)
"""

import logging
import re
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from app.article_body import ArticleBodyMixin
from app.article_metadata import ArticleMetadataMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleFetcher(ArticleMetadataMixin, ArticleBodyMixin):
    """Baixa e extrai conteúdo completo de uma página de notícia."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    TIMEOUT = 20
    # Parágrafos com estas situações são ruído/boilerplate
    _BOILERPLATE = re.compile(
        r"(leia mais|leia também|veja também|veja mais|saiba mais|"
        r"compartilhe|publicidade|anúncio|anuncie|assinante|clique aqui|"
        r"acompanhe o|siga o|newsletter|redes sociais|notícias ao vivo|"
        r"última atualização|escrito por|por redação|siga nosso)",
        re.IGNORECASE,
    )

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    # ----------------------------------------------------------
    # Ponto de entrada
    # ----------------------------------------------------------
    def fetch(self, url: str, base_summary: str = "") -> Dict:
        """
        Baixa `url` e retorna um artigo limpo:
        {title, lead, content, published_at, author, image_url, url, status}
        Retorna status 'failed' em caso de erro; nunca lança.
        """
        # Enforce robots.txt for article URL
        try:
            from app.robots import is_allowed

            if not is_allowed(url):
                logger.warning(f"[ROBOTS] Artigo bloqueado por robots.txt: {url}")
                return {"status": "blocked", "url": url, "reason": "robots.txt disallow"}
        except Exception as e:
            logger.debug(f"[ROBOTS] check falhou para {url}: {e}")
        try:
            resp = self.session.get(url, timeout=self.TIMEOUT, allow_redirects=True)
            resp.raise_for_status()
            # Evita mojibake (Ã£): quando o servidor omite o charset, o requests
            # assume latin1 e corrompe acentos — usa detecção real nesses casos
            ctype = resp.headers.get("Content-Type", "")
            if "charset" not in ctype.lower() or "iso-8859-1" in ctype.lower():
                resp.encoding = resp.apparent_encoding or "utf-8"
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")

            # remove elementos de ruído antes de qualquer extração
            jsonld = self._extract_jsonld(soup)
            self._strip_noise(soup)
            title = self._clean_text(
                self._pick_first(
                    self._meta(soup, ["og:title"]),
                    (jsonld or {}).get("headline"),
                    self._text(soup, "h1"),
                    self._text(soup, "title"),
                )
            )

            lead = self._clean_text(
                self._pick_first(
                    self._meta(soup, ["description", "og:description", "twitter:description"]),
                    (jsonld or {}).get("description"),
                    base_summary,
                )
            )

            content = self._extract_body(soup, jsonld)
            if not content.strip():
                # fallback: reconstrói parágrafos do documento principal
                content = self._paragraph_fallback(soup)

            published_at = self._extract_date(soup, jsonld)
            author = self._extract_author(soup, jsonld)
            image_url = self._extract_image(soup, jsonld, url)

            # título final: se o título vier poluído por prefixo da categoria,
            # tenta a melhor versão (JSON-LD já costuma estar limpo)
            title = self._dedupe_title(title)

            # lead de alto nível: deriva do corpo real quando o meta é genérico/sujo
            # ou quando o conteúdo oferece lead mais específico que o meta
            if content and len(content) > 100:
                # encontra primeiro parágrafo significativo (pula datas/cabeçalhos)
                paras = [p for p in content.split("\n\n") if p.strip()]
                meaningful = None
                for p in paras:
                    if re.match(r"^\s*\d{1,2}/", p) and len(p.split()) < 10:
                        continue  # data tipo "28/agosto/2026 3:17 pm"
                    if len(p.split()) >= 12:
                        meaningful = p
                        break
                if meaningful:
                    m = re.search(r"^(.+?[.!?])\s", meaningful)
                    candidate = m.group(1) if m else meaningful[:400]
                    candidate = self._clean_text(candidate)
                    # substitui se o lead atual é sujo/genérico ou o candidato é claramente melhor
                    if self._is_dirty_lead(lead) or self._is_generic_lead(lead) or len(candidate) > len(lead) * 0.7:
                        if len(candidate.split()) >= 8:
                            # só substitui se não for genérico também
                            if not self._is_generic_lead(candidate):
                                lead = candidate

            return {
                "status": "success",
                "title": title[:300],
                "lead": lead[:1000],
                "content": content,
                "published_at": published_at,
                "author": author,
                "image_url": image_url,
                "url": url,
            }

        except requests.exceptions.RequestException as e:
            logger.debug(f"[FETCH] falha de rede em {url}: {e}")
        except Exception as e:
            logger.debug(f"[FETCH] erro em {url}: {e}")
        return {"status": "failed", "url": url}

    # ----------------------------------------------------------
