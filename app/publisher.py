"""Transactional publication and bounded public article queries."""

import hashlib
import json
import logging
import re
import unicodedata

from sqlalchemy import case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.contracts import category_name, category_values, iso_utc, sources_list, utcnow
from app.database import get_session
from app.editorial import validate_publication
from app.ml_editorial import get_latest_trend_signals
from app.schema import ArticleIdentity, NewsArticle, PublicationLog, Reporter

logger = logging.getLogger(__name__)


class ArticlePublisher:
    def __init__(self, db_session=None):
        self._db_session = db_session

    @property
    def db(self):
        if self._db_session is None:
            self._db_session = get_session()
        return self._db_session

    def publish_article(self, article_data, idempotency_key=None):
        validate_publication(article_data)
        if not isinstance(article_data.get("reporter_slug"), str) or not article_data["reporter_slug"].strip():
            raise ValueError("reporter_slug obrigatorio")
        if len(article_data["reporter_slug"]) > 100:
            raise ValueError("reporter_slug excede 100 caracteres")
        payload = json.dumps(article_data, sort_keys=True, ensure_ascii=True)
        key = "publish:" + hashlib.sha256((idempotency_key or payload).encode()).hexdigest()
        # A unique ledger reservation serializes concurrent retries on PostgreSQL.
        for attempt in range(3):
            try:
                identity = self.db.get(ArticleIdentity, key)
                if identity and identity.article_id:
                    article = self.db.get(NewsArticle, identity.article_id)
                    if article:
                        return self._publication_result(article)
                if identity is None:
                    identity = ArticleIdentity(key=key)
                    self.db.add(identity)
                    self.db.flush()
                reporter = self._get_or_create_reporter(article_data["reporter_slug"])
                article = NewsArticle(
                    title=article_data["title"].strip(),
                    slug=self._generate_slug(article_data["title"]),
                    summary=article_data.get("summary") or "",
                    content=article_data["content"],
                    reporter_id=reporter.id,
                    sources=sources_list(article_data.get("sources")),
                    original_text=article_data.get("original_text") or article_data.get("body") or "",
                    compliance_hash=article_data.get("hash") or "",
                    category=category_name(article_data["category"]),
                    region=article_data.get("region") or "ms",
                    tags=article_data.get("tags") or [],
                    image_url=article_data.get("image_url"),
                    importance_score=int((article_data.get("importance_score") or 0) * 10),
                    engagement_score=int((article_data.get("engagement_score") or 0) * 10),
                    final_score=int((article_data.get("final_score") or 0) * 10),
                    priority_tier=article_data.get("priority_tier") or "TIER_2",
                    is_curiosity=bool(article_data.get("is_curiosity")),
                    status="rewritten",
                )
                self.db.add(article)
                self.db.flush()
                identity.article_id = article.id
                self.publish_existing(article)
                self.db.commit()
                return self._publication_result(article)
            except IntegrityError:
                self.db.rollback()
                if attempt == 2:
                    raise
            except Exception:
                self.db.rollback()
                raise

    def publish_existing(self, article):
        """Caller owns transaction and must lock existing rows before publication."""
        if article.status == "published":
            return
        validate_publication(
            {
                "title": article.title,
                "content": article.content,
                "summary": article.summary,
                "category": article.category,
                "sources": article.sources,
                "original_text": article.original_text,
                "priority_tier": article.priority_tier,
                "is_curiosity": article.is_curiosity,
                "region": article.region,
            }
        )
        article.slug = article.slug or self._generate_slug(article.title)
        article.category = category_name(article.category)
        article.sources = sources_list(article.sources)
        article.status = "published"
        article.visibility = "public"
        article.published_at = article.published_at or utcnow()
        article.updated_at = utcnow()
        self._log_publication(article, {})
        self.db.query(Reporter).filter(Reporter.id == article.reporter_id).update(
            {
                Reporter.articles_published: Reporter.articles_published + 1,
                Reporter.experience_points: Reporter.experience_points + 10,
            },
            synchronize_session=False,
        )

    @staticmethod
    def _publication_result(article):
        return {
            "success": True,
            "article_id": article.id,
            "slug": article.slug,
            "published_at": iso_utc(article.published_at),
        }

    def _get_or_create_reporter(self, slug):
        reporter = self.db.query(Reporter).filter(Reporter.slug == slug).first()
        if reporter is None:
            from app.rewriter import load_reporters_config

            profile = load_reporters_config().get(slug)
            reporter = Reporter(
                slug=slug,
                display_name=profile.display_name if profile else slug.replace(".", " ").title(),
                role=category_name(profile.role) if profile else "general",
            )
            self.db.add(reporter)
            self.db.flush()
        return reporter

    def _generate_slug(self, title):
        slug = unicodedata.normalize("NFKD", title or "").encode("ascii", "ignore").decode("ascii").lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        base = re.sub(r"\s+", "-", slug).strip("-")[:180].strip("-") or "artigo"
        candidate, counter = base, 1
        while self.db.query(NewsArticle.id).filter(NewsArticle.slug == candidate).first():
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def _log_publication(self, article, article_data):
        self.db.add(
            PublicationLog(
                article_id=article.id,
                action="published",
                reporter_id=article.reporter_id,
                details="Publicacao aprovada pelo gate editorial",
            )
        )

    def publish_batch(self, articles):
        results = []
        for article in articles:
            try:
                results.append(self.publish_article(article))
            except ValueError as exc:
                results.append({"success": False, "error": str(exc)})
            except Exception as exc:
                logger.error("Publicacao falhou (%s)", type(exc).__name__)
                results.append({"success": False, "error": "Falha interna de publicacao"})
        return results

    def _public_query(self, category=None, reporter_slug=None, region=None):
        # This is a local newsroom. Never let a caller reintroduce global inventory
        # through an omitted filter, pagination or a direct API parameter.
        query = self.db.query(NewsArticle).filter(
            NewsArticle.status == "published",
            NewsArticle.visibility == "public",
            NewsArticle.region == "ms",
        )
        if region and region != "ms":
            return query.filter(False)
        if category:
            query = query.filter(NewsArticle.category.in_(category_values(category)))
        if reporter_slug:
            query = query.join(NewsArticle.reporter).filter(Reporter.slug == reporter_slug)
        return query

    def get_published_articles(self, limit=20, offset=0, category=None, reporter_slug=None, sort_by="recent", region=None):
        query = self._public_query(category, reporter_slug, region).options(joinedload(NewsArticle.reporter))
        if sort_by == "trend":
            trends = get_latest_trend_signals(limit=8)
            weights = {}
            for index, trend in enumerate(trends):
                for value in category_values(trend.get("category") or trend.get("topic")):
                    weights[value] = max(weights.get(value, 0), len(trends) - index)
            if weights:
                query = query.order_by(case(weights, value=NewsArticle.category, else_=0).desc())
        articles = (
            query.order_by(NewsArticle.published_at.desc().nullslast(), NewsArticle.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._article_to_dict(a) for a in articles]

    def count_published_articles(self, category=None, reporter_slug=None, region=None):
        return self._public_query(category, reporter_slug, region).count()

    def _article_to_dict(self, article):
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "content": article.content,
            "category": category_name(article.category),
            "reporter": article.reporter.display_name if article.reporter else None,
            "reporter_slug": article.reporter.slug if article.reporter else None,
            "author": article.author,
            "image_url": article.image_url,
            "sources": sources_list(article.sources),
            "tags": article.tags,
            "published_at": iso_utc(article.published_at),
            "created_at": iso_utc(article.created_at),
            "updated_at": iso_utc(article.updated_at),
            "is_curiosity": article.is_curiosity,
            "region": article.region,
            "importance_score": article.importance_score,
            "engagement_score": article.engagement_score,
            "final_score": article.final_score,
            "priority_tier": article.priority_tier,
        }

    def close(self):
        if self._db_session is not None:
            self._db_session.close()
