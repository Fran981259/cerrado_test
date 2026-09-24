"""Persistência de rascunhos coletados pelo pipeline editorial."""

import hashlib
import logging
import re
import unicodedata
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.contracts import as_utc, category_name, sources_list
from app.database import get_session
from app.local_news_policy import local_story_decision
from app.schema import ArticleIdentity, NewsArticle, Reporter

logger = logging.getLogger(__name__)


def _clean_plain_text(value: str) -> str:
    if not value:
        return ""
    try:
        from bs4 import BeautifulSoup

        value = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    except Exception:
        value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[\r\n\t]+", " ", value)
    return re.sub(r"\s{2,}", " ", value).strip()


def _url_hash(url: str) -> str:
    """Cria hash único a partir da URL de origem para deduplicação."""
    return hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:64]


def _parse_iso_datetime(value) -> Optional[object]:
    if not value or not isinstance(value, str):
        return None
    try:
        from dateutil import parser as date_parser

        parsed = date_parser.isoparse(value.strip())
        if parsed.tzinfo is None:
            return parsed
        normalized = as_utc(parsed)
        return normalized.replace(tzinfo=None) if normalized is not None else None
    except Exception:
        return _parse_simple_datetime(value)


def _parse_simple_datetime(value: str) -> Optional[object]:
    for date_format in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value.strip()[:19], date_format)
        except ValueError:
            continue
    return None


def _make_draft_slug(title: str, url_hash: str) -> str:
    """Gera slug único e estável a partir do título e do hash da fonte."""
    normalized = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode("ascii")
    slug_base = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")[:80] or "artigo"
    return f"{slug_base}-{url_hash[:6]}"


def persist_articles(articles: list, fetch_details: bool = True) -> dict:
    """Persiste artigos coletados como rascunhos e informa o resultado agregado."""
    db = get_session()
    counters = _empty_counters()
    try:
        fetcher = _build_fetcher(fetch_details)
        recent_titles = _recent_titles(db)
        for article_data in articles:
            _persist_one_article(db, article_data, fetcher, recent_titles, counters)
        db.commit()
        return counters
    except Exception as error:
        db.rollback()
        logger.error("[SCAN] erro no commit: %s", error)
        raise
    finally:
        db.close()


def _empty_counters() -> dict:
    return {"inserted": 0, "duplicates": 0, "errors": 0, "fetched": 0, "fetch_miss": 0}


def _build_fetcher(fetch_details: bool):
    if not fetch_details:
        return None
    from app.article_fetcher import ArticleFetcher

    return ArticleFetcher()


def _recent_titles(db) -> list[str]:
    try:
        records = (
            db.query(NewsArticle.title)
            .filter(NewsArticle.status.in_(["draft", "classified", "rewritten", "published"]))
            .order_by(NewsArticle.created_at.desc())
            .limit(200)
            .all()
        )
        return [record[0] for record in records if record[0]]
    except Exception:
        return []


def _persist_one_article(db, article_data: dict, fetcher, recent_titles: list[str], counters: dict) -> None:
    url = article_data.get("url", "")
    locality = local_story_decision(
        source_url=url,
        title=article_data.get("title", ""),
        summary=article_data.get("summary", ""),
        body=article_data.get("body", ""),
    )
    if locality == "reject":
        logger.info("[SCAN] fonte fora da política local ignorada: %s", url)
        return
    _persist_local_article(db, article_data, fetcher, recent_titles, counters, locality)


def _persist_local_article(db, article_data: dict, fetcher, recent_titles: list[str], counters: dict, locality: str) -> None:
    try:
        source_hash = _article_hash(article_data, counters)
        if not source_hash:
            return
        if _is_duplicate(db, article_data, source_hash, recent_titles):
            counters["duplicates"] += 1
            return
        identity = ArticleIdentity(key="source:" + source_hash)
        db.add(identity)
        db.flush()
        article = _build_article(db, article_data, fetcher, counters, locality, source_hash)
        if article is None:
            db.rollback()
            return
        db.add(article)
        db.flush()
        identity.article_id = article.id
        db.commit()
        counters["inserted"] += 1
    except IntegrityError:
        db.rollback()
        counters["duplicates"] += 1
    except Exception as error:
        db.rollback()
        counters["errors"] += 1
        logger.error("[SCAN] erro ao persistir artigo (%s)", type(error).__name__)


def _article_hash(article_data: dict, counters: dict) -> Optional[str]:
    url = article_data.get("url", "")
    if not url and not (article_data.get("needs_review") and article_data.get("identity_key")):
        counters["errors"] += 1
        return None
    return _url_hash(article_data.get("identity_key") or url)


def _is_duplicate(db, article_data: dict, source_hash: str, recent_titles: list[str]) -> bool:
    if db.query(NewsArticle).filter(NewsArticle.compliance_hash == source_hash).first():
        return True
    return _has_duplicate_title(article_data.get("title") or "", recent_titles)


def _has_duplicate_title(title: str, recent_titles: list[str]) -> bool:
    if not title:
        return False
    from app.filter import DuplicateDetector

    candidate = {"title": title[:500]}
    for existing_title in recent_titles[-50:]:
        if DuplicateDetector.are_duplicates(candidate, {"title": existing_title}, threshold=0.85):
            return True
        if DuplicateDetector.are_semantically_similar(candidate["title"], existing_title):
            logger.info("[SCAN] duplicata semântica detectada: %r e %r", candidate["title"], existing_title)
            return True
    return False


def _build_article(db, article_data: dict, fetcher, counters: dict, locality: str, source_hash: str):
    content = _article_content(article_data, fetcher, counters)
    if content is None or not _has_title_body_overlap(article_data.get("title") or "", content["body"]):
        counters["errors"] += 1
        return None
    category = category_name(article_data.get("category"))
    reporter = _find_or_create_reporter(db, category)
    title = _clean_plain_text(article_data.get("title_pt") or content["title"])[:500]
    lead = _clean_plain_text(article_data.get("summary_pt") or content["lead"])[:2000]
    now = datetime.now(timezone.utc)
    return NewsArticle(
        title=title, slug=_make_draft_slug(title, source_hash), summary=lead, content=content["body"], author=content["author"],
        image_url=content["image_url"], reporter_id=reporter.id, sources=sources_list([{"url": article_data.get("url", ""), "name": article_data.get("source", ""), "title": title}]),
        original_text=content["body"] or lead, compliance_hash=source_hash,
        status="review" if article_data.get("needs_review") or locality == "review" else "draft", category=category,
        region=article_data.get("region") or "ms", tags=[category], is_curiosity=bool(article_data.get("is_curiosity")),
        published_at=content["published_at"], created_at=now, updated_at=now,
    )


def _article_content(article_data: dict, fetcher, counters: dict):
    content = {
        "title": _clean_plain_text(article_data.get("title") or "")[:500],
        "lead": _clean_plain_text(article_data.get("summary") or "")[:2000],
        "body": article_data.get("body") or "", "published_at": None, "author": None, "image_url": None,
    }
    if not fetcher:
        return content
    detail = fetcher.fetch(article_data.get("url", ""), base_summary=article_data.get("summary", ""))
    if detail.get("status") != "success":
        counters["fetch_miss"] += 1
        return None if detail.get("status") == "blocked" else content
    counters["fetched"] += 1
    return _apply_fetch_detail(content, detail)


def _apply_fetch_detail(content: dict, detail: dict) -> dict:
    if detail.get("title"):
        content["title"] = _clean_plain_text(detail["title"])[:500]
    if detail.get("lead"):
        content["lead"] = _clean_plain_text(detail["lead"])[:2000]
    content["body"] = detail.get("content") or ""
    content["published_at"] = _parse_iso_datetime(detail.get("published_at"))
    content["author"] = (detail.get("author") or "")[:200]
    content["image_url"] = (detail.get("image_url") or "")[:500]
    return content


def _has_title_body_overlap(title: str, body: str) -> bool:
    title_words = set(re.findall(r"\b\w+\b", _clean_plain_text(title).lower()))
    body_words = set(re.findall(r"\b\w+\b", body.lower()))
    if len(title_words) < 3 or not body:
        return True
    overlap = len(title_words.intersection(body_words)) / len(title_words)
    if overlap >= 0.15:
        return True
    logger.warning("[SCAN] Frankenstein detectado na raiz")
    return False


def _find_or_create_reporter(db, category: str) -> Reporter:
    from app.rewriter import get_reporter_for_category, load_reporters_config

    profile = get_reporter_for_category(category) or next(iter(load_reporters_config().values()))
    reporter = db.query(Reporter).filter(Reporter.slug == profile.slug).first()
    if reporter:
        return reporter
    reporter = Reporter(
        slug=profile.slug, display_name=profile.display_name, role=profile.role, email=f"{profile.slug}@portalcerrado.com.br"
    )
    db.add(reporter)
    db.flush()
    return reporter
