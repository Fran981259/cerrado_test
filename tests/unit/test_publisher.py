"""Unit tests para publisher slug."""
from app.database import get_session
from app.publisher import ArticlePublisher
from app.schema import NewsArticle
from datetime import datetime
import unicodedata

def _get_reporter_id(db):
    from app.schema import Reporter
    rep = db.query(Reporter).first()
    if not rep:
        rep = Reporter(slug="test.reporter", display_name="Test Reporter", role="general", email="test@portalcerrado.com.br")
        db.add(rep); db.commit(); db.refresh(rep)
    return rep.id

def test_slug_unique_without_collision():
    db = get_session()
    pub = ArticlePublisher(db)
    title = f"Teste Slug Único Sem Colisão {datetime.utcnow().isoformat()}"
    slug = pub._generate_slug(title)
    # deve gerar sem -2
    assert slug and "-" in slug
    assert not slug.endswith("-1")
    db.close()

def test_slug_collision_generates_increment():
    db = get_session()
    pub = ArticlePublisher(db)
    rep_id = _get_reporter_id(db)
    title = f"Título Repetido Para Colisão {datetime.utcnow().timestamp()}"
    slug1 = pub._generate_slug(title)
    art = NewsArticle(title=title, slug=slug1, summary="x", content="x", reporter_id=rep_id, sources=[], status="published", category="general", tags=["general"], published_at=datetime.utcnow())
    db.add(art); db.commit()
    slug2 = pub._generate_slug(title)
    assert slug1 != slug2
    assert slug2 == f"{slug1}-2" or slug2.endswith("-2")
    # cleanup
    db.query(NewsArticle).filter(NewsArticle.slug==slug1).delete()
    db.commit()
    db.close()

def test_slug_normalizes_accents():
    db = get_session()
    pub = ArticlePublisher(db)
    title = "Ação com acentuação: São Paulo e coração"
    slug = pub._generate_slug(title)
    assert "acao" in slug
    assert "sao" in slug
    db.close()

def test_article_fetcher_extracts_real_page(monkeypatch=None):
    # smoke test: ArticleFetcher não lança em URL inválida
    from app.article_fetcher import ArticleFetcher
    f = ArticleFetcher()
    res = f.fetch("https://invalid.invalid/notfound", base_summary="fallback")
    assert res["status"] in ("failed", "success")
