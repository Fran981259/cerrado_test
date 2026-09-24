"""Catálogo composto do scanner."""

from app.scanner_keyword_core import CATEGORY_KEYWORDS as _CORE_KEYWORDS
from app.scanner_keyword_extra import CATEGORY_KEYWORDS as _EXTRA_KEYWORDS

CATEGORY_KEYWORDS = {**_CORE_KEYWORDS, **_EXTRA_KEYWORDS}

REPORTER_BY_CATEGORY = {
    "tech": "enzo.bianchi",
    "sports": "marcus.teixeira",
    "security": "rafael.dumas",
    "politics": "luciana.freitas",
    "health": "maya.santos",
    "education": "lucas.nakamura",
    "agriculture": "bia.fernandes",
    "entertainment": "leon.vaz",
    "economy": "camila.rocha",
    "general": "enzo.bianchi",
    # aliases vindos do classifier/miner
    "culture": "leon.vaz",
    "science": "maya.santos",
}
