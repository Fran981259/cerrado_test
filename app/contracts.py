"""Shared boundary contracts; existing timestamps in the database represent UTC."""
from datetime import datetime, timezone
from urllib.parse import urlsplit

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


def as_utc(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def iso_utc(value):
    return as_utc(value).isoformat() if value is not None else None


class UTCDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return as_utc(value).replace(tzinfo=None) if value is not None else None


ALIASES = {
    "technology": "tech", "tecnologia": "tech",
    "entertainment": "culture", "science_health": "health",
    "sports_global": "sports", "geopolitics": "politics",
    "cultura": "culture"
}
CATEGORIES = {"tech", "culture", "health", "science", "sports", "politics", "economy",
              "security", "agriculture", "education", "clima", "general"}


def category_name(value):
    value = (value or "general").lower().strip()
    return ALIASES.get(value, value) if value in CATEGORIES or value in ALIASES else "general"


def category_values(value):
    canonical = category_name(value)
    return [canonical] + [alias for alias, target in ALIASES.items() if target == canonical]


def sources_list(value):
    result = []
    seen = set()
    for source in value if isinstance(value, list) else []:
        source = {"url": source} if isinstance(source, str) else source
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            continue
        url = source["url"].strip()
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme in {"https", "http"} and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            valid = False
        if valid and url not in seen:
            seen.add(url)
            result.append({"url": url, "name": str(source.get("name") or ""), "title": str(source.get("title") or "")})
    return result
