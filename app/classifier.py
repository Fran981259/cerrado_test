"""
Classificador de Notícias — Portal Cerrado
============================================
Avalia cada notícia minerada/coletada por:
- Grau de importância (impacto)
- Potencial de engajamento
- Score final combinado
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from app.classifier_category import CategoryClassifierMixin
from app.classifier_patterns import PatternLoaderMixin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportanceLevel(Enum):
    """Níveis de importância da notícia."""

    CRITICAL = 5  # Acontecimentos globais majeures
    HIGH = 4  # Impacto regional/nacional forte
    MEDIUM = 3  # Relevante mas não excepcional
    LOW = 2  # Interesse local/curiosidade
    MINIMAL = 1  # Preenchimento, sem grande impacto


class EngagementLevel(Enum):
    """Níveis de potencial de engajamento."""

    VIRAL = 5  # Potencial para viralizar (celebridades, escândalos)
    HIGH = 4  # Alto engajamento (polêmicas, novidades)
    MEDIUM = 3  # Engajamento moderado
    LOW = 2  # Baixo engajamento
    MINIMAL = 1  # Pouco interesse


class NewsClassifier(PatternLoaderMixin, CategoryClassifierMixin):
    """Classificador de notícias por importância e engajamento."""

    # Pesos para cálculo do score final
    WEIGHT_IMPORTANCE = 0.6  # 60% importância
    WEIGHT_ENGAGEMENT = 0.4  # 40% engajamento

    def __init__(self):
        self._load_patterns()

    def classify(self, article: Dict) -> Dict:
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        combined = title + " " + summary

        importance_score = self._calculate_importance(combined, article)
        engagement_score = self._calculate_engagement(combined, article)

        final_score = importance_score * self.WEIGHT_IMPORTANCE + engagement_score * self.WEIGHT_ENGAGEMENT

        importance_level = self._get_importance_level(importance_score)
        engagement_level = self._get_engagement_level(engagement_score)
        priority_tier = self._get_priority_tier(final_score)

        article["classification"] = {
            "importance_score": round(importance_score, 2),
            "engagement_score": round(engagement_score, 2),
            "final_score": round(final_score, 2),
            "importance_level": importance_level.name,
            "engagement_level": engagement_level.name,
            "priority_tier": priority_tier,
            "classified_at": datetime.now(timezone.utc).isoformat(),
        }
        return article

    def _calculate_importance(self, text: str, article: Dict) -> float:
        score = 3.0
        for keyword, weight in self.high_importance_keywords.items():
            if keyword.lower() in text:
                score = max(score, weight)
                if weight >= 4:
                    break
        for keyword, weight in self.low_importance_keywords.items():
            if keyword.lower() in text:
                score = min(score, weight)
        category = article.get("category", "")
        from app.contracts import category_name

        cat = category_name(category)
        if cat in ("politics", "economy", "health", "agriculture", "technology", "security"):
            score = min(5.0, score + 0.4)
        elif cat == "sports":
            score = max(2.0, score - 0.5)
        source = article.get("source", "").lower()
        tier1_sources = ["reuters", "bloomberg", "financial times", "nature", "science"]
        if any(s in source for s in tier1_sources):
            score = min(5.0, score + 0.3)
        return max(1.0, min(5.0, score))

    def _calculate_engagement(self, text: str, article: Dict) -> float:
        score = 3.0
        for keyword, weight in self.high_engagement_keywords.items():
            if keyword.lower() in text:
                score = max(score, weight)
                if weight >= 4:
                    break
        for keyword, weight in self.low_engagement_keywords.items():
            if keyword.lower() in text:
                score = min(score, weight)
        exclamations = text.count("!")
        questions = text.count("?")
        if exclamations >= 2 or questions >= 2:
            score = min(5.0, score + 0.5)
        title_len = len(article.get("title", ""))
        if title_len > 150:
            score = max(1.0, score - 0.5)
        elif 40 <= title_len <= 90:
            score = min(5.0, score + 0.3)
        return max(1.0, min(5.0, score))

    def _get_importance_level(self, score: float) -> ImportanceLevel:
        if score >= 4.5:
            return ImportanceLevel.CRITICAL
        elif score >= 3.5:
            return ImportanceLevel.HIGH
        elif score >= 2.5:
            return ImportanceLevel.MEDIUM
        elif score >= 1.5:
            return ImportanceLevel.LOW
        else:
            return ImportanceLevel.MINIMAL

    def _get_engagement_level(self, score: float) -> EngagementLevel:
        if score >= 4.5:
            return EngagementLevel.VIRAL
        elif score >= 3.5:
            return EngagementLevel.HIGH
        elif score >= 2.5:
            return EngagementLevel.MEDIUM
        elif score >= 1.5:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.MINIMAL

    def _get_priority_tier(self, final_score: float) -> str:
        if final_score >= 4.0:
            return "TIER_1"
        elif final_score >= 3.0:
            return "TIER_2"
        elif final_score >= 2.0:
            return "TIER_3"
        else:
            return "REJECT"

    def filter_by_priority(self, articles: List[Dict], min_tier: str = "TIER_3") -> List[Dict]:
        tier_order = {"TIER_1": 4, "TIER_2": 3, "TIER_3": 2, "REJECT": 1}
        min_level = tier_order.get(min_tier, 2)
        filtered = []
        for article in articles:
            tier = article.get("classification", {}).get("priority_tier", "REJECT")
            if tier_order.get(tier, 0) >= min_level:
                filtered.append(article)
        filtered.sort(key=lambda a: a.get("classification", {}).get("final_score", 0), reverse=True)
        return filtered
