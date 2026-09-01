"""Tests para similaridade check Lei 9.610/98 (item 5) e fallback rewriter (item 6)."""
import os
import pytest
from app.publisher import ArticlePublisher
from app.database import get_session
from app.schema import NewsArticle, Reporter
from datetime import datetime

def _get_pub():
    db = get_session()
    pub = ArticlePublisher(db)
    return pub, db

def test_similarity_blocks_high_overlap():
    pub, db = _get_pub()
    # Conteúdo muito similar ao original (>35%)
    original = "O governo de Mato Grosso do Sul anunciou investimento de 10 milhões em saúde para hospitais de Campo Grande."
    content = "O governo de Mato Grosso do Sul anunciou investimento de 10 milhões em saúde para hospitais de Campo Grande."  # idêntico
    article = {
        "title": "Governo anuncia investimento em saúde MS" + str(datetime.utcnow().timestamp()),
        "content": content,
        "original_text": original,
        "reporter_slug": "maya.santos",
        "category": "health",
        "tags": ["health"],
        "sources": [{"url": "https://example.com/a", "name": "Test"}],
    }
    with pytest.raises(ValueError, match="similar"):
        pub.publish_article(article)
    db.close()

def test_similarity_allows_paraphrase():
    pub, db = _get_pub()
    original = "O governo de Mato Grosso do Sul anunciou investimento de 10 milhões em saúde para hospitais de Campo Grande com foco em leitos de UTI."
    paraphrase = "Em Campo Grande, a gestão estadual destinou R$ 10 milhões para ampliar a rede hospitalar, com ênfase na criação de vagas em terapia intensiva, segundo apuração própria com base em dados oficiais e contextualização para MS."
    article = {
        "title": "Teste paráfrase válida " + str(datetime.utcnow().timestamp()),
        "content": paraphrase,
        "original_text": original,
        "reporter_slug": "maya.santos",
        "category": "health",
        "tags": ["health"],
        "sources": [{"url": "https://example.com/b", "name": "Test"}],
    }
    # Deve permitir (similaridade <35%)
    result = pub.publish_article(article)
    assert result["success"] is True
    # cleanup
    db.query(NewsArticle).filter(NewsArticle.id == result["article_id"]).delete()
    db.commit()
    db.close()

def test_similarity_ignores_curiosity():
    pub, db = _get_pub()
    original = "Texto original"
    article = {
        "title": "Curiosidade teste " + str(datetime.utcnow().timestamp()),
        "content": original,
        "original_text": original,
        "reporter_slug": "enzo.bianchi",
        "category": "technology",
        "tags": ["tech"],
        "is_curiosity": True,
        "sources": [{"url": "https://example.com/c", "name": "Test"}],
    }
    # Curiosidades não são bloqueadas por similaridade (original pode ser igual)
    result = pub.publish_article(article)
    assert result["success"] is True
    db.query(NewsArticle).filter(NewsArticle.id == result["article_id"]).delete()
    db.commit()
    db.close()

def test_rewriter_fallback_returns_empty_when_short():
    from app.rewriter import ArticleRewriter, load_reporters_config
    reporters = load_reporters_config()
    r = reporters["enzo.bianchi"]
    w = ArticleRewriter(r)
    # Sem body e sem summary suficiente -> deve retornar vazio para retry (não thin content)
    article = {"title": "Teste sem corpo", "summary": "", "url": "https://example.com/x", "body": ""}
    res = w.rewrite(article)
    assert res["content"] == ""  # abortou para retry

def test_rewriter_fallback_uses_body_when_long():
    from app.rewriter import ArticleRewriter, load_reporters_config
    reporters = load_reporters_config()
    r = reporters["enzo.bianchi"]
    w = ArticleRewriter(r)
    long_body = ("Paragrafo real apurado sobre tecnologia com dados e entrevistas. " * 40)
    article = {"title": "Teste com corpo longo para fallback", "summary": "Resumo curto", "url": "https://example.com/y", "body": long_body}
    res = w.rewrite(article)
    assert len(res["content"].split()) >= 200
    assert "Paragrafo real" in res["content"]
    # Não deve conter boilerplate genérico repetido
    assert "O tema se insere em um cenário mais amplo" not in res["content"]
