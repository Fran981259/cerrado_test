"""ML editorial leve para o Portal Cerrado.

Este modulo cria um ranking de temas com base em sinais reais do portal:
categoria, frequencia recente, recencia e score editorial ja existente.
Nao escreve noticia. Nao substitui Gemini/OpenAI.
"""

from __future__ import annotations

import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import func

from app.database import get_session
from app.schema import EditorialTrendSignal, NewsArticle

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9]{3,}")

TOPIC_KEYWORDS = {
    "politics": {"governo", "prefeito", "governador", "câmara", "assembleia", "eleição", "política", "stf", "stj", "tre", "tse", "câmara dos vereadores", "assembleia legislativa"},
    "economy": {"economia", "mercado", "emprego", "juros", "inflação", "banco", "investimento", "arrecadação", "salário", "piso salarial"},
    "security": {"polícia", "crime", "prisão", "homicídio", "roubo", "furto", "investigação", "suspeito", "flagrante", "delegacia"},
    "health": {"saúde", "hospital", "vacina", "médico", "paciente", "uti", "sus", "dengue", "tratamento", "exame", "pronto-socorro"},
    "agriculture": {"agro", "agronegócio", "safra", "soja", "milho", "pecuária", "gado", "colheita", "plantio", "produtor rural"},
    "sports": {"futebol", "esporte", "jogo", "time", "gol", "campeonato", "atleta", "torcida", "vitória", "partida"},
    "tech": {"tecnologia", "ia", "inteligência artificial", "aprendizado de máquina", "app", "sistema", "software", "startup", "digital", "plataforma"},
}


@dataclass
class TrendItem:
    topic: str
    category: str
    score: int
    article_count: int
    evidence: List[Dict[str, Any]]


class EditorialTrendAnalyzer:
    """Agrupa e ranqueia temas com base em sinais do portal."""

    def normalize_text(self, text: str) -> str:
        return (text or "").lower().strip()

    def extract_tokens(self, article: Dict[str, Any]) -> List[str]:
        text = " ".join([
            article.get("title", ""),
            article.get("summary", ""),
            article.get("category", ""),
        ])
        return _TOKEN_RE.findall(self.normalize_text(text))

    def extract_phrases(self, article: Dict[str, Any]) -> str:
        return self.normalize_text(" ".join([
            article.get("title", ""),
            article.get("summary", ""),
            article.get("category", ""),
        ]))

    def _keyword_hits(self, article: Dict[str, Any], keywords: Iterable[str]) -> int:
        tokens = set(self.extract_tokens(article))
        text = self.extract_phrases(article)
        hits = 0
        for keyword in keywords:
            kw = self.normalize_text(keyword)
            if " " in kw:
                if kw in text:
                    hits += 1
            elif kw in tokens:
                hits += 1
        return hits

    def guess_topic(self, article: Dict[str, Any]) -> str:
        category = (article.get("category") or "general").lower().strip()
        if category in TOPIC_KEYWORDS:
            return category

        for topic, keywords in TOPIC_KEYWORDS.items():
            if self._keyword_hits(article, keywords) > 0:
                return topic
        return "general"

    def article_weight(self, article: Dict[str, Any]) -> float:
        classification = article.get("classification", {}) if isinstance(article.get("classification"), dict) else {}
        final_score = float(classification.get("final_score", article.get("final_score", 0)) or 0)
        priority_tier = classification.get("priority_tier") or article.get("priority_tier") or "TIER_3"
        tier_boost = {"TIER_1": 1.3, "TIER_2": 1.15, "TIER_3": 1.0, "REJECT": 0.4}.get(priority_tier, 1.0)

        when = article.get("published_at") or article.get("created_at") or article.get("scraped_at")
        recency_boost = 1.0
        if isinstance(when, datetime):
            age_hours = max((datetime.utcnow() - when).total_seconds() / 3600.0, 0.0)
            recency_boost = 1.0 + max(0.0, 24.0 - age_hours) / 24.0

        base = 1.0 + (final_score / 10.0)
        return base * tier_boost * recency_boost

    def build_trends(self, articles: Iterable[Dict[str, Any]], window_hours: int = 24) -> List[TrendItem]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for article in articles:
            if not isinstance(article, dict):
                continue
            topic = self.guess_topic(article)
            grouped[topic].append(article)

        items: List[TrendItem] = []
        for topic, group in grouped.items():
            category_counter = Counter((a.get("category") or "general").lower() for a in group)
            dominant_category = category_counter.most_common(1)[0][0] if category_counter else "general"
            keyword_signal = sum(max(1, self._keyword_hits(a, TOPIC_KEYWORDS.get(topic, set()))) for a in group)
            weight_sum = sum(self.article_weight(a) for a in group)
            score = int(round((weight_sum * 10) + (keyword_signal * 2)))
            evidence = []
            for a in group[:5]:
                evidence.append({
                    "title": a.get("title", ""),
                    "slug": a.get("slug", ""),
                    "category": a.get("category", "general"),
                    "weight": round(self.article_weight(a), 2),
                })
            items.append(TrendItem(topic=topic, category=dominant_category, score=score, article_count=len(group), evidence=evidence))

        items.sort(key=lambda x: (x.score, x.article_count), reverse=True)
        return items

    def refresh_trend_signals(self, session=None, window_hours: int = 24, limit: int = 200) -> List[Dict[str, Any]]:
        db = session or get_session()
        close_db = session is None
        try:
            cutoff = datetime.utcnow() - timedelta(hours=window_hours)
            articles = (
                db.query(NewsArticle)
                .filter(NewsArticle.status.in_(["classified", "rewritten", "published"]))
                .filter(func.coalesce(NewsArticle.published_at, NewsArticle.created_at) >= cutoff)
                .order_by(func.coalesce(NewsArticle.published_at, NewsArticle.created_at).desc())
                .limit(limit)
                .all()
            )

            payload = [
                {
                    "title": art.title,
                    "slug": art.slug,
                    "category": art.category,
                    "summary": art.summary or "",
                    "final_score": art.final_score or 0,
                    "priority_tier": art.priority_tier or "TIER_3",
                    "created_at": art.created_at,
                    "published_at": art.published_at,
                    "classification": {
                        "final_score": (art.final_score or 0) / 10.0,
                        "priority_tier": art.priority_tier or "TIER_3",
                    },
                }
                for art in articles
            ]

            trends = self.build_trends(payload, window_hours=window_hours)
            saved: List[Dict[str, Any]] = []
            for item in trends:
                row = EditorialTrendSignal(
                    topic=item.topic,
                    category=item.category,
                    score=item.score,
                    article_count=item.article_count,
                    window_hours=window_hours,
                    evidence=item.evidence,
                )
                db.add(row)
                saved.append({
                    "topic": item.topic,
                    "category": item.category,
                    "score": item.score,
                    "article_count": item.article_count,
                    "window_hours": window_hours,
                    "evidence": item.evidence,
                })

            db.commit()
            return saved
        except Exception:
            db.rollback()
            raise
        finally:
            if close_db:
                db.close()


    def latest_trend_signals(self, session=None, limit: int = 8) -> List[Dict[str, Any]]:
        db = session or get_session()
        close_db = session is None
        try:
            rows = (
                db.query(EditorialTrendSignal)
                .order_by(EditorialTrendSignal.generated_at.desc(), EditorialTrendSignal.score.desc())
                .all()
            )
            deduped: List[Dict[str, Any]] = []
            seen = set()
            for row in rows:
                if row.topic in seen:
                    continue
                seen.add(row.topic)
                deduped.append({
                    "topic": row.topic,
                    "category": row.category,
                    "score": row.score,
                    "article_count": row.article_count,
                    "window_hours": row.window_hours,
                    "generated_at": row.generated_at.isoformat() if row.generated_at else None,
                    "evidence": row.evidence or [],
                })
                if len(deduped) >= limit:
                    break

            if not deduped:
                return self.refresh_trend_signals(session=db, window_hours=24, limit=limit)
            return deduped
        finally:
            if close_db:
                db.close()


def get_current_trends(window_hours: int = 24, limit: int = 200) -> List[Dict[str, Any]]:
    return EditorialTrendAnalyzer().refresh_trend_signals(window_hours=window_hours, limit=limit)


def get_latest_trend_signals(limit: int = 8) -> List[Dict[str, Any]]:
    return EditorialTrendAnalyzer().latest_trend_signals(limit=limit)
