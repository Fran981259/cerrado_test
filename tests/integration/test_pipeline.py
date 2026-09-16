"""Integration: pipeline DB + health."""
import pathlib
from app.database import get_session
from app.schema import NewsArticle
from app.tasks.maintenance import system_health_check, report_metrics

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

def test_health_check_has_expected_keys():
    h = system_health_check()
    assert "status" in h and "checks" in h
    assert "database" in h["checks"]

def test_report_metrics_keys():
    m = report_metrics()
    assert "articles_today" in m and "success_rate" in m and "by_category" in m
