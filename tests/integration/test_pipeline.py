"""Integration: pipeline DB + frontend export."""
from app.database import get_session
from app.schema import NewsArticle
from app.tasks.frontend_tasks import export_frontend_articles_to_files
from app.tasks.maintenance import system_health_check, report_metrics, update_sitemap
import json, pathlib

def test_published_count_matches_export():
    db = get_session()
    cnt = db.query(NewsArticle).filter(NewsArticle.status=="published").count()
    db.close()
    res = export_frontend_articles_to_files(limit=100)
    data = json.loads(pathlib.Path("frontend/src/data/articles.json").read_text(encoding="utf-8"))
    assert res["exported"] == len(data)
    assert abs(res["exported"] - cnt) <= 1  # allow small drift

def test_no_generic_titles_in_export():
    data = json.loads(pathlib.Path("frontend/src/data/articles.json").read_text(encoding="utf-8"))
    for a in data:
        assert a["title"].strip().lower() != "o estado online"
        assert "homepage-nova" not in (a.get("url","") or "")
        assert "mercedita e serenatas" not in a["title"].lower()

def test_sitemap_generated():
    res = update_sitemap()
    assert res["sitemap_updated"] is True
    assert pathlib.Path("frontend/public/sitemap.xml").exists()
    xml = pathlib.Path("frontend/public/sitemap.xml").read_text(encoding="utf-8")
    assert "<urlset" in xml and "atualizabrasil.news" in xml or "localhost" in xml

def test_health_check_has_expected_keys():
    h = system_health_check()
    assert "status" in h and "checks" in h
    assert "database" in h["checks"]

def test_report_metrics_keys():
    m = report_metrics()
    assert "articles_today" in m and "success_rate" in m and "by_category" in m
