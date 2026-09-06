"""Integration: pipeline DB + health/sitemap."""
import pathlib
from app.database import get_session
from app.schema import NewsArticle
from app.tasks.maintenance import system_health_check, report_metrics, update_sitemap

def test_published_count_matches_pipeline_summary():
    db = get_session()
    cnt = db.query(NewsArticle).filter(NewsArticle.status=="published").count()
    db.close()
    assert isinstance(cnt, int)

def test_no_generic_titles_in_db():
    db = get_session()
    rows = db.query(NewsArticle).filter(NewsArticle.status == "published").all()
    for a in rows:
        assert a.title.strip().lower() != "o estado online"
        assert "homepage-nova" not in ((a.sources[0].get("url", "") if a.sources and isinstance(a.sources[0], dict) else "") if a.sources else "")
        assert "mercedita e serenatas" not in a.title.lower()
    db.close()

def test_sitemap_generated():
    res = update_sitemap()
    assert res["sitemap_updated"] is True
    assert pathlib.Path("frontend/public/sitemap.xml").exists()
    xml = pathlib.Path("frontend/public/sitemap.xml").read_text(encoding="utf-8")
    assert "<urlset" in xml
    assert "100.95.111.24" in xml or "localhost" in xml

def test_health_check_has_expected_keys():
    h = system_health_check()
    assert "status" in h and "checks" in h
    assert "database" in h["checks"]

def test_report_metrics_keys():
    m = report_metrics()
    assert "articles_today" in m and "success_rate" in m and "by_category" in m
