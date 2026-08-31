"""
Tarefas de Classificação de Artigos
"""
from app.celery_app import celery_app
from app.classifier import classify_articles
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.classify_tasks.classify_pending_articles",
    bind=True,
    max_retries=3
)
def classify_pending_articles(self):
    """
    Classifica artigos em status 'draft' por importância e engajamento,
    gravando os scores no banco e marcando-os como 'classified'.
    Roda a cada 30 minutos.
    """
    try:
        from app.database import get_session
        from app.schema import NewsArticle
        from app.classifier import NewsClassifier
        from datetime import datetime

        logger.info("[CLASSIFY] Iniciando classificação de drafts")
        db = get_session()
        classifier = NewsClassifier()
        classified = 0
        try:
            articles = (
                db.query(NewsArticle)
                .filter(NewsArticle.status == "draft")
                .order_by(NewsArticle.created_at.asc())
                .limit(100)
                .all()
            )
            for art in articles:
                data = {
                    "title": art.title,
                    "summary": art.summary or "",
                    "category": art.category or "general",
                }
                enriched = classifier.classify(data)
                cls = enriched.get("classification", {})
                art.importance_score = int((cls.get("importance_score", 0) or 0) * 10)
                art.engagement_score = int((cls.get("engagement_score", 0) or 0) * 10)
                art.final_score = int((cls.get("final_score", 0) or 0) * 10)
                art.priority_tier = cls.get("priority_tier") or "TIER_2"
                art.status = "classified"
                art.updated_at = datetime.utcnow()
                classified += 1
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        logger.info(f"[CLASSIFY] Classificados: {classified} artigos")
        return {"status": "success", "classified": classified}
    except Exception as e:
        logger.error(f"[CLASSIFY] Erro: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.classify_tasks.classify_single_article",
    bind=True,
    max_retries=3
)
def classify_single_article(self, article: dict):
    """Classifica um único artigo."""
    try:
        from app.classifier import NewsClassifier
        classifier = NewsClassifier()
        classified = classifier.classify(article)
        return {"status": "success", "article": classified}
    except Exception as e:
        logger.error(f"[CELERY] Erro em classify_single_article: {e}")
        raise self.retry(exc=e)
