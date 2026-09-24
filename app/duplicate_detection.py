"""Comparação de títulos para deduplicação editorial."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, List


class DuplicateDetector:
    """Detecta duplicatas textuais e semânticas entre artigos."""

    @staticmethod
    def are_duplicates(article1: Dict, article2: Dict, threshold: float = 0.85) -> bool:
        """Retorna se títulos iguais ou semanticamente próximos são duplicados."""
        title1 = article1.get("title", "").lower()
        title2 = article2.get("title", "").lower()
        if not title1 or not title2:
            return False
        return SequenceMatcher(None, title1, title2).ratio() >= threshold or DuplicateDetector.are_semantically_similar(title1, title2)

    @staticmethod
    def get_keywords(text: str) -> set:
        """Extrai palavras-chave relevantes, ignorando conectivos frequentes."""
        stopwords = {"para", "como", "sobre", "pelo", "pela", "onde", "mais", "isso", "esse", "esta", "entre", "ainda"}
        normalized = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()
        return set(re.findall(r"\b[a-z]{4,}\b", normalized)) - stopwords

    @staticmethod
    def are_semantically_similar(text1: str, text2: str) -> bool:
        """Compara a sobreposição das palavras-chave fundamentais."""
        keywords1 = DuplicateDetector.get_keywords(text1)
        keywords2 = DuplicateDetector.get_keywords(text2)
        if not keywords1 or not keywords2:
            return False
        intersection = keywords1.intersection(keywords2)
        return len(intersection) >= 3 and len(intersection) / min(len(keywords1), len(keywords2)) >= 0.45

    @staticmethod
    def find_duplicates(articles: List[Dict], threshold: float = 0.85) -> List[List[Dict]]:
        """Agrupa artigos duplicados sem repetir membros entre os grupos."""
        groups, used = [], set()
        for index, article in enumerate(articles):
            if index in used:
                continue
            group = [article]
            used.add(index)
            for other_index, other_article in enumerate(articles[index + 1 :], index + 1):
                if other_index not in used and DuplicateDetector.are_duplicates(article, other_article, threshold):
                    group.append(other_article)
                    used.add(other_index)
            if len(group) > 1:
                groups.append(group)
        return groups


class SensitiveContentFilter:
    """Compatibilidade para a política editorial sem bloqueio por termos."""

    SENSITIVE_TOPICS: Dict[str, Dict] = {}

    @staticmethod
    def check(article: Dict) -> Dict:
        """Retorna não sensível, pois a política não censura termos factuais."""
        return {"is_sensitive": False}
