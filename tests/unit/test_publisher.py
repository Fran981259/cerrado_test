"""Unit tests para publisher slug."""
from app.database import get_session
from app.publisher import ArticlePublisher
from app.schema import NewsArticle
from datetime import datetime, timezone, timedelta
import unicodedata

def _get_reporter_id(db):
    from app.schema import Reporter
    rep = db.query(Reporter).first()
    if not rep:
        rep = Reporter(slug="test.reporter", display_name="Test Reporter", role="general", email="test@portalcerrado.com.br")
        db.add(rep); db.commit(); db.refresh(rep)
    return rep.id

def test_slug_unique_without_collision():
    db = get_session()
    pub = ArticlePublisher(db)
    title = f"Teste Slug Único Sem Colisão {datetime.now(timezone.utc).isoformat()}"
    slug = pub._generate_slug(title)
    # deve gerar sem -2
    assert slug and "-" in slug
    assert not slug.endswith("-1")
    db.close()

def test_slug_collision_generates_increment():
    db = get_session()
    pub = ArticlePublisher(db)
    rep_id = _get_reporter_id(db)
    title = f"Título Repetido Para Colisão {datetime.now(timezone.utc).timestamp()}"
    slug1 = pub._generate_slug(title)
    art = NewsArticle(title=title, slug=slug1, summary="x", content="x", reporter_id=rep_id, sources=[], status="published", category="general", tags=["general"], published_at=datetime.now(timezone.utc))
    db.add(art); db.commit()
    slug2 = pub._generate_slug(title)
    assert slug1 != slug2
    assert slug2 == f"{slug1}-2" or slug2.endswith("-2")
    # cleanup
    db.query(NewsArticle).filter(NewsArticle.slug==slug1).delete()
    db.commit()
    db.close()

def test_slug_normalizes_accents():
    db = get_session()
    pub = ArticlePublisher(db)
    title = "Ação com acentuação: São Paulo e coração"
    slug = pub._generate_slug(title)
    assert "acao" in slug
    assert "sao" in slug
    db.close()

def test_article_fetcher_extracts_real_page(monkeypatch=None):
    # smoke test: ArticleFetcher não lança em URL inválida
    from app.article_fetcher import ArticleFetcher
    f = ArticleFetcher()
    from unittest.mock import patch
    with patch("app.robots.is_allowed", return_value=True):
        res = f.fetch("https://invalid.invalid/notfound", base_summary="fallback")
    assert res["status"] in ("failed", "success")


def test_get_published_articles_orders_by_trend(monkeypatch):
    from app.schema import Reporter

    db = get_session()
    pub = ArticlePublisher(db)
    rep = Reporter(slug=f"trend.test.{datetime.now(timezone.utc).timestamp()}", display_name="Trend Test", role="general", email=None)
    db.add(rep)
    db.commit()
    db.refresh(rep)
    now = datetime.now(timezone.utc)

    arts = [
        NewsArticle(title="Saúde em alta", slug=f"trend-health-{now.timestamp()}", summary="x", content="x", reporter_id=rep.id, sources=[], status="published", category="health", tags=["health"], published_at=now - timedelta(minutes=10)),
        NewsArticle(title="Política em pauta", slug=f"trend-politics-{now.timestamp()}", summary="x", content="x", reporter_id=rep.id, sources=[], status="published", category="politics", tags=["politics"], published_at=now - timedelta(minutes=5)),
        NewsArticle(title="Economia no foco", slug=f"trend-economy-{now.timestamp()}", summary="x", content="x", reporter_id=rep.id, sources=[], status="published", category="economy", tags=["economy"], published_at=now),
    ]

    monkeypatch.setattr("app.publisher.get_latest_trend_signals", lambda limit=8: [{"category": "health"}, {"category": "politics"}])

    try:
        db.add_all(arts)
        db.commit()

        result = pub.get_published_articles(limit=10, reporter_slug=rep.slug, sort_by="trend")

        positions = {slug: next(i for i, item in enumerate(result) if item.get("slug") == slug) for slug in [a.slug for a in arts]}
        assert positions[arts[0].slug] < positions[arts[1].slug] < positions[arts[2].slug]
    finally:
        for art in arts:
            db.query(NewsArticle).filter(NewsArticle.slug == art.slug).delete()
        db.query(Reporter).filter(Reporter.id == rep.id).delete()
        db.commit()
        db.close()
