"""Inferência de categoria do classificador."""

import re

from app.classifier_category_keywords import CATEGORY_KEYWORDS


class CategoryClassifierMixin:
    def classify_category(self, text: str) -> str:
        """Heurística para classificar categoria. Retorna nome canônico de contracts.CATEGORIES."""
        from app.contracts import category_name

        text = text.lower()
        mapping = CATEGORY_KEYWORDS
        for cat, keywords in mapping.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in keywords):
                return category_name(cat)
        return category_name("general")
