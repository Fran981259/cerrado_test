"""
Robots.txt checker — Portal Cerrado
Respeita robots.txt em runtime, com cache via SourcePortal (re-check diário).
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

USER_AGENT = os.getenv("USER_AGENT", "PortalCerrado/1.0")
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
            if (portal and portal.robots_txt_last_fetched
                    and getattr(portal, "robots_txt_content", None)):
                age = datetime.utcnow() - portal.robots_txt_last_fetched
                if age < timedelta(hours=CACHE_TTL_HOURS):
                    # Cache hit: reconstrói o parser do conteúdo e avalia A URL ATUAL
                    allowed = _can_fetch_from_text(portal.robots_txt_content, ua, url)
                    logger.debug(f"[ROBOTS] cache hit {base} -> {allowed} p/ {url} (age {age})")
                    return bool(allowed)
            # Cache miss, expirado ou linha legada sem conteúdo: busca fresco
            content = _fetch_raw(robots_url)
            allowed = _can_fetch_from_text(content, ua, url) if content else True
            # Atualiza ou cria portal
            if not portal:
                portal = SourcePortal(url=base, name=urlparse(base).netloc, robots_txt_url=robots_url)
                db.add(portal)
            portal.robots_txt_url = robots_url
            portal.robots_txt_last_fetched = datetime.utcnow()
            portal.robots_txt_allowed = bool(allowed)
            if content:
                portal.robots_txt_content = content
            db.commit()
            logger.info(f"[ROBOTS] {base} robots.txt -> {allowed} p/ {url} (fetched {robots_url})")
            return bool(allowed)
        finally:
            db.close()
    except Exception as e:
        logger.debug(f"[ROBOTS] DB cache falhou, fallback para fetch direto: {e}")

    # Fallback sem DB: fetch direto
    return _fetch_and_parse(robots_url, ua, url)


def _fetch_raw(robots_url: str) -> Optional[str]:
    """Baixa o robots.txt bruto (None em falha)."""
    try:
        import socket
        import urllib.request
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(5)
            with urllib.request.urlopen(robots_url, timeout=5) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                return raw or None
        finally:
            socket.setdefaulttimeout(old_timeout)
    except Exception as e:
        logger.debug(f"[ROBOTS] falha ao baixar {robots_url}: {e}")
        return None


def _can_fetch_from_text(content: Optional[str], user_agent: str, target_url: str) -> bool:
    """Avalia can_fetch() a partir do texto cru do robots.txt."""
    if not content:
        return True
    try:
        rp = RobotFileParser()
        rp.set_url("")
        rp.parse(content.splitlines())
        return rp.can_fetch(user_agent, target_url)
    except Exception as e:
        logger.debug(f"[ROBOTS] falha ao parsear cache: {e} — permitindo por padrão")
        return True


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
