"""Public monitoring and discovery routes."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from sqlalchemy import func

from app.contracts import iso_utc
from app.database import get_session
from app.schema import NewsArticle, Reporter

router = APIRouter()


@router.get("/api/operations/status")
def operations_status():
    """Return a read-only, local-publication freshness signal."""
    db = get_session()
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        latest = _latest_article(db)
        return {
            "status": "healthy" if _recent_count(db, now - timedelta(hours=2)) else "stale",
            "checked_at": iso_utc(now),
            "published_today": _recent_count(db, today_start),
            "published_last_two_hours": _recent_count(db, now - timedelta(hours=2)),
            "latest_published_at": iso_utc(latest.published_at) if latest else None,
            "latest_article": latest.title if latest else None,
        }
    except Exception as error:
        logger.error("Status operacional indisponível (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Status operacional indisponível") from None
    finally:
        db.close()


@router.get("/api/sitemap")
def sitemap_articles(after_id: int = Query(0, ge=0), through_id: int = Query(None, ge=0), limit: int = Query(1000, ge=1, le=1000)):
    """Return one stable page of public local sitemap records."""
    db = get_session()
    try:
        upper = through_id if through_id is not None else (db.query(func.max(NewsArticle.id)).scalar() or 0)
        rows = _local_public_query(db).filter(NewsArticle.id > after_id, NewsArticle.id <= upper, NewsArticle.slug.isnot(None)).order_by(NewsArticle.id).limit(limit).all()
        return {"through_id": upper, "articles": [{"id": row.id, "slug": row.slug, "updated_at": iso_utc(row.updated_at), "published_at": iso_utc(row.published_at)} for row in rows]}
    except Exception:
        raise HTTPException(status_code=503, detail="Sitemap temporariamente indisponivel") from None
    finally:
        db.close()


@router.get("/api/news-sitemap")
def recent_news_sitemap_articles(limit: int = Query(1000, ge=1, le=1000)):
    """Return recent public local articles with the fields required by a news sitemap."""
    db = get_session()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=2)
        rows = (
            _local_public_query(db)
            .filter(NewsArticle.published_at >= cutoff, NewsArticle.slug.isnot(None))
            .order_by(NewsArticle.published_at.desc(), NewsArticle.id.desc())
            .limit(limit)
            .all()
        )
        return {"articles": [_news_sitemap_record(row) for row in rows]}
    except Exception:
        raise HTTPException(status_code=503, detail="Sitemap de notícias temporariamente indisponível") from None
    finally:
        db.close()


@router.get("/api/reporters")
def list_reporters():
    """List active digital reporters."""
    db = get_session()
    try:
        reporters = db.query(Reporter).filter(Reporter.active).all()
        return {"reporters": [{"slug": reporter.slug, "name": reporter.display_name, "role": reporter.role, "articles_published": reporter.articles_published, "stage": reporter.personality_stage} for reporter in reporters]}
    except Exception as error:
        logger.error("Reporteres indisponiveis (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Reporteres temporariamente indisponiveis") from None
    finally:
        db.close()


def _local_public_query(db):
    """Build the shared query for public MS articles."""
    return db.query(NewsArticle).filter(NewsArticle.status == "published", NewsArticle.visibility == "public", NewsArticle.region == "ms")


def _recent_count(db, cutoff: datetime) -> int:
    """Count public local articles published since a UTC cutoff."""
    return _local_public_query(db).filter(NewsArticle.published_at >= cutoff).count()


def _latest_article(db):
    """Select the newest public local article."""
    return _local_public_query(db).order_by(NewsArticle.published_at.desc()).first()


def _news_sitemap_record(article):
    """Serialize one public article for the Next.js news sitemap route."""
    return {
        "slug": article.slug,
        "title": article.title,
        "published_at": iso_utc(article.published_at),
        "updated_at": iso_utc(article.updated_at),
    }
