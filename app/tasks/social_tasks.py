import logging
from datetime import timedelta

from app.celery_app import celery_app
from app.contracts import utcnow
from app.database import get_session
from app.schema import NewsArticle, PublicationLog
from app.social.twitter import post_to_twitter

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.social_tasks.post_top_news_twitter")
def post_top_news_twitter():
    """
    Finds the most important article published in the last 12 hours that
    hasn't been posted to Twitter yet, and posts it.
    """
    db = get_session()
    try:
        twelve_hours_ago = utcnow() - timedelta(hours=12)

        # Subquery to find articles already posted to Twitter
        posted_subquery = (
            db.query(PublicationLog.article_id).filter(PublicationLog.action == "social_twitter").subquery()
        )

        # Find the top article (by final_score or importance_score) published recently
        top_article = (
            db.query(NewsArticle)
            .filter(
                NewsArticle.status == "published",
                NewsArticle.published_at >= twelve_hours_ago,
                NewsArticle.id.not_in(posted_subquery),
            )
            .order_by(NewsArticle.final_score.desc(), NewsArticle.published_at.desc())
            .first()
        )

        if not top_article:
            logger.info("Nenhuma notícia relevante encontrada para postar no Twitter nas últimas 12h.")
            return {"status": "skipped", "reason": "no_article"}

        # Post to Twitter
        success = post_to_twitter(title=top_article.title, category=top_article.category, slug=top_article.slug)

        if success:
            # Register in log
            log = PublicationLog(
                article_id=top_article.id,
                action="social_twitter",
                reporter_id=top_article.reporter_id,
                details="Postado automaticamente no Twitter (X) como Top News",
            )
            db.add(log)
            db.commit()
            return {"status": "success", "article_id": top_article.id}
        else:
            return {"status": "failed", "article_id": top_article.id}

    except Exception as e:
        logger.error(f"Erro na task post_top_news_twitter: {e}")
        db.rollback()
        raise
    finally:
        db.close()
