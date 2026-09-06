"""Tests para robots.txt enforcement (item 8)."""
import os
from unittest.mock import patch, MagicMock
from app.robots import is_allowed, _fetch_and_parse, _can_fetch_from_text

CANNED_ROBOTS = """User-agent: *
Disallow: /busca
Allow: /
"""


def _temp_db(monkeypatch, tmp_path):
    """Banco SQLite temporário p/ is_allowed (não toca no DATABASE_URL real)."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    import app.schema  # noqa: F401 — registra as tabelas no metadata ANTES do create_all
    db_file = str(tmp_path / "robots_test.db")
    engine = sqlalchemy.create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr("app.database.get_session", lambda: Session())
    return Session


def test_robots_per_path_cache_granularity(monkeypatch, tmp_path):
    """Regressão item 2: dois paths do mesmo domínio no mesmo cache window
    retornam resultados diferentes (antes, o 1º path decidia por todos)."""
    _temp_db(monkeypatch, tmp_path)
    import app.robots as robots_mod
    robots_mod.RESPECT_ROBOTS = True
    with patch("app.robots._fetch_raw", return_value=CANNED_ROBOTS) as mock_fetch:
        assert is_allowed("https://example.com/noticias/x", user_agent="*") is True
        assert is_allowed("https://example.com/busca?q=1", user_agent="*") is False
        # 2ª chamada usa cache de conteúdo (1 fetch só) e ainda diferencia
        assert is_allowed("https://example.com/noticias/y", user_agent="*") is True
        assert is_allowed("https://example.com/busca", user_agent="*") is False
        assert mock_fetch.call_count == 1


def test_robots_legacy_row_without_content_refetches(monkeypatch, tmp_path):
    """Linha legada (só booleano, sem conteúdo) = cache miss, sem crash."""
    Session = _temp_db(monkeypatch, tmp_path)
    from app.schema import SourcePortal
    from datetime import datetime
    db = Session()
    db.add(SourcePortal(url="https://legacy.com", name="legacy",
                        robots_txt_last_fetched=datetime.utcnow(),
                        robots_txt_allowed=True, robots_txt_content=None))
    db.commit()
    db.close()
    import app.robots as robots_mod
    robots_mod.RESPECT_ROBOTS = True
    with patch("app.robots._fetch_raw", return_value=CANNED_ROBOTS) as mock_fetch:
        assert is_allowed("https://legacy.com/noticias/x", user_agent="*") is True
        assert mock_fetch.call_count == 1

def test_robots_respects_env_disable():
    with patch.dict(os.environ, {"RESPECT_ROBOTS_TXT": "0"}):
        # reload module to pick env? is_allowed reads env at import time via global, but also checks global var
        # Instead patch the global directly
        import app.robots as robots_mod
        orig = robots_mod.RESPECT_ROBOTS
        robots_mod.RESPECT_ROBOTS = False
        try:
            assert is_allowed("https://example.com/page") is True
        finally:
            robots_mod.RESPECT_ROBOTS = orig

def test_robots_fetch_and_parse_allows_on_failure():
    # _fetch_and_parse should return True on exception (fail-open)
    with patch("urllib.robotparser.RobotFileParser.read", side_effect=Exception("network fail")):
        allowed = _fetch_and_parse("https://example.com/robots.txt", "TestBot", "https://example.com/page")
        assert allowed is True

def test_robots_is_allowed_uses_cache(monkeypatch=None):
    # Test that scanner calls is_allowed before fetching
    from app.scanner import RealPortalScanner
    scanner = RealPortalScanner()
    with patch("app.robots.is_allowed", return_value=False) as mock:
        res = scanner._scan_portal({"name": "Test", "url": "https://example.com", "selectors": {}})
        assert res["status"] == "blocked"
        mock.assert_called_once()

def test_article_fetcher_blocks_robots():
    from app.article_fetcher import ArticleFetcher
    fetcher = ArticleFetcher()
    with patch("app.robots.is_allowed", return_value=False):
        res = fetcher.fetch("https://example.com/noticia/123", base_summary="x")
        assert res["status"] == "blocked"
        assert res["reason"] == "robots.txt disallow"

def test_miner_blocks_robots():
    from app.miner import GlobalNewsMiner
    miner = GlobalNewsMiner.__new__(GlobalNewsMiner)
    miner.config = {"global_miner": {"portals": {}}}
    miner.classifier = None
    import httpx
    miner.session = httpx.Client()
    # Mock is_allowed to block
    with patch("app.robots.is_allowed", return_value=False):
        res = miner._mine_portal({"name": "Test", "rss": "https://example.com/rss", "url": "https://example.com"}, "technology", limit=5)
        assert res == []
