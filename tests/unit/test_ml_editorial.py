from datetime import datetime, timedelta


def test_trend_analyzer_prioritizes_repeated_topics():
    from app.ml_editorial import EditorialTrendAnalyzer

    now = datetime.utcnow()
    articles = [
        {
            "title": "Governo anuncia nova medida na política estadual",
            "summary": "A política estadual recebeu novas diretrizes.",
            "category": "politics",
            "created_at": now,
            "classification": {"final_score": 4.0, "priority_tier": "TIER_1"},
        },
        {
            "title": "Assembleia debate projeto do governo",
            "summary": "O governo apresentou projeto e debate segue em pauta.",
            "category": "politics",
            "created_at": now - timedelta(hours=1),
            "classification": {"final_score": 3.5, "priority_tier": "TIER_2"},
        },
        {
            "title": "Mercado registra leve alta no emprego",
            "summary": "Indicadores econômicos mostram melhora.",
            "category": "economy",
            "created_at": now,
            "classification": {"final_score": 3.0, "priority_tier": "TIER_2"},
        },
    ]

    analyzer = EditorialTrendAnalyzer()
    trends = analyzer.build_trends(articles)

    assert trends[0].topic == "politics"
    assert trends[0].article_count == 2
    assert trends[0].score >= trends[1].score


def test_guess_topic_uses_keywords_when_category_is_generic():
    from app.ml_editorial import EditorialTrendAnalyzer

    analyzer = EditorialTrendAnalyzer()
    topic = analyzer.guess_topic({
        "title": "Polícia investiga roubo em Campo Grande",
        "summary": "A ocorrência mobilizou a polícia e a investigação.",
        "category": "general",
    })

    assert topic == "security"
