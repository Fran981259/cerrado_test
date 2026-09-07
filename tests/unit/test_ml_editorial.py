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


def test_guess_topic_handles_multiword_phrase():
    from app.ml_editorial import EditorialTrendAnalyzer

    analyzer = EditorialTrendAnalyzer()
    topic = analyzer.guess_topic({
        "title": "Inteligência artificial avança nas redações",
        "summary": "",
        "category": "general",
    })

    assert topic == "tech"


def test_refresh_trend_signals_uses_real_db_rows():
    from app.database import get_session
    from app.schema import NewsArticle, Reporter, EditorialTrendSignal
    from app.ml_editorial import EditorialTrendAnalyzer

    db = get_session()
    reporter = db.query(Reporter).first()
    assert reporter is not None

    slug = f"ml-trend-{datetime.utcnow().timestamp()}"
    article = NewsArticle(
        title="Governo e assembleia discutem pacote econômico em MS",
        slug=slug,
        summary="A política econômica do estado ganhou novo debate.",
        content="Conteúdo de teste para tendência.",
        reporter_id=reporter.id,
        status="published",
        category="politics",
        published_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        visibility="public",
        final_score=40,
        priority_tier="TIER_1",
    )

    try:
        db.add(article)
        db.commit()

        before = db.query(EditorialTrendSignal).count()
        trends = EditorialTrendAnalyzer().refresh_trend_signals(session=db, window_hours=24, limit=20)
        after = db.query(EditorialTrendSignal).count()

        assert after >= before
        assert any(t["topic"] == "politics" for t in trends)
    finally:
        db.query(EditorialTrendSignal).filter(EditorialTrendSignal.evidence.like(f'%{slug}%')).delete(synchronize_session=False)
        db.query(NewsArticle).filter(NewsArticle.slug == slug).delete(synchronize_session=False)
        db.commit()
        db.close()
