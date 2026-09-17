"""All publication paths use the same transactional editorial gate."""
import logging
from app.celery_app import celery_app
from app.contracts import utcnow
from app.database import get_session
from app.editorial import EditorialRejection
from app.publisher import ArticlePublisher
from app.schema import NewsArticle

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.publish_tasks.publish_ready_articles", bind=True, max_retries=3, time_limit=300)
def publish_ready_articles(self):
    db = get_session()
    published = rejected = 0
    try:
        articles = db.query(NewsArticle).filter(NewsArticle.status == "rewritten").order_by(
            NewsArticle.updated_at.asc(), NewsArticle.id.asc()).with_for_update(skip_locked=True).limit(100).all()
        publisher = ArticlePublisher(db)
        for article in articles:
            # Trava de Segurança Final (Failsafe)
            if not article.content or len(article.content.strip()) < 100:
                logger.error(f"[PUBLISH] Abortado: Texto muito curto ou vazio ({article.slug})")
                article.status = "failed"
                rejected += 1
                continue
                
            if article.content == article.original_text:
                logger.error(f"[PUBLISH] Abortado: Texto cru não processado pela IA ({article.slug})")
                article.status = "failed"
                rejected += 1
                continue
                
            try:
                publisher.publish_existing(article)
                published += 1
            except EditorialRejection:
                article.status = "review"
                article.updated_at = utcnow()
                rejected += 1
        db.commit()
        from app.ml_editorial import EditorialTrendAnalyzer
        EditorialTrendAnalyzer().refresh_trend_signals(session=db)
        return {"status": "success", "published": published, "review": rejected, "failed": 0}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.publish_tasks.publish_single_article", bind=True, max_retries=3, time_limit=60)
def publish_single_article(self, article):
    publisher = ArticlePublisher()
    try:
        return publisher.publish_article(article)
    except ValueError:
        raise
    except Exception as exc:
        logger.error("Publicacao falhou (%s)", type(exc).__name__)
        raise self.retry(exc=RuntimeError("Publicacao temporariamente indisponivel"), countdown=60)
    finally:
        publisher.close()
