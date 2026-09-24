"""Metadados, ruído e imagens da extração de artigos."""

import json
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup


class ArticleMetadataMixin:
    """Extrai metadados e imagens, mantendo o fetcher focado na orquestração."""

    # Remoção de ruído / boilerplate no DOM
    # ----------------------------------------------------------
    def _strip_noise(self, soup: BeautifulSoup) -> None:
        for tag in soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "header",
                "footer",
                "aside",
                "form",
                "iframe",
                "svg",
                "button",
                "ad",
                "ins",
            ]
        ):
            tag.decompose()
        for sel in [
            ".advertisement",
            ".ads",
            ".ad",
            ".banner",
            ".menu",
            ".footer",
            ".header",
            ".sidebar",
            ".related",
            ".comments",
            ".share",
            ".social",
            ".newsletter",
            ".tags",
            "figcaption",
        ]:
            for el in soup.select(sel):
                el.decompose()

    # ----------------------------------------------------------
    # Metadados
    # ----------------------------------------------------------
    def _meta(self, soup: BeautifulSoup, names: List[str]) -> Optional[str]:
        for name in names:
            el = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
            if el and el.get("content"):
                return str(el["content"])
        return None

    def _text(self, soup: BeautifulSoup, selector: str) -> str:
        el = soup.select_one(selector)
        return el.get_text(" ", strip=True) if el else ""

    def _extract_jsonld(self, soup: BeautifulSoup) -> Optional[Dict]:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
            except Exception:
                continue
            if isinstance(data, list):
                data = next((d for d in data if isinstance(d, dict)), None)
            if isinstance(data, dict):
                if data.get("@type") == "NewsArticle" or data.get("headline") or data.get("articleBody"):
                    return data
                # itemList -> primeiro item pode ser notícia
                if data.get("@type") == "ItemList" and isinstance(data.get("itemListElement"), list):
                    first = next(iter(data["itemListElement"]), None)
                    if isinstance(first, dict):
                        return first
        return None

    def _extract_date(self, soup: BeautifulSoup, jsonld: Optional[Dict]) -> Optional[str]:
        val = self._meta(soup, ["article:published_time", "datePublished", "pubdate"])
        if val:
            return val
        if jsonld and jsonld.get("datePublished"):
            return jsonld["datePublished"]
        if jsonld and jsonld.get("dateModified"):
            return jsonld["dateModified"]
        time_el = soup.find("time")
        if time_el and time_el.get("datetime"):
            return str(time_el["datetime"])
        return None

    def _extract_author(self, soup: BeautifulSoup, jsonld: Optional[Dict]) -> Optional[str]:
        if jsonld and jsonld.get("author"):
            a = jsonld["author"]
            if isinstance(a, dict):
                return a.get("name")
            if isinstance(a, list):
                return ", ".join(x.get("name", "") for x in a if isinstance(x, dict))
            return str(a)
        for sel in [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'a[rel="author"]',
            ".author a",
            ".byline",
            ".autor",
        ]:
            try:
                el = soup.select_one(sel)
            except Exception:
                el = None
            if el and (el.get("content") or el.get_text(strip=True)):
                content = el.get("content")
                return str(content) if content else el.get_text(strip=True)
        # fallback via find
        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find(
            "meta", attrs={"property": "article:author"}
        )
        if meta_author and meta_author.get("content"):
            return str(meta_author["content"])
        return None

    def _extract_image(self, soup: BeautifulSoup, jsonld: Optional[Dict], page_url: str = "") -> Optional[str]:
        # 1) og:image / twitter:image via meta
        for key in ["og:image", "twitter:image", "twitter:image:src"]:
            val = self._meta(soup, [key])
            if val and self._is_valid_image_url(val):
                return self._abs_url(val, page_url)
        # 1b) link rel="image_src"
        link = soup.find("link", rel="image_src")
        href = link.get("href") if link else None
        if href and self._is_valid_image_url(str(href)):
            return self._abs_url(str(href), page_url)
        # 2) JSON-LD
        if jsonld and jsonld.get("image"):
            img = jsonld["image"]
            if isinstance(img, dict):
                val = img.get("url")
            elif isinstance(img, list):
                first = img[0]
                val = first.get("url") if isinstance(first, dict) else str(first)
            else:
                val = str(img)
            if val and self._is_valid_image_url(val):
                return self._abs_url(val, page_url)
        # 3) Maior imagem dentro do conteúdo principal (evita repetição de placeholder)
        # Tenta área principal primeiro: #single, article com mais texto, main
        candidates_containers = []
        single = soup.find(id="single")
        if single:
            candidates_containers.append(single)
        # artigo com mais palavras
        articles = soup.find_all("article")
        if articles:
            best_article = max(articles, key=lambda a: len(a.get_text(" ", strip=True).split()), default=None)
            if best_article:
                candidates_containers.append(best_article)
        for sel in ["main", ".entry-content", ".post-content", ".article-content", ".single-content", ".conteudo"]:
            el = soup.select_one(sel)
            if el:
                candidates_containers.append(el)
        # coleta imgs desses containers primeiro
        for container in candidates_containers:
            for img in container.find_all("img"):
                src = self._img_src(img)
                if src and self._is_valid_image_url(src):
                    return self._abs_url(src, page_url)
            # background-image em divs dentro do container
            for el in container.find_all(style=re.compile(r"background-image", re.I)):
                m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", str(el.get("style", "")))
                if m and self._is_valid_image_url(m.group(1)):
                    return self._abs_url(m.group(1), page_url)
        # 4) fallback global: primeira imagem válida na página que não seja ícone
        for img in soup.find_all("img"):
            src = self._img_src(img)
            if src and self._is_valid_image_url(src):
                return self._abs_url(src, page_url)
        return None

    def _img_src(self, img) -> Optional[str]:
        for attr in ["src", "data-src", "data-lazy-src", "data-original"]:
            v = img.get(attr)
            if v and v.strip() and not v.strip().startswith("data:"):
                return v.strip()
        # srcset: pega primeira URL
        srcset = img.get("srcset") or img.get("data-srcset")
        if srcset:
            first = srcset.split(",")[0].strip().split(" ")[0]
            if first:
                return first
        return None

    def _is_valid_image_url(self, url: str) -> bool:
        if not url or url.startswith("data:"):
            return False
        low = url.lower()
        # descarta ícones, logos, placeholders, tracking pixels e genéricos repetidos
        bad = [
            "icone",
            "icon",
            "logo",
            "placeholder",
            "avatar",
            "sprite",
            "pixel",
            "blank",
            "facebook.png",
            "instagram.png",
            "twitter.png",
            "youtube.png",
            "tiktok",
            "brasao",
            "fb_marca",
            "fb_",
            "default",
            "no-image",
            "sem-imagem",
        ]
        if any(b in low for b in bad):
            return False
        # deve parecer imagem
        if (
            not re.search(r"\.(jpg|jpeg|png|webp|avif)(\?|$|#)", low)
            and "wp-content/uploads" not in low
            and "image" not in low
        ):
            # permite urls sem extensão mas com padrão de CDN de imagem
            if not re.search(r"/(img|image|foto|thumb|media)/", low):
                return False
        return True

    def _abs_url(self, url: str, base: str) -> str:
        if url.startswith("http"):
            return url
        if url.startswith("//"):
            return "https:" + url
        if base and url.startswith("/"):
            return urljoin(base, url)
        return url

    # ----------------------------------------------------------
