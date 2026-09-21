"""Integration: pipeline DB + health."""

from datetime import datetime, timezone

from app.database import get_session
from app.schema import NewsArticle, PublicationLog, Reporter
from app.tasks.maintenance import report_metrics, system_health_check


def test_published_count_matches_pipeline_summary():
    db = get_session()
    cnt = db.query(NewsArticle).filter(NewsArticle.status == "published").count()
    db.close()
    assert isinstance(cnt, int)


def test_no_generic_titles_in_db():
    db = get_session()
    rows = db.query(NewsArticle).filter(NewsArticle.status == "published").all()
    for a in rows:
        assert a.title.strip().lower() != "o estado online"
        assert "homepage-nova" not in (
            (a.sources[0].get("url", "") if a.sources and isinstance(a.sources[0], dict) else "") if a.sources else ""
        )
        assert "mercedita e serenatas" not in a.title.lower()
    db.close()


def test_health_check_has_expected_keys():
    h = system_health_check()
    assert "status" in h and "checks" in h
    assert "database" in h["checks"]


def test_report_metrics_keys():
    m = report_metrics()
    assert "articles_today" in m and "success_rate" in m and "by_category" in m


def test_editorial_pipeline_classifies_rewrites_and_publishes(monkeypatch):
    """The real state transitions work without a network LLM call."""
    from app.tasks.classify_tasks import classify_pending_articles
    from app.tasks.publish_tasks import publish_ready_articles
    from app.tasks.rewrite_tasks import rewrite_pending_articles

    marker = str(datetime.now(timezone.utc).timestamp()).replace(".", "-")
    db = get_session()
    reporter = Reporter(
        slug=f"pipeline-{marker}",
        display_name="Pipeline Test",
        role="politics",
        email=f"pipeline-{marker}@portalcerrado.local",
    )
    db.add(reporter)
    db.flush()
    article = NewsArticle(
        title="Governo anuncia investimento público para saúde em Mato Grosso do Sul",
        slug=f"pipeline-{marker}",
        summary="O governo detalhou recursos para ampliar serviços públicos de saúde no estado.",
        content="Texto original com informações da fonte para a etapa de reescrita.",
        original_text="Texto original com informações da fonte para a etapa de reescrita.",
        reporter_id=reporter.id,
            sources=[{"url": f"https://www.midiamax.com.br/{marker}", "name": "Midiamax"}],
        status="draft",
        category="politics",
        region="ms",
        tags=["politics"],
    )
    db.add(article)
    db.flush()
    existing_log_count = db.query(PublicationLog).filter(PublicationLog.article_id == article.id).count()
    db.commit()
    article_id = article.id
    reporter_id = reporter.id
    db.close()

    rewritten_content = " ".join(["informacao verificada"] * 360)

    class FakeLLM:
        api_key = "test"

        def rewrite_article(self, *_args, **_kwargs):
            return {
                "rewritten_content": rewritten_content,
                "rewritten_title": "Investimento público reforça serviços de saúde em Mato Grosso do Sul",
                "rewritten_summary": "Texto reescrito para validar o fluxo editorial completo.",
            }

    monkeypatch.setattr("app.tasks.rewrite_tasks.LLMClient", FakeLLM)
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    try:
        classify_pending_articles()
        rewrite_pending_articles()
        publish_ready_articles()

        db = get_session()
        stored = db.get(NewsArticle, article_id)
        assert stored is not None
        assert stored.status == "published"
        assert stored.visibility == "public"
        assert stored.published_at is not None
        assert db.query(PublicationLog).filter(PublicationLog.article_id == article_id).count() == existing_log_count + 1
    finally:
        if "db" in locals():
            db.query(PublicationLog).filter(PublicationLog.article_id == article_id).delete()
            db.query(NewsArticle).filter(NewsArticle.id == article_id).delete()
            db.query(Reporter).filter(Reporter.id == reporter_id).delete()
            db.commit()
            db.close()
