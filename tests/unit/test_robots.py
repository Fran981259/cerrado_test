"""Tests para robots.txt enforcement (item 8)."""
import os
from unittest.mock import patch, MagicMock
from app.robots import is_allowed, _fetch_and_parse

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
