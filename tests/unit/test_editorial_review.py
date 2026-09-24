"""Regression coverage for the protected editorial queue."""

from datetime import datetime, timezone

from fastapi.routing import APIRoute

from app.database import get_session
from app.schema import NewsArticle, Reporter


def test_editorial_queue_includes_local_publications_only():
    """Published local articles remain available for category correction."""
    from app.editorial_routes import list_articles_for_review

    db = get_session()
    marker = str(datetime.now(timezone.utc).timestamp()).replace(".", "-")
    reporter = Reporter(slug=f"editorial-{marker}", display_name="Editorial Test", role="general")
    try:
        db.add(reporter)
        db.flush()
        articles = [
            _article(reporter, marker, "published-ms", "ms", "public"),
            _article(reporter, marker, "published-global", "global", "public"),
            _article(reporter, marker, "published-archived", "ms", "archived"),
        ]
        db.add_all(articles)
        db.commit()
        queue = list_articles_for_review(_auth=None)["articles"]
        slugs = {article["slug"] for article in queue}
        assert articles[0].slug in slugs
        assert articles[1].slug not in slugs
        assert articles[2].slug not in slugs
    finally:
        db.query(NewsArticle).filter(NewsArticle.slug.like(f"editorial-%-{marker}")).delete()
        db.query(Reporter).filter(Reporter.slug == reporter.slug).delete()
        db.commit()
        db.close()


def test_editorial_and_analytics_routes_have_one_registration():
    """Protect routes moved to specialized routers from shadow registrations."""
    from app.main import app

    registered_routes = list(_route_keys(app.routes))
    expected_routes = {
        ("/api/publish", "POST"),
        ("/api/editorial/review", "GET"),
        ("/api/editorial/review/{slug}", "PUT"),
        ("/api/analytics/track", "POST"),
    }

    for route in expected_routes:
        assert registered_routes.count(route) == 1


def _route_keys(routes):
    """Yield HTTP route keys, including nested routers in current FastAPI."""
    for route in routes:
        if isinstance(route, APIRoute):
            yield from ((route.path, method) for method in route.methods or set())
        elif nested_router := getattr(route, "original_router", None):
            yield from _route_keys(nested_router.routes)


def _article(reporter: Reporter, marker: str, suffix: str, region: str, visibility: str) -> NewsArticle:
    return NewsArticle(
        title=f"Editorial {suffix}",
        slug=f"editorial-{suffix}-{marker}",
        summary="Resumo de teste",
        content="Conteúdo de teste",
        reporter_id=reporter.id,
        sources=[],
        status="published",
        visibility=visibility,
        category="general",
        region=region,
        tags=["general"],
        published_at=datetime.now(timezone.utc),
    )
