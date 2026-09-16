"""Robots decisions distinguish missing policies from unavailable origins."""
import logging
import os
from datetime import timedelta
from urllib.error import HTTPError
from urllib.parse import urlsplit, urljoin
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from app.contracts import as_utc, utcnow

logger = logging.getLogger(__name__)
USER_AGENT = os.getenv("USER_AGENT", "PortalCerrado/1.0")
RESPECT_ROBOTS = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() not in ("0", "false", "no")
CACHE_TTL_HOURS = int(os.getenv("ROBOTS_TXT_CACHE_HOURS", "24"))
ALLOW = "User-agent: *\nAllow: /"
DENY = "User-agent: *\nDisallow: /"


def _get_base(url):
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _fetch_raw(robots_url):
    try:
        with urlopen(Request(robots_url, headers={"User-Agent": USER_AGENT}), timeout=5) as response:
            return response.read(512_000).decode("utf-8", errors="replace") or ALLOW
    except HTTPError as exc:
        if exc.code in (404, 410):
            return ALLOW
        if exc.code in (401, 403):
            return DENY
    except Exception:
        pass
    return None


def _can_fetch_from_text(content, user_agent, target_url):
    if content is None:
        return False
    parser = RobotFileParser()
    parser.parse(content.splitlines())
    return parser.can_fetch(user_agent, target_url)


def _fetch_and_parse(robots_url, user_agent, target_url):
    return _can_fetch_from_text(_fetch_raw(robots_url), user_agent, target_url)


_MEM_CACHE: dict = {}
def is_allowed(url, user_agent=None):
    if not RESPECT_ROBOTS:
        return True
    ua = user_agent or USER_AGENT
    base = _get_base(url)
    robots_url = urljoin(base + "/", "robots.txt")
    # mem cache: evita 40 DB+HTTP sequenciais por scan_all
    cached = _MEM_CACHE.get(base)
    if cached:
        content, fetched_at = cached
        if timedelta(0) <= utcnow() - fetched_at < timedelta(hours=CACHE_TTL_HOURS):
            return _can_fetch_from_text(content, ua, url)
    db = None
    try:
        from app.database import get_session
        from app.schema import SourcePortal
        db = get_session()
        portal = db.query(SourcePortal).filter(SourcePortal.url == base).first()
        if portal and portal.robots_txt_last_fetched and portal.robots_txt_content:
            age = as_utc(utcnow()) - as_utc(portal.robots_txt_last_fetched)
            if timedelta(0) <= age < timedelta(hours=CACHE_TTL_HOURS):
                _MEM_CACHE[base] = (portal.robots_txt_content, as_utc(portal.robots_txt_last_fetched))
                return _can_fetch_from_text(portal.robots_txt_content, ua, url)
        content = _fetch_raw(robots_url)
        if content is None:
            return False  # Do not renew an old policy after an unsuccessful fetch.
        allowed = _can_fetch_from_text(content, ua, url)
        _MEM_CACHE[base] = (content, utcnow())
        if portal is None:
            portal = SourcePortal(url=base, name=urlsplit(base).netloc)
            db.add(portal)
        portal.robots_txt_url = robots_url
        portal.robots_txt_content = content
        portal.robots_txt_last_fetched = utcnow()
        portal.robots_txt_allowed = allowed
        db.commit()
        return allowed
    except Exception as exc:
        if db is not None:
            db.rollback()
        logger.warning("Robots cache unavailable (%s)", type(exc).__name__)
        # fallback usa mem cache se existir
        if base in _MEM_CACHE:
            return _can_fetch_from_text(_MEM_CACHE[base][0], ua, url)
        return _fetch_and_parse(robots_url, ua, url)
    finally:
        if db is not None:
            db.close()
