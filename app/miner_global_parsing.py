"""Parsing e filtros de feeds RSS do minerador global."""

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalNewsParsingMixin:
    config: Dict[str, Any]
    session: httpx.Client

    # GOOGLE NEWS RSS (pt-BR / Brasil)
    # ----------------------------------------------------------
    def mine_google_news(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Descoberta de pauta via Google News RSS (títulos + veículo + data).

        Os links do Google News são tokens criptografados (CBMi): tenta-se
        resolver para o publisher via HEAD; se não resolver, mantém o link
        do Google e o pipeline tenta apurar (fetch_miss é tolerado).
        """
        out: List[Dict[str, Any]] = []
        searches = self.config.get("global_miner", {}).get("google_news", [])
        for search in searches:
            rss_url = search.get("rss", "")
            category = search.get("category", "general")
            if not rss_url:
                continue
            if search.get("respect_robots", True):
                try:
                    from app.robots import is_allowed

                    if not is_allowed(rss_url):
                        logger.warning(f"[ROBOTS] Google News bloqueado: {search.get('name')}")
                        continue
                except Exception:
                    pass
            try:
                # Google redireciona /headlines/section/topic/* para a URL canônica
                response = self.session.get(rss_url, follow_redirects=True)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
                for entry in feed.entries[:limit]:
                    article = self._parse_gnews_entry(entry, search, category)
                    if article and self._is_relevant(article):
                        out.append(article)
                logger.info(f"[GNEWS] {search.get('name')}: {len(feed.entries)} no feed")
            except Exception as e:
                logger.error(f"[GNEWS] erro em {search.get('name')}: {e}")
        logger.info(f"[GNEWS] total aproveitado: {len(out)} artigos")
        return out

    def _resolve_google_url(self, url: str) -> str:
        """Tenta resolver o link criptografado para o publisher real."""
        try:
            r = self.session.head(url, follow_redirects=True, timeout=10)
            final = str(r.url)
            if "news.google.com" not in final:
                return final
        except Exception:
            pass
        return url

    def _parse_gnews_entry(self, entry, search: Dict, category: str) -> Optional[Dict]:
        try:
            title = entry.get("title", "").strip()
            if not title:
                return None
            link = entry.get("link", "")
            src = entry.get("source") or {}
            publisher = (src.get("title") or "").strip() or "Google News"
            resolved = self._resolve_google_url(link) if link else link
            summary = self._clean_html(entry.get("summary", entry.get("description", "")))
            published = entry.get("published", entry.get("updated", ""))
            article = {
                "title": title,
                "url": resolved,
                "summary": summary[:1500],
                "source": publisher,
                "source_url": (src.get("href") or "").strip() or "https://news.google.com",
                "source_lang": "pt-BR",
                "category": category,
                "image_url": self._extract_image(entry),
                "published_at": self._parse_date(published),
                "mined_at": datetime.now(timezone.utc).isoformat(),
                "hash": hashlib.md5(link.encode()).hexdigest(),
                "requires_translation": False,
                "origin": "google_news",
            }
            return article
        except Exception as e:
            logger.error(f"[GNEWS] erro ao parsear: {e}")
            return None

    def _mine_portal(self, portal: Dict, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Coleta artigos de um portal via RSS com limite variável."""
        articles: List[Dict[str, Any]] = []
        rss_url = portal.get("rss")
        if not rss_url:
            return articles

        # Enforce robots.txt for RSS URL (opt-out permitido por busca, ex: Google News RSS)
        if portal.get("respect_robots", True):
            try:
                from app.robots import is_allowed

                if not is_allowed(rss_url):
                    logger.warning(f"[ROBOTS] RSS bloqueado por robots.txt: {rss_url}")
                    return articles
            except Exception as e:
                logger.debug(f"[ROBOTS] check falhou para {rss_url}: {e}")

        try:
            response = self.session.get(rss_url)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            entries = feed.entries[:limit]

            for entry in entries:
                article = self._parse_entry(entry, portal, category)
                if article and self._is_relevant(article):
                    articles.append(article)

        except Exception as e:
            logger.error(f"Erro ao coletar RSS de {portal['name']}: {e}")

        return articles

    def _parse_entry(self, entry, portal: Dict, category: str) -> Optional[Dict]:
        try:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            published = entry.get("published", entry.get("updated", ""))

            summary = self._clean_html(summary)
            image_url = self._extract_image(entry)
            source_lang = self._detect_language(title + " " + summary)

            article = {
                "title": title,
                "url": link,
                "summary": summary[:1500],
                "source": portal["name"],
                "source_url": portal["url"],
                "source_lang": source_lang,
                "category": category,
                "region": "global",
                "image_url": image_url,
                "published_at": self._parse_date(published),
                "mined_at": datetime.now(timezone.utc).isoformat(),
                "hash": hashlib.md5(link.encode()).hexdigest(),
                "requires_translation": source_lang != "pt-BR",
            }

            return article

        except Exception as e:
            logger.error(f"Erro ao parsear: {e}")
            return None

    def _clean_html(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_image(self, entry) -> Optional[str]:
        if hasattr(entry, "media_content") and entry.media_content:
            return entry.media_content[0].get("url")
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    return enc.get("url")
        if hasattr(entry, "links"):
            for link in entry.links:
                if link.get("type", "").startswith("image/"):
                    return link.get("href")
        return None

    def _detect_language(self, text: str) -> str:
        common_en = ["the", "and", "is", "in", "to", "of", "a", "that", "it", "for"]
        common_pt = ["o", "a", "e", "é", "de", "do", "da", "que", "para", "com"]

        text_lower = text.lower()
        en_count = sum(1 for w in common_en if f" {w} " in f" {text_lower} ")
        pt_count = sum(1 for w in common_pt if f" {w} " in f" {text_lower} ")

        return "en" if en_count > pt_count else "pt-BR"

    def _parse_date(self, date_str: str) -> str:
        if not date_str:
            return datetime.now(timezone.utc).isoformat()

        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%a, %d %b %Y %H:%M:%S %z",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue

        return datetime.now(timezone.utc).isoformat()

    def _is_relevant(self, article: Dict) -> bool:
        filters = self.config.get("global_miner", {}).get("relevance_filters", {})
        title_lower = article["title"].lower()
        summary_lower = article["summary"].lower()
        combined = title_lower + " " + summary_lower

        # Google News: já vem em pt-BR, com busca direcionada e veículo —
        # relevante por construção (o filtro de qualidade/dedup vem depois)
        if article.get("origin") == "google_news" and article.get("source"):
            return True

        brazil_kw = filters.get("brazil_keywords", [])
        for kw in brazil_kw:
            if kw.lower() in combined:
                return True

        category = article["category"]
        if category in ["technology", "economy", "geopolitics", "health", "science_health"]:
            cat_kw = filters.get("global_keywords", {}).get(category, [])
            for kw in cat_kw:
                if re.search(r"\b" + re.escape(kw.lower()) + r"\b", combined):
                    return True

        if category == "sports_global":
            return True

        return False
