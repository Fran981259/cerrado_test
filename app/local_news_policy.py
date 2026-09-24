"""Single editorial policy for a Mato Grosso do Sul local-news operation."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_CITIES = {"fortaleza", "nacional"}
LOCAL_CONTEXT_TERMS = (
    "mato grosso do sul",
    "sul-mato-gross",
    "campo grande",
    "dourados",
    "três lagoas",
    "tres lagoas",
    "corumbá",
    "corumba",
    "ponta porã",
    "ponta pora",
    "aquidauana",
    "bonito",
    "naviraí",
    "navirai",
    "sidrolândia",
    "sidrolandia",
    "chapadão do sul",
    "chapadao do sul",
    "coxím",
    "coxim",
    "maracaju",
    "paranaíba",
    "paranaiba",
    "nova andradina",
    "costa rica",
)


def _host(url: str) -> str:
    return (urlsplit(url or "").hostname or "").lower().removeprefix("www.")


@lru_cache(maxsize=1)
def local_source_hosts() -> frozenset[str]:
    """Read the regional source registry; foreign entries are deliberately excluded."""
    config = yaml.safe_load((ROOT / "config" / "portals_capital_ms.yml").read_text(encoding="utf-8")) or {}
    hosts: set[str] = {"g1.globo.com", "agenciadenoticias.ms.gov.br", "msnews.com.br"}
    for entries in (config.get("portals_ms") or {}).values():
        for entry in entries or []:
            city = str(entry.get("city") or "").strip().lower()
            if city in EXCLUDED_CITIES:
                continue
            value = _host(str(entry.get("url") or ""))
            if value:
                hosts.add(value)
    return frozenset(hosts)


def is_local_source(url: str) -> bool:
    value = _host(url)
    return any(value == allowed or value.endswith(f".{allowed}") for allowed in local_source_hosts())


def has_local_context(*texts: str) -> bool:
    content = " ".join(text or "" for text in texts).lower()
    return any(term in content for term in LOCAL_CONTEXT_TERMS)


def local_story_decision(*, source_url: str, title: str = "", summary: str = "", body: str = "") -> str:
    """Return ``accept``, ``review`` or ``reject`` without inventing local relevance."""
    if not is_local_source(source_url):
        return "reject"
    if not has_local_context(title, summary, body):
        return "review"
    return "accept"
