"""
Robots.txt checker — Atualiza Brasil
Respeita robots.txt em runtime, com cache via SourcePortal (re-check diário).
"""
import os
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

USER_AGENT = os.getenv("USER_AGENT", "AtualizaBrasil/1.0")
RESPECT_ROBOTS = os.getenv("RESPECT_ROBOTS_TXT", "true").lower() not in ("0", "false", "no")
CACHE_TTL_HOURS = int(os.getenv("ROBOTS_TXT_CACHE_HOURS", "24"))


def _get_base(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def is_allowed(url: str, user_agent: str = None) -> bool:
    """Verifica se url é permitido por robots.txt. Usa cache DB se disponível."""
    if not RESPECT_ROBOTS:
        return True
    ua = user_agent or USER_AGENT
    base = _get_base(url)
    robots_url = urljoin(base + "/", "robots.txt")

    # Tenta cache DB
    try:
        from app.database import get_session
        from app.schema import SourcePortal
        db = get_session()
        try:
            portal = db.query(SourcePortal).filter(SourcePortal.url == base).first()
            if portal and portal.robots_txt_last_fetched and portal.robots_txt_allowed is not None:
                age = datetime.utcnow() - portal.robots_txt_last_fetched
                if age < timedelta(hours=CACHE_TTL_HOURS):
                    logger.debug(f"[ROBOTS] cache hit {base} -> {portal.robots_txt_allowed} (age {age})")
                    return bool(portal.robots_txt_allowed)
            # Cache miss ou expirado: busca robots.txt
            allowed = _fetch_and_parse(robots_url, ua, url)
            # Atualiza ou cria portal
            if not portal:
                portal = SourcePortal(url=base, name=urlparse(base).netloc, robots_txt_url=robots_url)
                db.add(portal)
            portal.robots_txt_url = robots_url
            portal.robots_txt_last_fetched = datetime.utcnow()
            portal.robots_txt_allowed = bool(allowed)
            db.commit()
            logger.info(f"[ROBOTS] {base} robots.txt -> {allowed} (fetched {robots_url})")
            return bool(allowed)
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"[ROBOTS] DB cache falhou, fallback para fetch direto: {e}")

    # Fallback sem DB: fetch direto
    return _fetch_and_parse(robots_url, ua, url)


def _fetch_and_parse(robots_url: str, user_agent: str, target_url: str) -> bool:
    try:
        rp = RobotFileParser()
        rp.set_url(robots_url)
        # timeout curto para não travar pipeline
        import socket
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(5)
            rp.read()
        finally:
            socket.setdefaulttimeout(old_timeout)
        return rp.can_fetch(user_agent, target_url)
    except Exception as e:
        logger.debug(f"[ROBOTS] falha ao ler {robots_url}: {e} — permitindo por padrão")
        return True
