"""
Tarefas do Frontend — Atualiza Brasil
Exporta artigos publicados do banco para o frontend (articles.json).
"""

import os
import json
import re
import unicodedata
import logging
from datetime import datetime

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


def slugify(text):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:80].strip("-")


def _project_root() -> str:
    # arquivo em app/tasks/frontend_tasks.py -> subir duas pastas
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def export_frontend_articles_to_files(limit: int = 100) -> dict:
    """Lê artigos publicados do banco e grava os JSONs do frontend."""
    from app.database import get_session
    from app.schema import NewsArticle
    from sqlalchemy.orm import joinedload

    db = get_session()
    out = []
    try:
        arts = (
            db.query(NewsArticle)
            .options(joinedload(NewsArticle.reporter))
            .filter(NewsArticle.status == "published", NewsArticle.visibility == "public")
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
            .all()
        )

        seen = set()
        for a in arts:
            title = (a.title or "").strip()
            summary = (a.summary or "") or title
            if len(summary) > 300:
                summary = summary[:300].rsplit(" ", 1)[0] + "..."
            base_slug = slugify(title)
            slug = base_slug
            i = 2
            while slug in seen:
                slug = f"{base_slug}-{i}"
                i += 1
            seen.add(slug)

            sources = a.sources if isinstance(a.sources, list) else []
            urls = [s.get("url", "") if isinstance(s, dict) else str(s) for s in sources] if sources else []
            names = [s.get("name", "") if isinstance(s, dict) else "" for s in sources] if sources else []

            # foto de capa: usa a original quando existe; quando não, gera placeholder determinístico único por matéria
            # evita o problema de "muita foto repetida" (mesmo fallback para todos)
            cover = (a.image_url or "").strip()
            if not cover:
                # picsum com seed = hash da URL ou slug -> cada matéria tem capa distinta mas estável
                import hashlib
                first_url = ""
                if a.sources and isinstance(a.sources, list) and len(a.sources) > 0:
                    first = a.sources[0]
                    first_url = first.get("url", "") if isinstance(first, dict) else str(first)
                seed = hashlib.md5(((a.slug or slug) + first_url).encode()).hexdigest()[:8]
                cover = f"https://picsum.photos/seed/{seed}/800/450"

            out.append({
                "title": title,
                "slug": a.slug or slug,
                "summary": summary[:240],
                "content": a.content or "",
                "category": a.category or "general",
                "reporter_slug": a.reporter.slug if a.reporter else "enzo.bianchi",
                "reporter": a.reporter.display_name if a.reporter else None,
                "author": a.author,
                "url": urls[0] if urls else "",
                "image_url": cover,
                "sources": urls,
                "source_names": names,
                "source": names[0] if names else "",
                "tags": a.tags if isinstance(a.tags, list) else [a.category or "general"],
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "id": a.id,
            })
    finally:
        db.close()

    root = _project_root()
    data_dir = os.path.join(root, "frontend", "src", "data")
    public_dir = os.path.join(root, "frontend", "public")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    src_path = os.path.join(data_dir, "articles.json")
    pub_path = os.path.join(public_dir, "articles.json")

    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(pub_path, "w", encoding="utf-8") as f:
        json.dump({
            "articles": out,
            "generated_at": datetime.utcnow().isoformat(),
            "total": len(out),
        }, f, ensure_ascii=False, indent=2)

    return {"exported": len(out), "src": src_path, "public": pub_path}


@celery_app.task(
    name="app.tasks.frontend_tasks.export_frontend_articles",
    bind=True,
    max_retries=3,
    time_limit=120
)
def export_frontend_articles(self, limit: int = 100):
    """
    Exporta artigos publicados do banco para o frontend.
    Roda a cada 30 minutos (após o publish).
    """
    logger.info("[FRONTEND] Exportando artigos publicados para o frontend")
    try:
        result = export_frontend_articles_to_files(limit=limit)
        logger.info(f"[FRONTEND] Exportados {result['exported']} artigos")
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"[FRONTEND] Erro: {e}")
        raise self.retry(exc=e)
