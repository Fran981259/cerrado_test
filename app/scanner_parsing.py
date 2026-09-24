"""Métodos de coleta e parsing do scanner."""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScannerArticleMethods:
    """Implementa a coleta e o parsing de artigos de um portal."""
    session: requests.Session
    REPORTER_BY_CATEGORY: dict
    CATEGORY_KEYWORDS: dict
    def _scan_portal(self, portal: Dict) -> Dict:
        """Escaneia um portal específico."""
        name = portal["name"]
        url = portal["url"]
        logger.info(f"Escaneando: {name} ({url})")
        # Enforce robots.txt at runtime (cached, re-check daily)
        try:
            from app.robots import is_allowed
            if not is_allowed(url):
                logger.warning(f"[ROBOTS] Bloqueado por robots.txt: {url}")
                return {"name": name, "url": url, "status": "blocked", "error": "robots.txt disallow", "articles": []}
        except Exception as e:
            logger.debug(f"[ROBOTS] check falhou para {url}: {e}")
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            # Anti-mojibake: charset ausente => requests chuta latin1 e quebra acentos
            ctype = response.headers.get("Content-Type", "")
            if "charset" not in ctype.lower() or "iso-8859-1" in ctype.lower():
                response.encoding = response.apparent_encoding or "utf-8"
            soup = BeautifulSoup(response.content, "html.parser")
            articles = self._extract_articles(soup, portal, url)
            return {
                "name": name,
                "url": url,
                "status": "success",
                "articles_count": len(articles),
                "articles": articles,
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Falha em {name}: {e}")
            return {
                "name": name,
                "url": url,
                "status": "failed",
                "error": str(e),
                "articles": [],
            }
    def _extract_articles(self, soup: BeautifulSoup, portal: Dict, base_url: str) -> List[Dict]:
        """Extrai artigos do HTML."""
        articles: List[Dict] = []
        seen_urls = set()
        candidates: List[Any] = []
        candidates.extend(soup.find_all("article"))
        candidates.extend(soup.find_all(["h2", "h3"]))
        candidates.extend(soup.find_all("div", class_=re.compile(r"noticia|post|news|article|item", re.I)))
        for element in candidates:
            article = self._parse_element(element, portal, base_url)
            if article and article["url"] not in seen_urls:
                if self._is_valid_article(article):
                    articles.append(article)
                    seen_urls.add(article["url"])
                    if len(articles) >= 25:
                        break
        return articles
    def _parse_element(self, element, portal: Dict, base_url: str) -> Optional[Dict]:
        """Parseia um elemento HTML em artigo."""
        try:
            if element.name in ["h2", "h3"]:
                link = element.find("a")
                if not link:
                    parent = element.parent
                    if parent:
                        link = parent.find("a")
                title = element.get_text(strip=True)
            else:
                link = element.find("a")
                title_elem = element.find(["h1", "h2", "h3", "h4"])
                if not title_elem:
                    title_elem = element.find("a")
                title = title_elem.get_text(strip=True) if title_elem else ""
            if not link or not link.get("href"):
                return None
            if not title or len(title) < 10:
                return None
            href = link["href"].strip()
            if href.startswith(("http://", "https://")):
                pass
            elif href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = urljoin(base_url, href)
            elif re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_\-./?=&%#]*$", href):
                # relativa sem barra inicial ("noticias/123-titulo")
                href = urljoin(base_url.rstrip("/") + "/", href)
            else:
                return None
            if any(
                skip in href.lower()
                for skip in [
                    "/login",
                    "/cadastro",
                    "/contato",
                    "/sobre",
                    "/privacy",
                    "/termos",
                    "/search",
                    "/feed",
                    "/rss",
                ]
            ):
                return None
            category = self._classify(title)
            reporter = self.REPORTER_BY_CATEGORY.get(category, "enzo.bianchi")
            summary = self._extract_summary(element)
            return {
                "title": title[:300],
                "summary": summary,
                "url": href,
                "source": portal["name"],
                "source_url": portal["url"],
                "category": category,
                "region": portal.get("region", "ms"),
                "reporter_slug": reporter,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception:
            return None
    def _extract_summary(self, element) -> str:
        """Extrai o summary/resumo do artigo."""
        text_parts = []
        for p in element.find_all(["p", "span", "div"]):
            text = p.get_text(strip=True)
            if 50 < len(text) < 300:
                text_parts.append(text)
        return " ".join(text_parts[:2])[:500] if text_parts else ""
    def _classify(self, title: str) -> str:
        """Classifica um artigo por categoria usando word boundaries."""
        import re
        title_lower = title.lower()
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Usa word boundary para evitar "ia" em "entre", "campo" em "comportamento", etc.
                pattern = r"\b" + re.escape(kw.lower()) + r"\b"
                if re.search(pattern, title_lower):
                    score += 1
            if score > 0:
                scores[category] = score
        if scores:
            best_category = max(scores, key=lambda c: scores[c])
            return best_category
        return "general"
    def _is_valid_article(self, article: Dict) -> bool:
        """Valida se é um artigo válido — filtro anti-lixo para AdSense."""
        title = (article.get("title", "") or "").strip()
        url = (article.get("url", "") or "").strip()
        if len(title) < 20:
            return False
        if len(title.split()) < 4:
            return False
        if not url.startswith("http"):
            return False
        title_lower = title.lower().strip()
        url_lower = url.lower()
        # 1) Títulos genéricos / placeholders (reprovam AdSense)
        invalid_exact = {
            "o estado online",
            "ms news",
            "ms todo dia",
            "agência de notícias ms",
        }
        if title_lower in invalid_exact:
            return False
        invalid_contains = [
            "últimas notícias",
            "última hora",
            "breaking news",
            "notícias ao vivo",
            "para o servidor",
            "contato",
            "sobre nós",
            "política de privacidade",
            "termos de uso",
            "cadastro",
            "login",
            "registro",
            "newsletter",
            "edição anterior",
            "arquivo",
            "search",
            "pesquisa",
            "search result",
            "click here",
            "saiba mais",
            "leia mais",
            "veja também",
            "veja mais",
            "voltar",
            "anterior",
            "próximo",
            "next",
            "previous",
            "veja notícias em campo grande",
            "últimas notícias de economia",
            "o jornal que respeita seus leitores",
            "mercedita e serenatas",  # placeholder cultural poluído
        ]
        if any(inv in title_lower for inv in invalid_contains):
            return False
        # 2) Título muito curto ou igual ao nome do portal
        if len(title.split()) < 4:
            return False
        # 3) URLs de listagem / homepage / artefatos do portal
        skip_url_substrings = [
            "javascript:",
            "mailto:",
            "#",
            "/search",
            "/login",
            "/signup",
            "/register",
            "/feed",
            "/rss",
            "/podcast",
            "/video",
            "/author",
            "/sobre",
            "/contato",
            "/privacy",
            "/termos",
            "/cadastro",
            "/homepage-nova",
            "/arte-e-lazer/mercedita",
            "/tag/",
            "/categoria/",
            "/author/",
            "/page/",
            "?s=",
            "?p=",
        ]
        if any(p in url_lower for p in skip_url_substrings):
            return False
        # 4) Homepage raiz sem slug profundo (ex: https://oestadoonline.com.br/)
        # exige pelo menos 2 segmentos após domínio para ser matéria
        try:
            path = urlparse(url).path.strip("/")
            if not path or path.count("/") < 1:
                # allow agência ms que tem slug com 1 segmento mas longo
                if len(path) < 15:
                    return False
        except Exception:
            return False
        # 5) Repetição grosseira de palavras (falha de scraping)
        # ex: "O Estado Online O Estado Online"
        words = title_lower.split()
        if len(words) >= 4 and len(set(words)) <= 2:
            return False
        return True
