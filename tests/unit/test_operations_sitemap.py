from datetime import datetime, timedelta, timezone

from app.database import get_session
from app.operations_routes import recent_news_sitemap_articles
from app.schema import NewsArticle, Reporter


def _article(reporter_id: object, slug: str, published_at: datetime, visibility: str = "public") -> NewsArticle:
    return NewsArticle(
        title=slug,
        slug=slug,
        content="Conteúdo",
        reporter_id=reporter_id,
        status="published",
        visibility=visibility,
        region="ms",
        published_at=published_at,
    )


def _seed_articles(db, marker: str) -> Reporter:
    reporter = Reporter(slug=f"sitemap.{marker}", display_name="Sitemap", role="general")
    db.add(reporter)
    db.flush()
    now = datetime.now(timezone.utc)
    db.add_all(
        [
            _article(reporter.id, f"sitemap-public-{marker}", now),
            _article(reporter.id, f"sitemap-private-{marker}", now, visibility="private"),
            _article(reporter.id, f"sitemap-old-{marker}", now - timedelta(days=3)),
        ]
    )
    db.commit()
    return reporter


def test_news_sitemap_contains_only_recent_public_ms_articles() -> None:
    db = get_session()
    marker = str(datetime.now(timezone.utc).timestamp())
    reporter = _seed_articles(db, marker)
    try:
        result = recent_news_sitemap_articles(limit=1000)
        slugs = {article["slug"] for article in result["articles"]}
        assert f"sitemap-public-{marker}" in slugs
        assert f"sitemap-private-{marker}" not in slugs
        assert f"sitemap-old-{marker}" not in slugs
    finally:
        db.query(NewsArticle).filter(NewsArticle.slug.like(f"sitemap-%{marker}")).delete()
        db.delete(reporter)
        db.commit()
        db.close()
