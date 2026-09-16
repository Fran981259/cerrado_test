"""
Reclassifica TODAS as notícias usando o classificador heurístico atualizado.
Normaliza categorias via contracts.category_name() para garantir nomes canônicos.
"""
from app.database import get_session
from app.schema import NewsArticle
from app.classifier import NewsClassifier
from app.contracts import category_name, CATEGORIES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reclassify_all():
    db = get_session()
    classifier = NewsClassifier()

    articles = db.query(NewsArticle).all()
    updated = 0
    fixed_invalid = 0

    for art in articles:
        text = ((art.title or "") + " " + (art.summary or "")).lower()
        new_cat = classifier.classify_category(text)

        raw_cat = art.category or "general"
        normalized = category_name(raw_cat)

        needs_update = False

        if art.category != new_cat:
            art.category = new_cat
            needs_update = True
            updated += 1
        elif normalized not in CATEGORIES:
            art.category = new_cat
            needs_update = True
            fixed_invalid += 1
            updated += 1

        if needs_update:
            logger.info(f"ID {art.id}: {raw_cat} -> {art.category} | {(art.title or '')[:60]}")

    db.commit()
    db.close()
    print(f"\nReclassificação concluída: {updated} artigos atualizados ({fixed_invalid} categorias inválidas corrigidas)")


if __name__ == "__main__":
    reclassify_all()
