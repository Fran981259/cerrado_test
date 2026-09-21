"""Protected routes for editorial review and manual publication."""

from datetime import datetime, timezone
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import and_, or_

from app.contracts import CATEGORIES, category_name, iso_utc
from app.database import get_session
from app.editorial import review_natural_writing
from app.publisher import ArticlePublisher
from app.schema import NewsArticle
from app.security import require_api_key

router = APIRouter()


class PublishArticleRequest(BaseModel):
    """Validated payload for a deliberate manual publication."""

    title: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    reporter_slug: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    summary: Optional[str] = Field(default=None, max_length=2_000)
    sources: Optional[List[dict[str, str]]] = Field(default=None, max_length=20)
    original_text: Optional[str] = None
    body: Optional[str] = None
    hash: Optional[str] = Field(default=None, max_length=64)
    tags: Optional[List[str]] = Field(default=None, max_length=30)
    image_url: Optional[str] = Field(default=None, max_length=500)
    region: Optional[Literal["ms"]] = None
    importance_score: Optional[float] = None
    engagement_score: Optional[float] = None
    priority_tier: Optional[Literal["TIER_1", "TIER_2", "TIER_3", "REJECT"]] = None


class UpdateReviewRequest(BaseModel):
    """Validated fields an editor may change in one review action."""

    content: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    importance_score: Optional[int] = Field(default=None, ge=0, le=100)
    engagement_score: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[Literal["draft", "classified", "review", "rewritten", "failed", "published"]] = None


@router.post("/api/publish")
def publish_article_endpoint(
    article: PublishArticleRequest, _auth=Depends(require_api_key), idempotency_key: str = Header(None)
):
    """Publish one manually approved article."""
    publisher = ArticlePublisher()
    try:
        return publisher.publish_article(article.model_dump(exclude_unset=True), idempotency_key=idempotency_key)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None
    except Exception as error:
        logger.error("Publicacao indisponivel (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Publicacao temporariamente indisponivel") from None
    finally:
        publisher.close()


@router.get("/api/editorial/review")
def list_articles_for_review(_auth=Depends(require_api_key)):
    """Return pending items and local public articles available for correction."""
    db = get_session()
    try:
        articles = (
            db.query(NewsArticle)
            .filter(
                or_(
                    NewsArticle.status.in_(["review", "classified", "draft"]),
                    and_(NewsArticle.status == "published", NewsArticle.visibility == "public", NewsArticle.region == "ms"),
                )
            )
            .order_by(NewsArticle.created_at.desc())
            .limit(2000)
            .all()
        )
        return {"articles": [_review_payload(article) for article in articles]}
    except Exception as error:
        logger.error("Falha ao listar matérias para curadoria (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        db.close()


@router.put("/api/editorial/review/{slug}")
def update_article_review(slug: str, data: UpdateReviewRequest, _auth=Depends(require_api_key)):
    """Persist a deliberate category, score or status decision."""
    db = get_session()
    try:
        article = db.query(NewsArticle).filter(NewsArticle.slug == slug).with_for_update().first()
        if not article:
            raise HTTPException(status_code=404, detail="Matéria não encontrada")
        _apply_review_changes(article, data.model_dump(exclude_unset=True), db)
        article.updated_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "success", "slug": slug}
    except HTTPException:
        raise
    except Exception as error:
        db.rollback()
        logger.error("Falha ao atualizar matéria (%s)", type(error).__name__)
        raise HTTPException(status_code=503, detail="Erro interno") from None
    finally:
        db.close()


def _review_payload(article: NewsArticle) -> dict:
    """Serialize only fields needed by the editorial dashboard."""
    return {
        "slug": article.slug, "title": article.title, "summary": article.summary, "content": article.content,
        "original_text": article.original_text, "writing_review": [finding.as_dict() for finding in review_natural_writing(article.content or "")],
        "category": article.category, "importance_score": article.importance_score,
        "engagement_score": article.engagement_score, "status": article.status,
        "published_at": iso_utc(article.published_at), "created_at": iso_utc(article.created_at),
    }


def _apply_review_changes(article: NewsArticle, changes: dict, db) -> None:
    """Apply validated review fields and use the publisher for a status promotion."""
    if "category" in changes:
        category = category_name(changes["category"])
        if category not in CATEGORIES:
            raise HTTPException(status_code=422, detail="Categoria invalida")
        article.category = category
    for field in ("content", "importance_score", "engagement_score"):
        if field in changes:
            setattr(article, field, changes[field])
    if changes.get("status") == "published" and article.status != "published":
        ArticlePublisher(db).publish_existing(article)
    elif "status" in changes:
        article.status = changes["status"]
