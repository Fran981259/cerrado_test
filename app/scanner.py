"""
Scanner REAL de Notícias — Portal Cerrado
Coleta headlines de portais brasileiros via HTTP.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlparse

import requests

from app.scanner_catalog import CATEGORY_KEYWORDS, REPORTER_BY_CATEGORY
from app.scanner_parsing import ScannerArticleMethods

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _normalize_url(u: str) -> str:
    try:
        p = urlparse((u or "").strip())
        netloc = (p.netloc or "").lower()
        scheme = (p.scheme or "https").lower()
        path = p.path.rstrip("/") or ""
        # remove www. for dedup? keep but normalize www vs non-www as same
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return f"{scheme}://{netloc}{path}"
    except Exception:
        return (u or "").strip().rstrip("/").lower()


class RealPortalScanner(ScannerArticleMethods):
    """Scanner que faz scraping REAL de portais."""

    CATEGORY_KEYWORDS = CATEGORY_KEYWORDS
    REPORTER_BY_CATEGORY = REPORTER_BY_CATEGORY

    PORTALS = [
        {
            "name": "MS News",
            "url": "https://www.msnews.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia, .news-item",
                "title": "h1, h2, h3, .title, .titulo",
                "link": "a",
            },
        },
        {
            "name": "MS Todo Dia",
            "url": "https://www.mstododia.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            },
        },
        {
            "name": "G1 MS",
            "url": "https://g1.globo.com/ms/",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            },
        },
        {
            "name": "O Estado Online",
            "url": "https://www.oestadoonline.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            },
        },
    ]

    _ms_lock = threading.Lock()

    @classmethod
    def _load_ms_portals(cls):
        """Carrega exclusivamente fontes jornalísticas de Mato Grosso do Sul."""
        import os

        import yaml

        with cls._ms_lock:
            if getattr(cls, "_ms_loaded", False):
                return

            # Carregar portais do MS
            cfg_ms = os.path.join(os.path.dirname(__file__), "..", "config", "portals_capital_ms.yml")
            cfg_ms = os.path.abspath(cfg_ms)

            seen = {_normalize_url(p["url"]) for p in cls.PORTALS}
            added = 0

            # 1. Portais MS
            if os.path.exists(cfg_ms):
                try:
                    with open(cfg_ms, "r", encoding="utf-8") as f:
                        data_ms = yaml.safe_load(f) or {}
                    for city, lst in (data_ms.get("portals_ms") or {}).items():
                        for p in lst or []:
                            url = (p.get("url") or "").strip()
                            norm = _normalize_url(url)
                            if not url or norm in seen:
                                continue
                            if not isinstance(p.get("name"), str) or not p.get("url"):
                                continue
                            city_name = p.get("city") or city
                            if city_name.strip().lower() in {"nacional", "fortaleza"}:
                                continue
                            cls.PORTALS.append(
                                {
                                    "name": p.get("name") or url,
                                    "url": url,
                                    "default_category": "general",
                                    "city": city_name,
                                    "region": "ms",
                                    "selectors": {
                                        "article": "article, .post, .noticia, .news-item",
                                        "title": "h1, h2, h3, .title, .titulo",
                                        "link": "a",
                                    },
                                }
                            )
                            seen.add(norm)
                            added += 1
                except Exception as e:
                    logger.warning(f"[SCANNER] falha ao carregar portals_capital_ms.yml: {e}")

            if added:
                logger.info(f"[SCANNER] Fontes locais carregadas: +{added} (total {len(cls.PORTALS)})")
            cls._ms_loaded = True

    def __init__(self):
        self.__class__._load_ms_portals()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def scan_all(self) -> Dict:
        """Escaneia TODOS os portais configurados — concorrente (6 threads)."""
        import concurrent.futures

        results: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "portals": {},
            "articles": [],
            "summary": {"total": 0, "success": 0, "failed": 0},
        }

        def _scan_one(p):
            try:
                return p["name"], self._scan_portal(p)
            except Exception as e:
                logger.error(f"Erro ao escanear {p['name']}: {e}")
                return p["name"], {
                    "name": p["name"],
                    "url": p["url"],
                    "status": "failed",
                    "error": str(e),
                    "articles": [],
                }

        # ThreadPool reduz 42*15s sequencial (~600s) para ~100s com 6 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
            futures = {ex.submit(_scan_one, p): p for p in self.PORTALS}
            for fut in concurrent.futures.as_completed(futures):
                name, res = fut.result()
                results["portals"][name] = res
                results["summary"]["total"] += 1
                if res.get("status") == "success":
                    results["summary"]["success"] += 1
                    results["articles"].extend(res.get("articles", []))
                else:
                    results["summary"]["failed"] += 1
        return results
