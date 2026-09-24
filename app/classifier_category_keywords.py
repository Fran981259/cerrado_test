"""Agregador das palavras-chave de categorização."""

from app.classifier_category_core import CATEGORY_KEYWORDS as _CORE_KEYWORDS
from app.classifier_category_extra import CATEGORY_KEYWORDS as _EXTRA_KEYWORDS

CATEGORY_KEYWORDS = {**_CORE_KEYWORDS, **_EXTRA_KEYWORDS}
