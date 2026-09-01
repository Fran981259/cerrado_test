"""
Fetcher de Artigos de Alta Qualidade — Atualiza Brasil
Extrai a PÁGINA REAL de cada matéria (não apenas o card da listagem):
- título limpo (JSON-LD / OG / h1)
- lead/resumo (meta description / JSON-LD)
- CORPO COMPLETO do texto (JSON-LD articleBody / <article> / main)
- data de publicação, autor e imagem
- limpeza de ruído (menu, "leia mais", prefixos repetidos, texto oculto)
"""

import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleFetcher:
    """Baixa e extrai conteúdo completo de uma página de notícia."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
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
            html = resp.text
            soup = BeautifulSoup(html, "html.parser")

            # remove elementos de ruído antes de qualquer extração
            self._strip_noise(soup)

            jsonld = self._extract_jsonld(soup)
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
    # Remoção de ruído / boilerplate no DOM
    # ----------------------------------------------------------
    def _strip_noise(self, soup: BeautifulSoup) -> None:
        for tag in soup.find_all(
            ["script", "style", "noscript", "nav", "header", "footer", "aside",
             "form", "iframe", "svg", "button", "ad", "ins"]
        ):
            tag.decompose()
        for sel in [".advertisement", ".ads", ".ad", ".banner", ".menu",
                    ".footer", ".header", ".sidebar", ".related", ".comments",
                    ".share", ".social", ".newsletter", ".tags", "figcaption"]:
            for el in soup.select(sel):
                el.decompose()

    # ----------------------------------------------------------
    # Metadados
    # ----------------------------------------------------------
    def _meta(self, soup: BeautifulSoup, names: List[str]) -> Optional[str]:
        for name in names:
            el = soup.find("meta", attrs={"property": name}) or soup.find(
                "meta", attrs={"name": name}
            )
            if el and el.get("content"):
                return el["content"]
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
            return time_el["datetime"]
        return None

    def _extract_author(self, soup: BeautifulSoup, jsonld: Optional[Dict]) -> Optional[str]:
        if jsonld and jsonld.get("author"):
            a = jsonld["author"]
            if isinstance(a, dict):
                return a.get("name")
            if isinstance(a, list):
                return ", ".join(x.get("name", "") for x in a if isinstance(x, dict))
            return str(a)
        for sel in ['meta[name="author"]', 'meta[property="article:author"]',
                    'a[rel="author"]', ".author a", ".byline", ".autor"]:
            try:
                el = soup.select_one(sel)
            except Exception:
                el = None
            if el and (el.get("content") or el.get_text(strip=True)):
                return el.get("content") or el.get_text(strip=True)
        # fallback via find
        meta_author = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
        if meta_author and meta_author.get("content"):
            return meta_author["content"]
        return None

    def _extract_image(self, soup: BeautifulSoup, jsonld: Optional[Dict], page_url: str = "") -> Optional[str]:
        # 1) og:image / twitter:image via meta
        for key in ["og:image", "twitter:image", "twitter:image:src"]:
            val = self._meta(soup, [key])
            if val and self._is_valid_image_url(val):
                return self._abs_url(val, page_url)
        # 1b) link rel="image_src"
        link = soup.find("link", rel="image_src")
        if link and link.get("href") and self._is_valid_image_url(link["href"]):
            return self._abs_url(link["href"], page_url)
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
                m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", el.get("style", ""))
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
        bad = ["icone", "icon", "logo", "placeholder", "avatar", "sprite", "pixel", "blank",
               "facebook.png", "instagram.png", "twitter.png", "youtube.png", "tiktok", "brasao",
               "fb_marca", "fb_", "default", "no-image", "sem-imagem"]
        if any(b in low for b in bad):
            return False
        # deve parecer imagem
        if not re.search(r"\.(jpg|jpeg|png|webp|avif)(\?|$|#)", low) and "wp-content/uploads" not in low and "image" not in low:
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
    # Corpo do texto
    # ----------------------------------------------------------
    def _extract_body(self, soup: BeautifulSoup, jsonld: Optional[Dict]) -> str:
        # 1) JSON-LD articleBody (fonte mais confiável)
        if jsonld and jsonld.get("articleBody"):
            body = self._clean_text(jsonld["articleBody"])
            if len(body.split()) >= 30:
                return body

        # 2) Heurística: container com mais texto (evita pegar <article> de relacionados)
        # Avalia candidatos específicos primeiro
        scored = []
        # id="single" é o container principal da Agência MS
        for sel in ["#single", "#content", "#post", ".post", ".entry-content", ".post-content",
                    ".article-content", ".single-content", ".noticia-conteudo", ".conteudo", ".texto",
                    "main", "[role=main]"]:
            el = soup.select_one(sel)
            if el:
                txt = self._paragraphs_to_text(el)
                words = len(txt.split())
                if words >= 40:
                    scored.append((words, txt))
        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            return scored[0][1]

        # 3) Melhor <article> por volume de texto (não o primeiro)
        articles = soup.find_all("article")
        if articles:
            best = None
            best_words = 0
            for art in articles:
                txt = self._paragraphs_to_text(art)
                w = len(txt.split())
                if w > best_words:
                    best_words = w
                    best = txt
            if best and best_words >= 40:
                return best

        return ""

    def _paragraphs_to_text(self, container) -> str:
        parts = []
        for el in container.find_all(["p", "h2", "h3", "li"]):
            text = self._clean_text(el.get_text(" ", strip=True))
            if not text or len(text.split()) < 3:
                continue
            if self._BOILERPLATE.search(text) and len(text.split()) < 12:
                continue
            if text in parts:
                continue
            parts.append(text)
        return "\n\n".join(parts)

    def _paragraph_fallback(self, soup: BeautifulSoup) -> str:
        """Reconstrói parágrafos do documento inteiro quando faltam seletores."""
        parts = []
        for el in soup.find_all("p"):
            text = self._clean_text(el.get_text(" ", strip=True))
            if not text or len(text.split()) < 3:
                continue
            if self._BOILERPLATE.search(text) and len(text.split()) < 12:
                continue
            parts.append(text)
        # limita a não' duplicar parágrafos idênticos consecutivos
        deduped = []
        for p in parts:
            if not deduped or p != deduped[-1]:
                deduped.append(p)
        return "\n\n".join(deduped)

    # ----------------------------------------------------------
    # Limpeza de texto
    # ----------------------------------------------------------
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # remove espaços duplicados, quebras e normaliza pontuação
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = text.replace("\u00a0", " ").strip()
        # remove prefixos repetidos de categoria/nome do portal presos ao texto
        text = self._dedupe_title(text)
        return text

    def _dedupe_title(self, text: str) -> str:
        """Remove repetições anômalas como 'XXX' + 'XXX' (prefixo colado ao texto)."""
        if not text:
            return text
        # ex.: "Utilidade PúblicaMato Grosso..." -> "Mato Grosso..."
        text = re.sub(
            r"^(Utilidade Pública|Notícias|Geral|Política|Economia|Saúde|"
            r"Esporte|Cultura|Educação|Agronegócio|Segurança)("
            r"(?=[A-ZÁÉÍÓÚÂÊÔÀ]))", "", text, flags=re.IGNORECASE
        )
        # remove palavras duplicadas consecutivas (falha de scraping)
        text = re.sub(r"\b(\w{4,})\s+\1\b", r"\1", text, flags=re.IGNORECASE)
        return text.strip()

    def _is_dirty_lead(self, lead: str) -> bool:
        if not lead or len(lead.strip()) < 40:
            return True
        # concatenação sem espaço: minúscula seguida de maiúscula
        if re.search(r"[a-záéíóúâêôãç][A-ZÁÉÍÓÚÂÊÔÃÇ]", lead):
            return True
        if "Utilidade Pública" in lead and "Mato" in lead and "PúblicaMato" in lead.replace(" ", ""):
            return True
        # lead com prefixo de categoria colado ou repetição grosseira
        if lead.count("Utilidade Pública") >= 1 and len(lead.split()) > 30:
            return True
        return False

    def _is_generic_lead(self, lead: str) -> bool:
        if not lead:
            return True
        low = lead.lower()
        generics = [
            "veja notícias em campo grande",
            "últimas notícias de economia, política",
            "o estado online - últimas",
            "acompanhe as últimas notícias",
            "fique por dentro",
        ]
        return any(g in low for g in generics)

    def _pick_first(self, *values) -> str:
        for v in values:
            if v and str(v).strip():
                return str(v).strip()
        return ""
